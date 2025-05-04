from shared.logging import logger
import subprocess

from shared.exceptions import DownloadFailedException
from shared.normalizer import get_website_name_from_url


class Wget:
    TIMEOUT = 2 * 60

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def get_output_directory_name(self, url):
        return f"{self.output_dir}/{get_website_name_from_url(url)}"

    def download(self, url: str) -> str:
        output_directory = self.get_output_directory_name(url)
        try:
            subprocess.run(
                [
                    "wget",
                    "--timeout=10",
                    "--tries=3",
                    "--quiet",
                    "-U"
                    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
                    "-H",
                    "-p",
                    "--save-headers",
                    "--convert-links",
                    "-nd",
                    "-P",
                    output_directory,
                    url,
                ], timeout=self.TIMEOUT)
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout in fetch {url}")
            raise DownloadFailedException

        return output_directory
