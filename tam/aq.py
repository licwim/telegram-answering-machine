# !/usr/bin/env python

import re
from typing import Union
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import InputStickerSetID

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
