# !/usr/bin/env python

import asyncio
from telethon.tl.types import Dialog

from .aq import AQ
from .telegram.client import TelegramApiClient


class ChatHandler:

    def __init__(self, client: TelegramApiClient, dialog: Dialog, aq_list: list):
        self.dialog = dialog
        self.aq_list = aq_list
        self._client = client
        self.stickers = {}

    def join(self):
        self._client.add_messages_handler(self.handle)
        print(f"Handler for {self.dialog.name} is added")

    async def handle(self, event):
        try:
            if event.chat_id != self.dialog.entity.id or event.message.out:
                return

            dialog = await self._client.get_dialog(event.chat_id, 'entity')
            message = event.message

            print(f"New message from {self.dialog.name}: {message.text}")

            for aq in self.aq_list:
                aq = AQ(self._client, data=aq)

                for question in aq.questions:
                    if question.match(message.text):
                        await asyncio.sleep(aq.answer.delay)
                        answer = await aq.answer.get_message()
                        await self._client.send_message(dialog, answer, message)
                        print(f"Reply to {self.dialog.name}: {answer}")
                        break

        except AttributeError as ex:
            print(ex.args)
