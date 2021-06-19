# !/usr/bin/env python
# ================================================= #
#                                                   #
#    ───╔═╗──╔══╗╔══╗╔═╗╔═╗╔═╗╔══╗╔═╗─────╔═╗───    #
#    ───║ ║──╚╗╔╝║╔═╝║ ║║ ║║ ║╚╗╔╝║ ║─────║ ║───    #
#    ───║ ║───║║─║║──║ ║║ ║║ ║─║║─║ ╚═╗ ╔═╝ ║───    #
#    ───║ ║───║║─║║──║ ║║ ║║ ║─║║─║ ╔═╗ ╔═╗ ║───    #
#    ───║ ╚═╗╔╝╚╗║╚═╗║ ╚╝ ╚╝ ║╔╝╚╗║ ║ ╚═╝ ║ ║───    #
#    ───╚═══╝╚══╝╚══╝╚══╝ ╚══╝╚══╝╚═╝─────╚═╝───    #
#                                                   #
#   __init__.py                                     #
#       By: licwim                                  #
#                                                   #
#   Created: 13-06-2021 11:56:01 by licwim          #
#   Updated: 13-06-2021 11:56:11 by licwim          #
#                                                   #
# ================================================= #

import json
from tam.config import Config

CONFIG_FILE = 'secrets.json'

with open(CONFIG_FILE, 'r') as fp:
    config = json.load(fp)
Config.USERNAME = config.get('username')
Config.API_ID = config.get('api_id')
Config.API_HASH = config.get('api_hash')
