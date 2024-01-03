# http://errbot.io/en/latest/user_guide/configuration/slack.html

import logging
from json import loads as json_loads
from os import getenv
from os.path import dirname, join

def map_path(target_name):
    '''Enables path names to be dynamically ascertained at runtime.'''
    return join(dirname(__file__), target_name).replace('\\', '/')

BACKEND = 'SlackV3'

BOT_IDENTITY = {
    'token': getenv('ERRBOT-TOKEN'),
    'signing_secret': getenv('ERRBOT-SIGNING-SECRET'),
    'app_token': getenv('ERRBOT-APP-TOKEN'),
}

BOT_ADMINS = json_loads(getenv('ERRBOT-ADMINS'))
BOT_ALT_PREFIXES = ('@tradingpost',)
CHATROOM_PRESENCE = () # this should be empty
SUPPRESS_CMD_NOT_FOUND = True

BOT_DATA_DIR = map_path('data')
BOT_EXTRA_PLUGIN_DIR = map_path('plugins')
CORE_PLUGINS = ('ACLs', 'CommandNotFoundFilter', 'Health', 'Help', 'Plugins', 'Utils')

BOT_LOG_FILE = None
BOT_LOG_LEVEL = logging.INFO
