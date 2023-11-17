import dataclasses
import datetime
from http.client import NOT_MODIFIED, OK

import requests

from abc import ABC, abstractmethod


@dataclasses.dataclass
class File:
    key: str
    last_modified: datetime.datetime


class ObjectResolver(ABC):
    @abstractmethod
    def resolve(self, key: str, **kwargs):
        raise NotImplementedError


class BrowserCache(ObjectResolver):
    def __init__(self):
        self.etag_storage = {}

    def resolve(self, key: str, **kwargs):
        etag = self.etag_storage.get(key, '')
        response = requests.get(key, headers={
            'If-None-Match': etag,
        })
        if response.status_code not in (NOT_MODIFIED, OK):
            raise Exception()
        etag: str = response.headers.get('etag')
        if etag:
            self.etag_storage[key] = etag


class NewCache(ObjectResolver):
    def __init__(self):
        self.storage = dict()

    def resolve(self, key: str, **kwargs):
        file: File = self.storage.get(key)
        object_last_modified = kwargs.get('last_modified')
        if file and file.last_modified >= object_last_modified:
            return
        response = requests.get(key)
        if response.status_code not in (OK,):
            raise Exception()
        self.storage[key] = File(
            key=key,
            last_modified=datetime.datetime.strptime(response.headers.get("Last-Modified"),
                                                     "%a, %d %b %Y %H:%M:%S GMT"),
        )
