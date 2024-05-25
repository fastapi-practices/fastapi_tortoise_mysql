#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append('../../')

from backend.app.database.db_mysql import mysql_config
from backend.app.models import models

TORTOISE_ORM = {
    'connections': mysql_config['connections'],
    'apps': {
        'ftm': {
            'models': ['aerich.models', *models],
            'default_connection': 'default',
        },
    },
}
