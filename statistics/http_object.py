from typing import List

from consts import CACHE_CONTROL, LAST_MODIFIED, EXPIRES, ETAG, CACHE_HEADERS, NO_STORE, MAX_AGE, NO_CACHE, \
    ObjectHeaderGroup


class HTTPObject:
    def __init__(self, headers: List[str]):
        self.headers_dict = self._elicit_headers(headers)
        self.type = self._get_type()

    @classmethod
    def _elicit_headers(cls, headers: List[str]):
        output = {}
        for header in headers:
            header = header.lower()
            if ":" not in header:
                continue
            key, value = header.split(": ", maxsplit=1)
            if key == CACHE_CONTROL:
                output[CACHE_CONTROL] = cls._get_cache_control_values(value)
            elif key in (LAST_MODIFIED, EXPIRES, ETAG):
                output[key] = value
        return output

    @classmethod
    def _get_cache_control_values(cls, val: str):
        output = {}
        if ";" in val:
            val = val.replace(";", ",")
        if "," in val:
            cache_controls = val.replace(" ", "").split(",")
        else:
            cache_controls = val.split(" ")
        for ctrl in cache_controls:
            if '=' in ctrl:
                key, value = ctrl.split("=")
                output[key] = value
            else:
                output[ctrl] = {}
        return output

    def get_max_age(self):
        return int(self.headers_dict.get(CACHE_CONTROL).get(MAX_AGE))

    def is_without_cache_headers(self):
        for header in self.headers_dict:
            if header in CACHE_HEADERS:
                return False
        return True

    def is_should_not_cache(self):
        cache_control = self.headers_dict.get(CACHE_CONTROL)
        if not cache_control:
            return False
        return cache_control.get(NO_STORE) is not None

    def is_revalidate_cache(self):
        cache_control = self.headers_dict.get(CACHE_CONTROL)
        if not cache_control:
            return False

        max_age = cache_control.get(MAX_AGE)
        no_cache = cache_control.get(NO_CACHE)
        no_store = cache_control.get(NO_STORE)

        return no_store is None and (no_cache is not None or (max_age and int(max_age) == 0))

    def is_should_cache(self):
        cache_control = self.headers_dict.get(CACHE_CONTROL)
        if not cache_control:
            return False

        max_age = cache_control.get(MAX_AGE)
        no_cache = cache_control.get(NO_CACHE)
        no_store = cache_control.get(NO_STORE)

        return no_cache is None and no_store is None and max_age and int(max_age) > 0

    def is_heuristic_cache(self):
        cache_control = self.headers_dict.get(CACHE_CONTROL)
        last_modified = self.headers_dict.get(LAST_MODIFIED)

        return cache_control is None and last_modified is not None

    def _get_type(self):
        if self.is_without_cache_headers():
            return ObjectHeaderGroup.WITHOUT_CACHE_HEADERS
        elif self.is_should_not_cache():
            return ObjectHeaderGroup.SHOULD_NOT_CACHE
        elif self.is_revalidate_cache():
            return ObjectHeaderGroup.REVALIDATE_BEFORE_USING
        elif self.is_should_cache():
            return ObjectHeaderGroup.SHOULD_CACHE
        elif self.is_heuristic_cache():
            return ObjectHeaderGroup.HEURISTIC_CACHE
        return ObjectHeaderGroup.UNKNOWN

    def __str__(self):
        return str(self.headers_dict)
