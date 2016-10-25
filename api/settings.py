# -*- coding: utf-8 -*-
"""JIMAM: API settings"""

import os

DEBUG = True

BASEDIR = os.path.abspath(os.path.dirname('./'))
LOG_FILE = os.path.join(BASEDIR, 'log/jimam.log')

JIMAM_USERNAME = 'JIMAM'
JIMAM_IP = '127.0.0.1'
JIMAM_PORT = 8000
API_ROOT = '/default'

MATTERMOST_WEBHOOK = 'https://mattermost.host/webhook'