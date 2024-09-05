import re


def get_website_name_from_url(url):
    match = re.search(
        "^((http|https)://)?(www\\.)?(?P<website_name>[a-zA-Z0-9_-]+(\\.[a-zA-Z0-9_-]+)*)\\.[a-zA-Z0-9_-]+/?$", url)
    website_name = match.group("website_name")

    return website_name
