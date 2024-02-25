import asyncio
import os
from typing import List, Tuple

from exceptions import DownloadFailedException
from interfaces import HTTPObjectResolver, Downloader, SiteList
from http_object import HTTPObject
from utils import get_http_objects_from_paths


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
