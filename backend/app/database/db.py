#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise.contrib.fastapi import register_tortoise

from backend.app.aerich.env import db_url
from backend.app.core.conf import settings
from backend.app.models import models


def register_db(app):
    register_tortoise(
        app,
        db_url=db_url,
        modules={'models': [*models]},
        add_exception_handlers=settings.ADD_EXCEPTION_HANDLERS,
    )
