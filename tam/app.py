# !/usr/bin/env python

from .chats import ChatsCollection
from .config import Config
from .telegram.client import TelegramApiClient
from .handlers import ChatHandlerController


class TelegramAnsweringMachine:
    def __init__(self):
        self.client = TelegramApiClient(Config.username, Config.api_id, Config.api_hash)
        self.loop = self.client.loop
        self.handler_contoller = ChatHandlerController(self.client)
        self.chats_collection = ChatsCollection(self.client)

    def create_chat_handlers(self):
        for handler_type in self.handler_contoller.HANDLER_TYPES:
            self.handler_contoller.create_handler(handler_type, self.chats_collection)

    def run(self):
        self.loop.run_until_complete(self.client.connect())
        self.chats_collection.fill(Config.aq_map)
        self.create_chat_handlers()
        try:
            self.client.start()
        except KeyboardInterrupt:
            self.loop.run_until_complete(self.client.exit())
            if not self.loop.is_closed():
                self.loop.close()
