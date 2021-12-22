#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise.contrib.fastapi import register_tortoise

from backend.app.database import db_url, models


def get_db(app):
    register_tortoise(
        app,
        db_url=db_url,
        modules={'models': models},
    )
