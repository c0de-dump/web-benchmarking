import enum
import os
import subprocess
from _hashlib import openssl_sha1
from typing import List


def get_website_list():
    return [
        # "https://bbc.com",
        # "https://cnn.com",
        "https://fararu.com"
    ]


def get_whole_page(output_dir, website: str):
    subprocess.run(
        [
            "wget",
            "-E",
            "-H",
            "-p",
            "-nd",
            "--save-headers",
            "-P",
            output_dir,
            website,
        ])


CACHE_HEADERS = (
    "cache-control",
    "last-modified",
    "expires",
    "etag",
)


class ObjectHeaderGroup(enum.Enum):
    WITHOUT_CACHE_HEADERS = 1
    SHOULD_NOT_CACHE = 2
    REVALIDATE_BEFORE_USING = 3
    SHOULD_CACHE = 4
    HEURISTIC_CACHE = 5
    UNKNOWN = 6


def is_without_cache_headers(headers: List[str]):
    for header in headers:
        if ": " not in header:
            continue
        key, value = header.split(": ", maxsplit=1)
        if key.lower() in CACHE_HEADERS:
            return False
    return True


def is_should_not_cache(headers: List[str]):
    for header in headers:
        key, value = header.split(": ", maxsplit=1)
        if key.lower() == 'cache-control':
            return 'no-store' in value.lower()
    return False


def is_revalidate_cache(headers: List[str]):
    for header in headers:
        key, value = header.split(": ", maxsplit=1)
        if key.lower() == 'cache-control':
            return 'no-store' not in value.lower() and \
                   ('no-cache' in value.lower() or 'max-age=0' in value.lower().replace(" ",
                                                                                        ""))  # TODO: Is it possible max-age=0123 ?
    return False


def is_should_cache(headers: List[str]):
    for header in headers:
        key, value = header.split(": ", maxsplit=1)
        if key.lower() == 'cache-control':
            return 'no-cache' not in value.lower() and \
                   'no-store' not in value.lower() and \
                   'max-age' in value.lower() and \
                   'max-age=0' not in value.lower().replace(" ", "")
    return False


def is_heuristic_cache(headers: List[str]):
    for header in headers:
        key, value = header.split(": ", maxsplit=1)
        if key.lower() == 'cache-control':
            return False

    for header in headers:
        key, value = header.split(": ", maxsplit=1)
        if key.lower() in ('cache-control', 'expires'):
            return True

    return False


def parse_object_headers(headers: List[str]):
    if is_without_cache_headers(headers):
        return ObjectHeaderGroup.WITHOUT_CACHE_HEADERS
    elif is_should_not_cache(headers):
        return ObjectHeaderGroup.SHOULD_NOT_CACHE
    elif is_revalidate_cache(headers):
        return ObjectHeaderGroup.REVALIDATE_BEFORE_USING
    elif is_should_cache(headers):
        return ObjectHeaderGroup.SHOULD_CACHE
    elif is_heuristic_cache(headers):
        return ObjectHeaderGroup.HEURISTIC_CACHE

    return ObjectHeaderGroup.UNKNOWN


def parse_file(path: str):
    with open(path, "rb", encoding=None) as f:
        return parse_object_headers(
            f.read().decode('unicode_escape', errors='ignore').split('\r\n\r\n')[0].split("\r\n")[1:]
        )


if __name__ == '__main__':
    # TODO: handle not 2xx responses
    counts = {
        ObjectHeaderGroup.WITHOUT_CACHE_HEADERS: 0,
        ObjectHeaderGroup.SHOULD_NOT_CACHE: 0,
        ObjectHeaderGroup.REVALIDATE_BEFORE_USING: 0,
        ObjectHeaderGroup.SHOULD_CACHE: 0,
        ObjectHeaderGroup.HEURISTIC_CACHE: 0,
        ObjectHeaderGroup.UNKNOWN: 0,
    }
    for website in get_website_list():
        dir_name = website.replace("/", "_")
        get_whole_page(dir_name, website)

        for name in os.listdir(dir_name):
            path = f"{dir_name}/{name}"
            if not os.path.isfile(path):
                continue
            counts[parse_file(path)] += 1
    print(counts)
