# !/usr/bin/env python
import os


class Config:
    CONFIG_FILE = os.getenv('TAM_CONFIG_FILE')

    username = str()
    api_id = int()
    api_hash = str()
    aq_map = dict()

    REQUIRED_ATTRIBUTES = [
        'username',
        'api_id',
        'api_hash',
        'aq_map',
    ]
