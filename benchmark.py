import dataclasses
import datetime
from http.client import OK
from typing import List

import requests
from bs4 import BeautifulSoup

from storage import BrowserCache, ObjectResolver, NewCache
import time


def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('func:%r args:[%r, %r] took: %2.4f sec' % (f.__name__, args, kw, te - ts))
        return result

    return timed


def get_html_soup(headers=None):
    if not headers:
        headers = {}
    response = requests.get("http://localhost/index.html", headers=headers)
    if response.status_code != OK:
        raise Exception()
    return BeautifulSoup(response.text)


def get_new_html_soup():
    return get_html_soup(headers={
        'new-cache-enabled': 'true'
    })


@dataclasses.dataclass
class Link:
    key: str
    last_modified: datetime.datetime


def get_object_links(soup: BeautifulSoup):
    imgs = soup.find_all("img")
    return [
        Link(
            key=("http://localhost" if img.get("src").startswith("/") else "") + (img.get("src")),
            last_modified=datetime.datetime.strptime(
                img.get('last-modified', str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))),
                "%Y-%m-%d %H:%M:%S")
        )
        for img in imgs
    ]


@timeit
def resolve_links(resolver: ObjectResolver, links: List[Link]):
    for link in links:
        resolver.resolve(link.key, last_modified=link.last_modified)


if __name__ == '__main__':
    # browser cache
    html = get_html_soup()
    links = get_object_links(html)

    browser_cache = BrowserCache()
    new_cache = NewCache()

    # first resolving
    resolve_links(browser_cache, links)
    # second resolving
    resolve_links(browser_cache, links)

    # new cache
    html = get_new_html_soup()
    links = get_object_links(html)

    # first resolving
    resolve_links(new_cache, links)
    # second resolving
    resolve_links(new_cache, links)
