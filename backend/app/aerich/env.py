#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append('../../../')

from backend.app.database.mysql_db import db_config
from backend.app.models import models

TORTOISE_ORM = {
    "connections": db_config['connections'],
    "apps": {
        "models": {
            "models": ["aerich.models", *models],
            "default_connection": "default",
        },
    },
}
