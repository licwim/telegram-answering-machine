# !/usr/bin/env python


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
