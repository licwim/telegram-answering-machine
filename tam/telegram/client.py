# !/usr/bin/env python

from telethon import TelegramClient
from telethon.tl.types import User
from tam.config import Config
from tam.error import (
    UserIsAuthorizedException,
    LoginFailedError
)


class BaseTelegramClient():

    MAX_RELOGIN_COUNT = 3

    def __init__(self, name):
        self.name = name
        self.client = TelegramClient(name, Config.API_ID, Config.API_HASH)
        self.client.connect()

    def sign_in(self, phone=None, code=None, password=None):
        if self.client.is_user_authorized():
            raise UserIsAuthorizedException()
        if phone:
            self.client.sign_in(phone=phone)
        if code:
            self.client.sign_in(code=code)
        if password:
            self.client.sign_in(password=password)
        if not self.client.is_user_authorized():
            if hasattr(self, 'relogin_count'):
                if self.relogin_count > self.MAX_RELOGIN_COUNT:
                    raise LoginFailedError()
                else:
                    self.relogin_count += 1
            else:
                self.relogin_count = 0
            self.sign_in(phone, code, password)

"""
    def start(self):
        self.get_info()
        self.client.start()

    def exit(self):
        try:
            if not self.save_user:
                self.client.log_out()
            self.client.disconnect()
            timeout = 15
            while timeout and self.client.is_connected():
                timeout -= 1
                sleep(1)
            if not timeout:
                msg_boxes().msgDisconnectError.exec()
            else:
                del self.client
        except ConnectionError:
            print("Connection error.")

    def get_info(self) -> User:
        self.user = self.client.get_me()
        return (self.user)

    def send_message(self, username, message):
        if not (username and message):
            return (1)
        message = message.rstrip('\t \n')
        if (len(message) > 20):
            return (1)
        try:
            user = self.client.get_entity(username)
            self.client.send_message(user, message)
        except errors.PeerFloodError:
            print (f"{username}: PeerFloodError")
            return (1)
        except errors.UsernameInvalidError:
            print (f"{username}: UsernameInvalidError")
            return (1)
        except ValueError:
            print (f"{username}: ValueError")
            return (1)
        return (0)

    def check_username(self, username):
        try:
            self.client.get_entity(username)
        except errors.UsernameInvalidError:
            return (1)
        except ValueError:
            return (2)
        return (0)
"""
