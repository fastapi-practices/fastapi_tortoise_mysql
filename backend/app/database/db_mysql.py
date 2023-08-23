#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from backend.app.core.conf import settings
from backend.app.models import models

mysql_config = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': f'{settings.DB_HOST}',
                'port': settings.DB_PORT,
                'user': f'{settings.DB_USER}',
                'password': f'{settings.DB_PASSWORD}',
                'database': f'{settings.DB_DATABASE}',
                'charset': f'{settings.DB_ENCODING}',
                'echo': settings.DB_ECHO,
            },
        },
    },
    'apps': {
        'ftm': {
            'models': [*models],
            'default_connection': 'default',
        },
    },
    'use_tz': False,
    'timezone': settings.DB_TIMEZONE,
}
