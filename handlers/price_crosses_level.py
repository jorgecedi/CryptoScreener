import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class PriceCrossesLevel:
    UP = 1
    DOWN = -1
    price = 0

    def __init__(self, level, cooldown=20):
        self.level = level
        self.enabled = True

    def handle(self, **kwargs):
        if not self.enabled:
            logger.debug("Handler not enabled")
            return False

        logger.debug(f"Handling signal with args: {kwargs}")
        self.price = kwargs["price"]

        if self.price > self.level:
            return True
        return False

    def get_success_message(self):
        return f"Actual quote price {self.price} crossed level {self.level}"

    def __str__(self):
        return f"PriceCrossesLevel: {self.level}"
