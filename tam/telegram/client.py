from typing import Union
from time import sleep
from telethon import TelegramClient
from telethon.tl.types import User, Chat
from telethon import errors, events

from tam.error import (
    EmptyChatError,
    EmptyMessageError,
    UserIsAuthorizedException,
    LoginFailedError,
    DisconnectFailedError
)
from .helpers import ChatHelper


class TelegramApiClient:

    MAX_RELOGIN_COUNT = 3
    DISCONNECT_TIMEOUT = 15

    def __init__(self, name: str, api_id: int, api_hash: str):
        self.name = name
        self._client = TelegramClient(name, api_id, api_hash)
        self.loop = self._client.loop
        self._relogin_count = 0
        self._current_user = None

    async def sign_in(
            self,
            phone: str = None,
            code: Union[int, str] = None,
            password: str = None
    ):
        if await self._client.is_user_authorized():
            raise UserIsAuthorizedException()

        if not phone:
            phone = input("Phone: ")
        await self._client.sign_in(phone=phone, code=code, password=password)

        if await self._client.is_user_authorized():
            return

        if not code:
            code = input("Code: ")
        await self._client.sign_in(code=code)

        if not password:
            password = input("Password: ")
        await self._client.sign_in(password=password)

        if not await self._client.is_user_authorized():
            if self._relogin_count > self.MAX_RELOGIN_COUNT:
                raise LoginFailedError()
            else:
                self._relogin_count += 1
            await self.sign_in(phone, code, password)

    async def start(self):
        await self._client.connect()
        await self.get_info()
        await self._client.start()
        print("Telegram Client is connected")

    async def exit(self, logout: bool = False):
        try:
            if logout:
                await self._client.log_out()
            await self._client.disconnect()
            for _ in range(self.MAX_RELOGIN_COUNT):
                if not self._client.is_connected():
                    break
                sleep(1)
            else:
                raise DisconnectFailedError()
        except ConnectionError:
            print("Connection error")

    async def get_info(self) -> User:
        self._current_user = await self._client.get_me()
        # print(self._current_user.username)
        return self._current_user

    async def send_message(self, chat: ChatHelper, message: str):
        message = message.rstrip('\t \n')
        if not chat:
            raise EmptyChatError
        if not message:
            raise EmptyMessageError

        try:
            return await self._client.send_message(chat.base, message)
        except errors.PeerFloodError as e:
            print(f"{chat.name}: PeerFloodError")
            raise e
        except errors.UsernameInvalidError as e:
            print(f"{chat.name}: UsernameInvalidError")
            raise e
        except ValueError as e:
            print(f"{chat.name}: ValueError")
            raise e

    async def check_username(self, username: str) -> bool:
        result = True
        try:
            await self._client.get_entity(username)
        except errors.UsernameInvalidError as e:
            print(f"{username}: UsernameInvalidError")
            result = False
        except ValueError as e:
            print(f"{username}: ValueError")
            result = False
        return result

    async def get_chat(self, chat_uid: Union[int, str]) -> Union[ChatHelper, None]:
        chat = await self._client.get_entity(chat_uid)

        if isinstance(chat, Chat) or isinstance(chat, User):
            return ChatHelper(chat)
        else:
            return None

    async def get_all_chats(self):
        dialogs = self._client.get_dialogs()
        for dialog in dialogs:
            print(dialog)

    def add_messages_handler(self, handler: callable, *args, **kwargs):
        self._client.add_event_handler(
            handler,
            events.NewMessage(*args, **kwargs)
        )
