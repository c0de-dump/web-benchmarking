import enum

CACHE_CONTROL = "cache-control"
LAST_MODIFIED = "last-modified"
EXPIRES = "expires"
ETAG = "etag"
NO_STORE = "no-store"
NO_CACHE = "no-cache"
MAX_AGE = "max-age"

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
    EXCEPTIONAL = 7
