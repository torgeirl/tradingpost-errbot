# http://errbot.io/en/latest/user_guide/configuration/slack.html

import logging
from os import getenv
from os.path import dirname, join

def map_path(target_name):
    '''Enables path names to be dynamically ascertained at runtime.'''
    return join(dirname(__file__), target_name).replace('\\', '/')

BACKEND = 'SlackRTM'

BOT_IDENTITY = {
    'token': getenv('ERRBOT-TOKEN'),
}

BOT_ADMINS = (getenv('ERRBOT-ADMINS'))
BOT_ALT_PREFIXES = ('@tradingpost',)
CHATROOM_PRESENCE = () # this should be empty
SUPPRESS_CMD_NOT_FOUND = True

BOT_DATA_DIR = map_path('data')
BOT_EXTRA_PLUGIN_DIR = map_path('plugins')

BOT_LOG_FILE = None
BOT_LOG_LEVEL = logging.INFO
