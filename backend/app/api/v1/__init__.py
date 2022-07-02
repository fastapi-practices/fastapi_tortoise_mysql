#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.api.v1.v1_captcha import captcha
from backend.app.api.v1.v1_test_redis import rd
from backend.app.api.v1.v1_user import user

v1 = APIRouter(prefix='/v1')

v1.include_router(captcha, prefix='/captcha', tags=['图形验证码'])
v1.include_router(user, prefix='/users', tags=['用户'])
v1.include_router(rd, prefix='/redis', tags=['测试-Redis'])
