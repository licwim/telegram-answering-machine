# !/usr/bin/env python

from .telegram.client import TelegramApiClient
from .telegram.helpers import ChatHelper


class ChatHandler:

    def __init__(self, client: TelegramApiClient, chat: ChatHelper, answer: str):
        self.chat = chat
        self.answer = answer
        self._client = client

    def join(self):
        self._client.add_messages_handler(self.handle)
        print(f"Handler for {self.chat.name} is added")

    async def handle(self, event):
        try:
            if event.chat_id != self.chat.id or event.message.out:
                return

            if event.chat:
                chat = ChatHelper(event.chat)
            else:
                chat = await self._client.get_chat(event.chat_id)

            message = event.message

            print(f"New message from {self.chat.name}: {message.text}")
            self._client.loop.create_task(self._client.send_message(chat, self.answer))
        except AttributeError as ex:
            print(ex.args)
