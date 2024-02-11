import os
from typing import List

from exceptions import DownloadFailedException
from interfaces import DirectoryPathsResolver, Downloader, SiteList


class DownloaderDirectoryResolver(DirectoryPathsResolver):
    def __init__(self, downloader: Downloader, site_list: SiteList):
        self.downloader = downloader
        self.site_list = site_list

    def resolve(self) -> List[str]:
        sites = []
        for website in self.site_list.get_list():
            try:
                dir_name = self.downloader.download(website)
            except DownloadFailedException:
                continue
            sites.append(dir_name)
        return sites


class WalkerDirectoryResolver(DirectoryPathsResolver):
    def __init__(self, root_download_path: str):
        self.root_download_path = root_download_path

    def resolve(self) -> List[str]:
        return [f"{self.root_download_path}/{dir}" for dir in os.listdir(self.root_download_path)]
