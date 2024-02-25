import logging
import os
from typing import List, Tuple

from consts import ObjectHeaderGroup
from http_object import HTTPObject
from interfaces import HTTPObjectResolver
from utils import save_kv_file, plot_max_age_cdf

logger = logging.getLogger(__name__)


class Statistics:
    def __init__(self, http_object_resolver: HTTPObjectResolver):
        self.http_object_resolver = http_object_resolver

    def do(self):
        logger.info("Resolving directories...")
        http_objects, exception_count = self.http_object_resolver.resolve()
        logger.info("Directories resolved!")

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
                max_age_hours = int(max_age_seconds / 60 / 60)
                max_age_count[max_age_hours] = max_age_count.get(max_age_hours, 0) + 1
        logger.info("Statistics Done. Saving files...")
        save_kv_file(cache_type_counts, 'counts.csv')
        save_kv_file(max_age_count, 'max_age_count.csv')
        plot_max_age_cdf(max_age_count)
        logger.info("Bye Bye!")
