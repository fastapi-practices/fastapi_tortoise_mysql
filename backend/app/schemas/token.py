#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel

from backend.app.schemas.base import SchemaBase
from backend.app.schemas.user import GetUserInfo


class Token(SchemaBase):
    code: int = 200
    msg: str = 'Success'
    access_token: str
    token_type: str = 'Bearer'
    user: GetUserInfo
