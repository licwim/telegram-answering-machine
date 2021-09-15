# !/usr/bin/env python

import asyncio

from .chats import ChatsCollection
from .telegram.client import TelegramApiClient


class Handler:

    def __init__(self, client: TelegramApiClient, chats_collection: ChatsCollection):
        self._client = client
        self._loop = client.loop
        self.chats_collection = chats_collection
        self.current_chat = None

    def listen(self):
        self._client.add_messages_handler(self.handle)
        print(f"Add handler for:\n\t" + "\n\t".join(self.chats_collection.get_all_names()) + "\n")

    async def handle(self, event):
        self.current_chat = self.chats_collection.get_by_dialog_id(event.chat_id)
        if self.current_chat and not event.message.out:
            return True
        else:
            return False


class ChatHandler(Handler):

    def __init__(self, client: TelegramApiClient, chats_collection: ChatsCollection):
        super().__init__(client, chats_collection)
        self.stickers = {}

    async def handle(self, event):
        try:
            if not await super().handle(event):
                return

            message = event.message
            dialog = self.current_chat.dialog

            print(f"New message from {dialog.name}: {message.text}\n")

            for aq in self.current_chat.aq_collection:
                for question in aq.questions:
                    if question.match(message.text):
                        await asyncio.sleep(aq.answer.delay)
                        answer = await aq.answer.get_message()
                        await self._client.send_message(dialog, answer, message)
                        print(f"Reply to {dialog.name}: {answer}\n")
                        break

        except AttributeError as ex:
            print(ex.args)


class ChatHandlerController:

    HANDLER_TYPES = [
        ChatHandler,
    ]

    def __init__(self, client: TelegramApiClient):
        self._handlers = {}
        self._client = client
        self._loop = client.loop

    def create_handler(self, type, chats_collection: ChatsCollection):
        if type in self.HANDLER_TYPES:
            handler = type(self._client, chats_collection)
            return self.add_handler(handler)
        return False

    def add_handler(self, handler: Handler):
        if handler.__class__ not in self._handlers.keys():
            self._handlers[handler.__class__] = handler
            handler.listen()
            return True
        return False

    def get_handler(self, key):
        if key:
            return self._handlers[key]
        return False
