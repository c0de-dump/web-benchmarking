import abc
from typing import List, Tuple

from http_object import HTTPObject


class SiteList(metaclass=abc.ABCMeta):
    def get_list(self):
        raise NotImplementedError


class Downloader(metaclass=abc.ABCMeta):
    async def download(self, url: str) -> str:
        raise NotImplementedError


class HTTPObjectResolver(metaclass=abc.ABCMeta):
    def resolve(self) -> Tuple[List[HTTPObject], int]:
        raise NotImplementedError
