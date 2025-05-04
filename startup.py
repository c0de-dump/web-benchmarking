import argparse
import os
import subprocess
from signal import SIGTERM
import self_hosting.download

from shared.normalizer import get_website_name_from_url
from shared.logging import logger
from load_testing.controller import LoadTesterController
from statistics.site_list_providers import AlexaScraperSiteList


def build_server():
    subprocess.run("go build -o newcaddy ./cmd/caddy", shell=True, cwd="/users/maxqian/CacheCatalyst/caddy")

def evaluate(website: str, content_path: str, caddyfile_path: str, repeats: int):
    website_name = f"/{get_website_name_from_url(website)}"
    output_name = f"http:__localhost:8080{website_name.replace('/', '_')}.json"

    logger.info(f"Expecting {website} serve from {website_name} and generate output {output_name}")
    if os.path.exists(output_name):
        logger.info(f"Website {website} already evaluated.")
        return

    try:
        self_hosting.download.self_host(website, content_path, caddyfile_path)
        logger.info(f"Website {website} complete downloading.")
    except Exception as e:
        logger.error(f"Failed to host for {website}: {e}")
        return

    server = subprocess.Popen(
        f"./newcaddy run --config {caddyfile_path}",
        shell=True,
        cwd="/users/maxqian/CacheCatalyst/caddy",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        preexec_fn=os.setsid,
    )

    LoadTesterController(
        [f"http://localhost:8080{website_name}"], "", repeats
    ).calculate()
    logger.info(f"Website {website} complete evaluation.")
    os.kill(os.getpgid(server.pid), SIGTERM)



def run_website_list(download_dir, repeats=3):
    # Make sure the content path is absolute
    if not os.path.isabs(download_dir):
        download_dir = os.path.abspath(download_dir)


    website_list = AlexaScraperSiteList().get_list()
    logger.info(f"Website list: {website_list}")
    for website in website_list:
        logger.info(f"Evaluating {website}")
        site_name = get_website_name_from_url(website)
        caddyfile_path = os.path.join(download_dir, f"Caddyfile.{site_name}")
        evaluate(website, download_dir, caddyfile_path, repeats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-sp",
        "--caddy-serve-path",
        help="Where caddy will serve files.",
        default="./wget_downloads",
    )

    parser.add_argument(
        "-r",
        "--repeats",
        help="request count to same page to calculate resposne time by averaging them.",
        default=3,
    )

    args = parser.parse_args()
    build_server()
    run_website_list(args.caddy_serve_path, args.repeats)
