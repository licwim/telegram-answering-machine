# !/usr/bin/env python

import re
from typing import Union
from telethon.sessions import abstract
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import Dialog, InputStickerSetID

from tam.error import ChatsCollectionError
from tam.telegram.client import TelegramApiClient


class Answer:

    def __init__(self, data: dict, client: TelegramApiClient, chat: 'Chat' = None):
        self.type = data['type']
        self._value = data['value']
        self._client = client
        self._chat = chat

        if 'delay' in data:
            self.delay = data['delay']
        else:
            self.delay = 0

    def before(self):
        pass

    async def get_message(self):
        return self._value

    def set_chat(self, chat: 'Chat'):
        self._chat = chat


class StickerAnswer(Answer):

    def before(self):
        super().before()
        self.sticker_set_short_name = self._value['sticker_set']
        self.offset = int(self._value['offset'])
        self.sticker = None

    async def get_message(self):
        if not self.sticker:
            for sticker_set in self._client.sticker_sets.sets:
                if self.sticker_set_short_name == sticker_set.short_name:
                    stickers = await self._client.request(GetStickerSetRequest(InputStickerSetID(sticker_set.id, sticker_set.access_hash)))
                    self.sticker = stickers.documents[self.offset - 1]
                    break

        return self.sticker


class TextAnswer(Answer):

    def before(self):
        super().before()
        self.text = self._value


class MentionAnswer(Answer):

    def before(self):
        super().before()
        self.mention = str(self._value).lstrip('@')

    async def get_message(self):
        members = await self._chat.get_members()
        members_usernames = [member.username for member in members]

        if self.mention == 'all':
            return ' '.join([f"@{username}" for username in members_usernames])

        if self.mention in members_usernames:
            return f"@{self.mention}"
        else:
            return None


class Question:

    def __init__(self, term: str):
        self.term = term.lower()

    def match(self, haystack: str) -> bool:
        if self.term == '*':
            return True
        if re.search(self.term.lower(), haystack.lower()):
            result = True
        else:
            result = False
        return result


class AQ:
    answer_types = {
        'text': TextAnswer,
        'sticker': StickerAnswer,
        'mention': MentionAnswer,
    }

    def __init__(self, client: TelegramApiClient, chat: 'Chat' = None, questions: list = None, answer: Answer = None, data: dict = None):
        self._client = client
        self._chat = chat

        if data:
            self.from_dict(data)
        else:
            self.questions = questions
            self.answer = answer

    def from_dict(self, data: dict):
        questions = []

        if isinstance(data['question'], str):
            data['question'] = [data['question']]
        for question in data['question']:
            questions.append(Question(question))
        answer = self.answer_prepare(data['answer'])
        if 'delay' in data and not answer.delay:
            answer.delay = data['delay']
        return self.__init__(self._client, self._chat, questions, answer)

    def answer_prepare(self, data: Union[dict, str]) -> Union[Answer, None]:
        answer = None

        if isinstance(data, str):
            if data.startswith('@'):
                data = {
                    'type': 'mention',
                    'value': data
                }
            else:
                data = {
                    'type': 'text',
                    'value': data
                }
        if data['type'] in self.answer_types:
            answer = self.answer_types[data['type']](data, self._client, self._chat)
            answer.before()

        return answer

    async def get_answer_message(self):
        return await self.answer.get_message()

    def set_chat(self, chat: 'Chat'):
        self._chat = chat


class AQCollection(list):

    def __init__(self, client: TelegramApiClient, chat: 'Chat' = None, aq_list: list = None):
        super().__init__()
        self._client = client
        self._chat = chat

        if aq_list:
            self.fill(aq_list)

    def fill(self, aq_list: list):
        for aq in aq_list:
            if isinstance(aq, dict):
                aq = AQ(self._client, self._chat, data=aq)
            if isinstance(aq, AQ):
                self.append(aq)

    def set_chat(self, chat: 'Chat'):
        self._chat = chat


class Chat:

    def __init__(self, client: TelegramApiClient, chat_uid: Union[str, int], dialog: Dialog, aq_collection: AQCollection = None):
        self._client = client
        self.chat_uid = chat_uid
        self.dialog = dialog
        self.aq_collection = aq_collection

    def __str__(self) -> str:
        return self.dialog.name

    def set_aq_collection(self, aq_collection: AQCollection):
        self.aq_collection = aq_collection

    async def get_members(self) -> list:
        return await self._client.get_dialog_members(self.dialog)

class ChatsCollection(list):

    def __init__(self, client: TelegramApiClient, data: dict = None):
        super().__init__()
        self._client = client

        if data:
            self.fill(data)

    def get_by_uid(self, uid) -> Union[Chat, None]:
        dialog = self._client.get_dialog(uid)
        if dialog:
            return self.get_by_dialog_id(dialog.id)
        return None

    def get_by_entity_id(self, id: int) -> Union[Chat, None]:
        dialog = self._client.get_dialog(id, 'entity')
        if dialog:
            return self.get_by_dialog_id(dialog.id)
        return None

    def get_by_dialog_id(self, id: int) -> Union[Chat, None]:
        for chat in self:
            if chat.dialog.id == id:
                return chat
        return None

    def fill(self, data: dict):
        errors = []

        for uid, aq_list in data.items():
            if uid.isnumeric():
                uid = int(uid)
            dialog = self._client.get_dialog(uid)
            if dialog:
                chat = Chat(self._client, uid, dialog)
            else:
                errors.append(ChatsCollectionError("Chat was not added", None, uid, dialog, aq_collection))
                continue
            aq_collection = AQCollection(self._client, chat, aq_list)
            chat.set_aq_collection(aq_collection)
            self.add(chat)

        return errors

    def add(self, chat: Chat):
        self.append(chat)

    def get_all_names(self) -> list:
        names = []
        for chat in self:
            names.append(chat.dialog.name)
        return names
