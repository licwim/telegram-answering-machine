# !/usr/bin/env python

from typing import Union


class BaseTamException(Exception):

    def __init__(self, message):
        super().__init__()
        self.message = message


class UserIsAuthorizedException(BaseTamException):

    def __init__(self):
        super().__init__("User is already authorized")


class LoginFailedError(BaseTamException):

    def __init__(self):
        super().__init__("Login isn't success")


class DisconnectFailedError(BaseTamException):

    def __init__(self):
        super().__init__("Disconnect error")


class EmptyDialogError(BaseTamException):

    def __init__(self):
        super().__init__("Empty dialog")


class EmptyMessageError(BaseTamException):

    def __init__(self):
        super().__init__("Empty message")


class ChatsCollectionError(BaseTamException):

    def __init__(self, message: str, chat: 'Chat' = None, chat_uid: Union[str, int] = None,\
                                dialog: 'Dialog' = None, aq_collection: 'AQCollection' = None):
        if not message:
            message = "Unknow error in ChatsCollection"
        self.chat = chat
        self.chat_uid = chat_uid
        self.dialog = dialog
        self.aq_collection = aq_collection
        super().__init__(message)
