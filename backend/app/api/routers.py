#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.api.v1.user import user
from backend.app.api.v1.captcha import captcha

v1 = APIRouter(prefix='/v1')

v1.include_router(captcha, prefix='/captcha', tags=['图形验证码'])

v1.include_router(user, prefix='/users', tags=['用户'])
