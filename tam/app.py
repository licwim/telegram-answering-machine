# !/usr/bin/env python

from time import sleep

from .chats import ChatsCollection
from .config import Config
from .telegram.client import TelegramApiClient
from .handlers import ChatsController


class TelegramAnsweringMachine:

    STOP_TIMEOUT = 60

    def __init__(self):
        self.client = TelegramApiClient(Config.username, Config.api_id, Config.api_hash)
        self.loop = self.client.loop
        self.chats_contoller = ChatsController(self.client)
        self.chats_collection = ChatsCollection(self.client)

    def _create_chat_handlers(self):
        for handler_type in self.chats_contoller.HANDLER_TYPES:
            self.chats_contoller.create_handler(handler_type, self.chats_collection)

    def run(self):
        self.loop.run_until_complete(self.client.connect())
        self.chats_collection.fill(Config.aq_map)
        self._create_chat_handlers()

        try:
            self.client.start()
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if self.loop.is_running():
            exit_task = self.loop.create_task(self.client.exit())
        else:
            exit_task = self.loop.run_until_complete(self.client.exit())

        timeout = 0
        while not (exit_task.done() or exit_task.cancelled()):
            sleep(1)
            timeout += 1
            if timeout > self.STOP_TIMEOUT:
                raise TimeoutError("Timeout for program completion exceeded")

        if self.loop.is_running():
            self.loop.stop()
        if not self.loop.is_closed():
            self.loop.close()
        self.input_listener.stop()
