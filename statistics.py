import enum
import os
import subprocess
from typing import List

import numpy as np
from matplotlib import pyplot as plt
from scipy import interpolate

CACHE_CONTROL = "cache-control"
LAST_MODIFIED = "last-modified"
EXPIRES = "expires"
ETAG = "etag"
NO_STORE = "no-store"
NO_CACHE = "no-cache"
MAX_AGE = "max-age"


def get_website_list():
    return [
        # "https://bbc.com",
        # "https://cnn.com",
        "https://fararu.com",
        "https://khabaronline.ir",
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
    CACHE_CONTROL,
    LAST_MODIFIED,
    EXPIRES,
    ETAG,
)


class ObjectHeaderGroup(enum.Enum):
    WITHOUT_CACHE_HEADERS = 1
    SHOULD_NOT_CACHE = 2
    REVALIDATE_BEFORE_USING = 3
    SHOULD_CACHE = 4
    HEURISTIC_CACHE = 5
    UNKNOWN = 6


def is_without_cache_headers(headers: dict):
    for header in headers:
        if header in CACHE_HEADERS:
            return False
    return True


def is_should_not_cache(headers: dict):
    cache_control = headers.get(CACHE_CONTROL)
    if not cache_control:
        return False
    return cache_control.get(NO_STORE) is not None


def is_revalidate_cache(headers: dict):
    cache_control = headers.get(CACHE_CONTROL)
    if not cache_control:
        return False

    max_age = cache_control.get(MAX_AGE)
    no_cache = cache_control.get(NO_CACHE)
    no_store = cache_control.get(NO_STORE)

    return no_store is None and (no_cache is not None or (max_age and int(max_age) == 0))


def is_should_cache(headers: dict):
    cache_control = headers.get(CACHE_CONTROL)
    if not cache_control:
        return False

    max_age = cache_control.get(MAX_AGE)
    no_cache = cache_control.get(NO_CACHE)
    no_store = cache_control.get(NO_STORE)

    return no_cache is None and no_store is None and max_age and int(max_age) > 0


def is_heuristic_cache(headers: dict):
    cache_control = headers.get(CACHE_CONTROL)
    last_modified = headers.get(LAST_MODIFIED)

    return cache_control is None and last_modified is not None


def get_cache_control_values(val: str):
    output = {}
    cache_controls = val.replace(" ", "").split(",")
    for ctrl in cache_controls:
        if '=' in ctrl:
            key, value = ctrl.split("=")
            output[key] = value
        else:
            output[ctrl] = {}
    return output


def elicit_headers(headers: List[str]):
    output = {}
    for header in headers:
        if ":" not in header:
            continue
        key, value = header.split(": ")
        if key == CACHE_CONTROL:
            output[CACHE_CONTROL] = get_cache_control_values(value)
        elif key in (LAST_MODIFIED, EXPIRES, ETAG):
            output[key] = value
    return output


def parse_object_headers(headers: List[str]):
    headers = [header.lower() for header in headers]
    normalized_headers = elicit_headers(headers)
    if is_without_cache_headers(normalized_headers):
        return ObjectHeaderGroup.WITHOUT_CACHE_HEADERS
    elif is_should_not_cache(normalized_headers):
        return ObjectHeaderGroup.SHOULD_NOT_CACHE
    elif is_revalidate_cache(normalized_headers):
        return ObjectHeaderGroup.REVALIDATE_BEFORE_USING
    elif is_should_cache(normalized_headers):
        return ObjectHeaderGroup.SHOULD_CACHE
    elif is_heuristic_cache(normalized_headers):
        return ObjectHeaderGroup.HEURISTIC_CACHE

    return ObjectHeaderGroup.UNKNOWN


def get_max_age(headers: List[str]):
    headers = [header.lower() for header in headers]
    normalized_headers = elicit_headers(headers)
    return normalized_headers.get(CACHE_CONTROL, {}).get(MAX_AGE)

def smooth_output(xs, ys):
    bspline = interpolate.make_interp_spline(xs, ys)
    x_new = np.linspace(min(xs), max(xs), 100)
    y_new = bspline(x_new)
    return x_new, y_new

def plot_max_age_cdf(max_age_count: dict):
    pair_max_age_and_count = [(max_age, count) for max_age, count in max_age_count.items()]
    pair_max_age_and_count.sort(key=lambda item: item[0])
    sum_count = sum(pair[1] for pair in pair_max_age_and_count)

    pair_max_age_and_probability = [(max_age, count / sum_count) for max_age, count in pair_max_age_and_count]
    cumulative_probability = 0
    for i in range(len(pair_max_age_and_probability)):
        cumulative_probability += pair_max_age_and_probability[i][1]
        pair_max_age_and_probability[i] = (pair_max_age_and_probability[i][0], cumulative_probability)

    xs = list(map(lambda pair: pair[0], pair_max_age_and_probability))
    ys = list(map(lambda pair: pair[1], pair_max_age_and_probability))
    plt.xticks(ticks=xs, rotation=90)
    plt.plot(xs, ys)
    plt.show()


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
    max_age_count = {}
    for website in get_website_list():
        dir_name = website.replace("/", "_")
        # get_whole_page(dir_name, website)

        for name in os.listdir(dir_name):
            path = f"{dir_name}/{name}"
            if not os.path.isfile(path):
                continue
            with open(path, "rb", encoding=None) as f:
                headers = f.read().decode('unicode_escape', errors='ignore').split('\r\n\r\n')[0].split("\r\n")[1:]
            cache_type = parse_object_headers(headers)
            counts[cache_type] += 1
            if cache_type == ObjectHeaderGroup.SHOULD_CACHE:
                max_age = int(get_max_age(headers))
                max_age_count[max_age] = max_age_count.get(max_age, 0) + 1

    print(counts)
    plot_max_age_cdf(max_age_count)

# {31536000: 98, 900: 3, 10800: 2, 2592000: 173, 180: 1}
