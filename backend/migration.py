#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys

sys.path.append('../')

from backend.database.db import mysql_config

TORTOISE_ORM = {
    'connections': mysql_config['connections'],
    'apps': mysql_config['apps'],
}
