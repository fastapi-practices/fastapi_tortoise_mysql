#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.api import jwt_security
from backend.app.api.jwt_security import create_access_token
from backend.app.common.log import log
from backend.app.crud import crud_user
from backend.app.crud.crud_user import register_user
from backend.app.models.user import UserIn_Pydantic, User_Pydantic
from backend.app.schemas import Response200
from backend.app.schemas.sm_token import Token

user = APIRouter()

headers = {"WWW-Authenticate": "Bearer"}


@user.post('/login', summary='登录', response_model=Token)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    current_user = await crud_user.get_user_by_username(form_data.username)
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='用户名不存在', headers=headers)
    elif not jwt_security.verity_password(form_data.password, current_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='密码错误', headers=headers)
    # 创建token
    access_token = create_access_token(current_user.pk)
    log.success('用户 {} 登陆成功', form_data.username)
    return Token(code=200, msg='success', access_token=access_token, token_type='Bearer', is_superuser=current_user.is_superuser)


@user.post('/register', summary='注册', response_model=Response200)
async def create_user(post: UserIn_Pydantic):
    username = await crud_user.get_user_by_username(name=post.username)
    if username:
        raise HTTPException(status_code=403, detail='该用户名已被注册~ 换一个吧')
    email = await crud_user.check_email(email=post.email)
    if email:
        raise HTTPException(status_code=403, detail='该邮箱已被注册~ 换一个吧')
    try:
        validate_email(post.email).email
    except EmailNotValidError:
        raise HTTPException(status_code=403, detail='邮箱格式错误，请重新输入')
    data = await register_user(post)
    return Response200(msg='success', data={
        'username': data.username,
        'email': data.email
    })


@user.get('/user', summary='获取用户信息')
async def get_user_info(current_user: User_Pydantic = Depends(jwt_security.get_current_user)):
    return current_user