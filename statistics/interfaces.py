import abc
from typing import List


class SiteList(metaclass=abc.ABCMeta):
    def get_list(self):
        raise NotImplementedError


class Downloader(metaclass=abc.ABCMeta):
    async def download(self, url: str) -> str:
        raise NotImplementedError


class HTTPObjectResolver(metaclass=abc.ABCMeta):
    def resolve(self) -> List[str]:
        raise NotImplementedError
