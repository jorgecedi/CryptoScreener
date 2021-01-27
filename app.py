import logging
import requests
import time
import os
import sys

from dotenv import load_dotenv
from notifier.telegram import TelegramNotifier
from webserver.server import app
from handlers.price_crosses_level import PriceCrossesLevel

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

LOOP_DELAY = int(os.getenv("LOOP_DELAY", 5))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", None)
TELEGRAM_GROUP_ID = os.getenv("TELEGRAM_GROUP_ID", None)


class Dispatcher:

    def __init__(self, handlers_with_config, notifiers, loop_delay):
        self.handlers_with_config = handlers_with_config
        self.loop_delay = loop_delay

    def publish_message(self, message):
        for notifier in notifiers:
            notifier.notify(message)
        logger.info(f"Success message: {message}")

    def start(self):
        self.running = True
        while self.running:
            logger.debug("Running loop")
            try:
                api_call = requests.get("https://api.bitso.com/v3/ticker/?book=btc_mxn")
                json_response = api_call.json()
                if json_response["success"] is True:
                    price = float(json_response["payload"]["ask"])
                    for handler_with_config in self.handlers_with_config:
                        try:
                            handler = handler_with_config[0]
                            config = handler_with_config[1]
                            config["price"] = price

                            if handler.handle(**config):
                                self.publish_message(handler.get_success_message())
                        except Exception as e:
                            logger.exception(e)
                else:
                    logger.error("Could not get price from broker")
            except Exception as e:
                logger.exception(e)
            time.sleep(self.loop_delay)


if __name__ == "__main__":
    # start loop, maybe I can change this for a real event loop
    try:
        handlers_with_config = [
            (PriceCrossesLevel(640000), {}),# Set a handler for when the prices goes over 650,000
        ]

        notifiers = [
            TelegramNotifier(TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_ID)
        ]

        dispatcher = Dispatcher(handlers_with_config, notifiers, LOOP_DELAY)
        dispatcher.start()
    except KeyboardInterrupt:
        logger.info("Stoping event loop")
    # app.run()
