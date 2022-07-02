#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

from backend.app.core.conf import settings
from backend.app.models import models

db_config = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.mysql',
            'credentials': {
                'host': f'{settings.DB_HOST}',
                'port': f'{settings.DB_PORT}',
                'user': f'{settings.DB_USER}',
                'password': f'{settings.DB_PASSWORD}',
                'database': f'{settings.DB_DATABASE}',
                'charset': f'{settings.DB_ENCODING}',
                'echo': f'{settings.DB_ECHO}'
            }
        },
    },
    'apps': {
        'models': {
            'models': [*models],
            'default_connection': 'default',
        },
    },
    'use_tz': False,
    'timezone': 'Asia/Shanghai'
}


def register_db(app: FastAPI):
    register_tortoise(
        app,
        config=db_config,
        generate_schemas=True,
        add_exception_handlers=settings.DB_ADD_EXCEPTION_HANDLERS,
    )
