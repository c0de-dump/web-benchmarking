import argparse
import datetime
import logging
import os.path

from site_list_providers import AlexaScraperSiteList, StaticWebsiteList
from object_resolver import WalkerDirectoryResolver, DownloaderObjectResolver, FirefoxSeleniumObjectResolver
from downlaoder.wget import Wget, AsyncWget
from interfaces import SiteList
from stats import Statistics

website_list_providers = {
    "alexa": AlexaScraperSiteList,
    "static": StaticWebsiteList,
}

logging.basicConfig(filename='stats.log', filemode='w', level=logging.INFO)


def get_async_downloader_resolver(path: str, website_list_provider: SiteList):
    return DownloaderObjectResolver(AsyncWget(path), website_list_provider)


def get_downloader_resolver(path: str, website_list_provider: SiteList):
    return DownloaderObjectResolver(Wget(path), website_list_provider)


def get_walker_resolver(path: str):
    return WalkerDirectoryResolver(path)


def get_path(args):
    path = args.path
    if not args.path:
        path = "./downloads"
    if not os.path.exists(path):
        os.mkdir(path)
    return path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("resolver", help=f"Provide resolver.",
                        choices=("walker", "downloader", "adownloader", "browser"))
    parser.add_argument("-p", "--path", help="Root path to store and read site objects in (a)downloader mode.")
    parser.add_argument("-wl", "--website-lister",
                        help="Should provider when resolver set to downloader."
                             "default is 'alexa' website list provider.", default="alexa")

    args = parser.parse_args()

    if args.resolver in ("downloader", "adownloader"):
        provider_class = website_list_providers[args.website_lister]
        if args.resolver == "downloader":
            resolver = get_downloader_resolver(get_path(args), provider_class())
        elif args.resolver == "adownloader":
            resolver = get_async_downloader_resolver(get_path(args), provider_class())
        else:
            raise Exception("Unhandled exception in finding proper downloader occurred.")

    elif args.resolver == "walker":
        resolver = get_walker_resolver(get_path(args))

    elif args.resolver == "browser":
        provider_class = website_list_providers[args.website_lister]
        resolver = FirefoxSeleniumObjectResolver(provider_class())
    else:
        raise Exception("Unhandled exception in finding resolver occurred.")

    statistics = Statistics(resolver)
    statistics.do()


if __name__ == "__main__":
    main()
