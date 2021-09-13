# !/usr/bin/env python

from .config import Config
from .telegram.client import TelegramApiClient
from .handler import ChatHandler


class TelegramAnsweringMachine:
    def __init__(self):
        self.client = TelegramApiClient(Config.username, Config.api_id, Config.api_hash)
        self.loop = self.client.loop
        self.handlers = {}

    def create_chat_handlers(self, aq_map: dict):
        for chat_uid, aq in aq_map.items():
            if chat_uid.isnumeric():
                chat_uid = int(chat_uid)
            chat = self.loop.run_until_complete(self.client.get_dialog(chat_uid))
            handler = ChatHandler(self.client, chat, aq)
            handler.join()
            self.handlers[chat_uid] = handler

    def run(self):
        self.loop.run_until_complete(self.client.start())
        self.create_chat_handlers(Config.aq_map)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.client.exit())
            if not self.loop.is_closed():
                self.loop.close()
