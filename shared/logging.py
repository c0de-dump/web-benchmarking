import logging

logging.basicConfig(
    format="%(asctime)s-%(name)s|%(levelname)s [%(filename)s:%(lineno)d] %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
