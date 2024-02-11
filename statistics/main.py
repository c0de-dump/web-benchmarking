import argparse
import logging
import os.path

from site_list_providers import AlexaScraperSiteList, StaticWebsiteList
from directory_resolver import WalkerDirectoryResolver, DownloaderDirectoryResolver
from downloader import Wget
from interfaces import SiteList
from stats import Statistics

website_list_providers = {
    "alexa": AlexaScraperSiteList,
    "static": StaticWebsiteList,
}

logging.basicConfig(filename='stats.log', filemode='w', level=logging.ERROR)


def get_downloader_resolver(path: str, website_list_provider: SiteList):
    return DownloaderDirectoryResolver(Wget(path), website_list_provider)


def get_walker_resolver(path: str):
    return WalkerDirectoryResolver(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("resolver", help=f"Provide resolver.",
                        choices=("walker", "downloader"))
    parser.add_argument("-p", "--path", help="Root path to store and read site objects.")
    parser.add_argument("-wl", "--website-lister",
                        help="Should provider when resolver set to downloader."
                             "default is 'alexa' website list provider.", default="alexa")

    args = parser.parse_args()

    path = args.path
    if not args.path:
        path = "./downloads"
    if not os.path.exists(path):
        os.mkdir(path)

    if args.resolver == "downloader":
        provider_class = website_list_providers[args.website_lister]
        resolver = get_downloader_resolver(path, provider_class())
    elif args.resolver == "walker":
        resolver = get_walker_resolver(path)
    else:
        raise Exception("Unhandled exception in finding resolver occurred.")

    statistics = Statistics(resolver)
    statistics.do()


if __name__ == "__main__":
    main()
