# !/usr/bin/env python

from typing import Union, Any
from time import sleep
from telethon import TelegramClient
from telethon.tl.types import Channel, Dialog, Message, User, Chat
from telethon import errors, events
from telethon.tl.functions.messages import GetAllStickersRequest

from tam.error import (
    UserIsAuthorizedException,
    LoginFailedError,
    DisconnectFailedError
)


class TelegramApiClient:

    MAX_RELOGIN_COUNT = 3
    DISCONNECT_TIMEOUT = 15

    def __init__(self, name: str, api_id: int, api_hash: str):
        self.name = name
        self._client = TelegramClient(name, api_id, api_hash)
        self.loop = self._client.loop
        self._relogin_count = 0
        self._current_user = None
        self.dialogs = {}
        self.sticker_sets = None

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
        print(f"Welcome, {self._current_user.username}!")

        for dialog in await self._client.get_dialogs():
            self.dialogs[dialog.entity.id] = dialog
        self.sticker_sets = await self.request(GetAllStickersRequest(0))
        return self._current_user

    async def send_message(self, dialog: Dialog, message: Any, reply_to: Message = None):
        try:
            if isinstance(message, str):
                message = message.rstrip('\t \n')
                if message:
                    await self._client.send_message(entity=dialog.entity, message=message, reply_to=reply_to)
            else:
                if message:
                    await self._client.send_file(entity=dialog.entity, file=message, reply_to=reply_to)
        except errors.PeerFloodError as e:
            print(f"{dialog.name}: PeerFloodError")
            raise e
        except errors.UsernameInvalidError as e:
            print(f"{dialog.name}: UsernameInvalidError")
            raise e
        except ValueError as e:
            print(f"{dialog.name}: ValueError")
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

    async def get_dialog(self, uid: Union[str, int], type: str = None) -> Union[Dialog, None]:
        if type:
            res_dialog = self._get_dialog_with_type(uid, type)
        else:
            res_dialog = self._get_dialog_without_type(uid)

        return res_dialog

    def _get_dialog_with_type(self, uid: Union[str, int], type: str) -> Union[Dialog, None]:
        res_dialog = None

        if type == 'entity':
            if isinstance(uid, int) and uid in self.dialogs.keys():
                res_dialog = self.dialogs[uid]
            elif isinstance(uid, str):
                for dialog in self.dialogs.values():
                    if (isinstance(dialog.entity, User) and uid == dialog.entity.username) or \
                        (isinstance(dialog.entity, Union[Chat, Channel]) and uid == dialog.entity.title):
                        res_dialog = dialog
                        break
        elif type == 'dialog':
            if isinstance(uid, int):
                for dialog in self.dialogs.values():
                    if uid == dialog.id:
                        res_dialog = dialog
                        break
            elif isinstance(uid, str):
                for dialog in self.dialogs.values():
                    if uid == dialog.name:
                        res_dialog = dialog
                        break

        return res_dialog

    def _get_dialog_without_type(self, uid: Union[str, int]) -> Union[Dialog, None]:
        res_dialog = None

        for dialog in self.dialogs.values():
            if isinstance(uid, int):
                if (uid == dialog.id) or \
                    (uid == dialog.entity.id):
                    res_dialog = dialog
                    break
            elif isinstance(uid, str):
                if (uid == dialog.name) or \
                    (isinstance(dialog.entity, User) and uid == dialog.entity.username) or \
                    ((isinstance(dialog.entity, Chat) or isinstance(dialog.entity, Channel)) and uid == dialog.entity.title):
                    res_dialog = dialog
                    break

        return res_dialog

    def add_messages_handler(self, handler: callable, *args, **kwargs):
        self._client.add_event_handler(
            handler,
            events.NewMessage(*args, **kwargs)
        )

    async def request(self, data):
        return await self._client(data)
