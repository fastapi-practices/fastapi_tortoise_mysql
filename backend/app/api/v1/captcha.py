#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fast_captcha import img_captcha
from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse

from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.utils.generate_string import get_uuid

captcha = APIRouter()


@captcha.get('', summary='获取验证码')
async def get_captcha(request: Request):
    img, code = img_captcha()
    uid = get_uuid()
    request.app.state.captcha_uid = uid
    await redis_client.set(uid, code, settings.CAPTCHA_EXPIRATION_TIME)
    return StreamingResponse(content=img, media_type='image/jpeg')


@captcha.get('/test', summary='验证码测试')
def check_captcha(request: Request):
    try:
        code = request.app.state.captcha_uid
        return {'code': 200, 'captcha_uid': code}
    except AttributeError:
        return {'msg': '请先获取验证码'}
