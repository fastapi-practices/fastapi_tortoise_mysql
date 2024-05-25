#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.admin.schemas.token import Token
from backend.app.admin.schemas.user import Auth, Auth2
from backend.app.admin.services.user_service import UserService
from backend.common.jwt import DependsJwtUser
from backend.common.response.response_schema import response_base

router = APIRouter()


@router.post('/swagger_login', summary='swagger 表单登录', description='form 格式登录，仅用于 swagger 文档调试接口')
async def login1(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    token, user = await UserService.login_swagger(form_data)
    return Token(access_token=token, user=user)


@router.post('/login', summary='json登录')
async def login2(obj: Auth) -> Token:
    token, user = await UserService.login_json(obj)
    return Token(access_token=token, user=user)


@router.post('/captcha_login', summary='验证码登录')
async def login3(request: Request, obj: Auth2) -> Token:
    token, user = await UserService.login_captcha(obj=obj, request=request)
    return Token(access_token=token, user=user)


@router.post('/logout', summary='登出', dependencies=[DependsJwtUser])
async def user_logout():
    return await response_base.response_200()
