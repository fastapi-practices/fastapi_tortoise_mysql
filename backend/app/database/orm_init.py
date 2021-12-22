#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append('../../')

from backend.app.database import db_url, models

# 指定在 backend/app 目录的终端下进行迁移
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
