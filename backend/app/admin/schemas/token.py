#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from backend.app.admin.schemas.base import SchemaBase
from backend.app.admin.schemas.user import GetUserInfo


class Token(SchemaBase):
    code: int = 200
    msg: str = 'Success'
    access_token: str
    token_type: str = 'Bearer'
    user: GetUserInfo
