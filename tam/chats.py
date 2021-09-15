# !/usr/bin/env python

import re
from typing import Union
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import Dialog, InputStickerSetID

from tam.error import ChatsCollectionError
from tam.telegram.client import TelegramApiClient


class Answer:

    def __init__(self, data: dict, client: TelegramApiClient):
        self.type = data['type']
        self._client = client
        if 'delay' in data:
            self.delay = data['delay']
        else:
            self.delay = 0

    async def get_message(self):
        pass


class StickerAnswer(Answer):

    def __init__(self, data: dict, client: TelegramApiClient):
        super().__init__(data, client)
        self.sticker_set_short_name = data['sticker_set']
        self.offset = int(data['offset'])
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

    def __init__(self, data: dict, client: TelegramApiClient):
        super().__init__(data, client)
        self.text = data['text']

    async def get_message(self):
        return self.text


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
        'sticker': StickerAnswer
    }

    def __init__(self, client: TelegramApiClient, questions: list = None, answer: Answer = None, data: dict = None):
        self._client = client
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
        return self.__init__(self._client, questions, answer)

    def answer_prepare(self, data: Union[dict, str]) -> Union[Answer, None]:
        answer = None

        if isinstance(data, str):
            data = {
                'type': 'text',
                'text': data
            }
        if data['type'] in self.answer_types:
            answer = self.answer_types[data['type']](data, self._client)

        return answer


class AQCollection(list):

    def __init__(self, client: TelegramApiClient, aq_list: list):
        super().__init__()
        for aq in aq_list:
            if isinstance(aq, dict):
                aq = AQ(client, data=aq)
            if isinstance(aq, AQ):
                self.append(aq)


class Chat:

    def __init__(self, client: TelegramApiClient, chat_uid: Union[str, int], dialog: Dialog, aq_collection: AQCollection):
        self._client = client
        self.chat_uid = chat_uid
        self.dialog = dialog
        self.aq_collection = aq_collection

    def __str__(self) -> str:
        return self.dialog.name


class ChatsCollection(list):

    def __init__(self, client: TelegramApiClient):
        super().__init__()
        self._client = client

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
            aq_collection = AQCollection(self._client, aq_list)

            if not self.add(uid, dialog, aq_collection):
                errors.append(ChatsCollectionError("Chat was not added", None, uid, dialog, aq_collection))

        return errors

    def add(self, uid, dialog: Dialog, aq_collection: AQCollection) -> bool:
        if uid and dialog and aq_collection:
            self.append(Chat(self._client, uid, dialog, aq_collection))
            return True
        return False

    def get_all_names(self) -> list:
        names = []
        for chat in self:
            names.append(chat.dialog.name)
        return names
