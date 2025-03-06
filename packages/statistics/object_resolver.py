import asyncio
import logging
import os
import time
from typing import List, Tuple

from shared.exceptions import DownloadFailedException
from interfaces import HTTPObjectResolver, Downloader, SiteList
from http_object import HTTPObject
from utils import get_http_objects_from_paths

from seleniumwire.webdriver import Firefox, FirefoxOptions
from selenium.webdriver import FirefoxService


class DownloaderObjectResolver(HTTPObjectResolver):
    def __init__(self, downloader: Downloader, site_list: SiteList, workers=2):
        self.downloader = downloader
        self.site_list = site_list
        self.workers = workers
        self.iter = self.get_list()

    def get_list(self):
        yield from self.site_list.get_list()

    async def _resolve(self, q: List):
        for website in self.iter:
            try:
                dir_name = await self.downloader.download(website)
            except DownloadFailedException:
                continue
            q.append(dir_name)

    async def _gather(self, q: List):
        tasks = (self._resolve(q) for _ in range(self.workers))
        await asyncio.gather(*tasks)

    def resolve(self) -> Tuple[List[HTTPObject], int]:
        q = []
        asyncio.run(self._gather(q))
        return get_http_objects_from_paths(q)


class WalkerDirectoryResolver(HTTPObjectResolver):
    def __init__(self, root_download_path: str):
        self.root_download_path = root_download_path

    def resolve(self) -> Tuple[List[HTTPObject], int]:
        return get_http_objects_from_paths(
            [f"{self.root_download_path}/{dir}" for dir in os.listdir(self.root_download_path)])


class FirefoxSeleniumObjectResolver(HTTPObjectResolver):
    def __init__(self, site_list: SiteList):
        self.site_list = site_list

    @classmethod
    def _get_driver(cls):
        options = FirefoxOptions()
        options.add_argument("--headless")

        service = FirefoxService()
        service.path = './geckodriver'
        service.log_path = '/dev/null'
        return Firefox(options=options, service=service)

    def resolve(self) -> Tuple[List[HTTPObject], int]:
        slogger = logging.getLogger('seleniumwire.handler')
        slogger.setLevel(logging.WARNING)
        slogger = logging.getLogger('seleniumwire.server')
        slogger.setLevel(logging.WARNING)

        exception_count = 0
        objects: List[HTTPObject] = []

        site_list = self.site_list.get_list()
        driver = self._get_driver()

        for i, site in enumerate(site_list):
            logger.info("%d/%d) requesting to %s", i+1, len(site_list), site)
            try:
                driver.get(site)
            except Exception as e:
                logger.error(f"fetching site {site} failed because %s", str(e))
                continue

            for request in driver.requests:
                if not request.response:
                    time.sleep(5)
                    break

            for request in driver.requests:
                if not request.response or not request.response.headers:
                    exception_count += 1
                    logger.warning(f"request for {request.host} has no response or header: %s", request)
                    continue

                try:
                    http_object = HTTPObject(str(request.response.headers).strip().split("\n"))
                    objects.append(http_object)
                except Exception as e:
                    exception_count += 1
                    logger.warning("exception occurred in eliciting object of site %s\n%s", request.host, str(e))
            del driver.requests

        driver.close()

        return objects, exception_count
