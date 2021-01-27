import logging
import os
import sys
import telegram

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class TelegramNotifier:

    def __init__(self, bot_token, group_id):
        self.bot = telegram.Bot(token=bot_token)
        self.group_id = group_id

    def notify(self, message):
        logger.info(f"Sending message to bot")
        self.bot.send_message(self.group_id, message, parse_mode=telegram.ParseMode.MARKDOWN)
