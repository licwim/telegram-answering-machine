# !/usr/bin/env python

from .config import Config
from .telegram.client import TelegramApiClient
from .handler import ChatHandler


class TelegramAnsweringMachine:
    def __init__(self):
        self.client = TelegramApiClient(Config.username, Config.api_id, Config.api_hash)
        self.loop = self.client.loop
        self.handlers = {}

    def create_chat_handlers(self, answers: dict):
        for chat_uid, answer in answers.items():
            chat = self.loop.run_until_complete(self.client.get_chat(chat_uid))
            handler = ChatHandler(self.client, chat, answer)
            handler.join()
            self.handlers[chat_uid] = handler

    def run(self):
        self.loop.run_until_complete(self.client.start())
        self.create_chat_handlers(Config.answers)
        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.client.exit())
            if not self.loop.is_closed():
                self.loop.close()
