#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise.contrib.fastapi import register_tortoise

from backend.app.core.conf import settings
from backend.app.models import models

db_url = f"mysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}?charset={settings.DB_ENCODING}&echo={settings.DB_ECHO}"


def register_db(app):
    register_tortoise(
        app,
        db_url=db_url,
        modules={'models': [*models]},
        add_exception_handlers=settings.DB_ADD_EXCEPTION_HANDLERS,
    )
