# !/usr/bin/env python


class Config:
    CONFIG_FILE = 'config.json'

    username = str()
    api_id = int()
    api_hash = str()
    answers = dict()

    REQUIRED_ATTRIBUTES = [
        'username',
        'api_id',
        'api_hash',
        'answers',
    ]
