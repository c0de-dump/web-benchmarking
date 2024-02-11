import logging
import os
from typing import List, Tuple

from consts import ObjectHeaderGroup
from http_object import HTTPObject
from interfaces import DirectoryPathsResolver
from utils import save_kv_file, plot_max_age_cdf

logger = logging.getLogger(__name__)


class Statistics:
    def __init__(self, directory_resolver: DirectoryPathsResolver):
        self.directory_resolver = directory_resolver

    @classmethod
    def _get_all_http_objects(cls, to_parse_paths) -> Tuple[List[HTTPObject], int]:
        http_objects: List[HTTPObject] = []
        exception_count = 0
        for root_path in to_parse_paths:
            logger.info("Exporting http_objects of %s", root_path)
            for path in os.listdir(root_path):
                path = f"{root_path}/{path}"
                with open(path, "rb", encoding=None) as f:
                    headers = f.read().decode('unicode_escape', errors='ignore').split('\r\n\r\n')[0].split("\r\n")[1:]
                try:
                    http_object = HTTPObject(headers)
                except Exception as e:
                    logger.error("Failed to parse headers for file %s with error %s. with headers\n%s", path, str(e),
                                 headers)
                    exception_count += 1
                    continue
                http_objects.append(http_object)
        return http_objects, exception_count

    def do(self):
        logger.info("Resolving directories...")
        to_parse_paths = self.directory_resolver.resolve()
        logger.info("Directories resolved!")

        logger.info("Parsing and get http objects...")
        http_objects, exception_count = self._get_all_http_objects(to_parse_paths)
        logger.info("Http objects parsed!")

        cache_type_counts = {
            ObjectHeaderGroup.WITHOUT_CACHE_HEADERS: 0,
            ObjectHeaderGroup.SHOULD_NOT_CACHE: 0,
            ObjectHeaderGroup.REVALIDATE_BEFORE_USING: 0,
            ObjectHeaderGroup.SHOULD_CACHE: 0,
            ObjectHeaderGroup.HEURISTIC_CACHE: 0,
            ObjectHeaderGroup.UNKNOWN: 0,
            ObjectHeaderGroup.EXCEPTIONAL: exception_count,
        }
        max_age_count = {}
        logger.info("Doing some statistics...")
        for http_object in http_objects:
            cache_type_counts[http_object.type] += 1

            if http_object.is_should_cache():
                try:
                    max_age_seconds = int(http_object.get_max_age())
                except Exception:
                    logger.error("Unable to get max of http_object %s", str(http_object))
                    cache_type_counts[ObjectHeaderGroup.EXCEPTIONAL] += 1
                    continue
                max_age_hours = int(max_age_seconds / 60 / 60 / 24)
                max_age_count[max_age_hours] = max_age_count.get(max_age_hours, 0) + 1
        logger.info("Statistics Done. Saving files...")
        save_kv_file(cache_type_counts, 'counts.csv')
        save_kv_file(max_age_count, 'max_age_count.csv')
        plot_max_age_cdf(max_age_count)
        logger.info("Bye Bye!")
