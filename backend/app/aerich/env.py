#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
sys.path.append('../../../')

from backend.app.models import models
from backend.app.core.conf import settings

db_url = f"mysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_DATABASE}?charset={settings.DB_ENCODING}"


TORTOISE_ORM = {
    "connections": {
        "default": db_url
    },
    "apps": {
        "models": {
            "models": ["aerich.models", *models],
            "default_connection": "default",
        },
    },
}
