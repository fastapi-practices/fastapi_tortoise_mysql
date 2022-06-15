#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.api import jwt_security
from backend.app.common.log import log
from backend.app.common.redis import redis_client
from backend.app.crud.crud_user import UserDao
from backend.app.schemas import Response200
from backend.app.schemas.sm_token import Token
from backend.app.schemas.sm_user import CreateUser, GetUserInfo, Auth, Auth2

user = APIRouter()

headers = {"WWW-Authenticate": "Bearer"}


@user.post('/login', summary='表单登录', response_model=Token)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    current_user = await UserDao.get_user_by_username(form_data.username)
    if not current_user:
        raise HTTPException(status_code=404, detail='用户名不存在', headers=headers)
    elif not jwt_security.verity_password(form_data.password, current_user.password):
        raise HTTPException(status_code=401, detail='密码错误', headers=headers)
    elif not current_user.is_active:
        raise HTTPException(status_code=401, detail='用户已被锁定', headers=headers)
    await UserDao.update_user_login_time(current_user.pk)
    access_token = jwt_security.create_access_token(current_user.pk)
    log.success('用户 {} 登陆成功', form_data.username)
    return Token(
        access_token=access_token,
        token_type='Bearer',
        is_superuser=current_user.is_superuser
    )


# @user.post('/login', summary='json登录', response_model=Token)
# async def user_login(obj: Auth):
#     current_user = await UserDao.get_user_by_username(obj.username)
#     if not current_user:
#         raise HTTPException(status_code=404, detail='用户名不存在', headers=headers)
#     elif not jwt_security.verity_password(obj.password, current_user.password):
#         raise HTTPException(status_code=401, detail='密码错误', headers=headers)
#     elif not current_user.is_active:
#         raise HTTPException(status_code=401, detail='用户已被锁定', headers=headers)
#     await UserDao.update_user_login_time(current_user.pk)
#     access_token = jwt_security.create_access_token(current_user.pk)
#     log.success('用户 {} 登陆成功', obj.username)
#     return Token(
#         access_token=access_token,
#         token_type='Bearer',
#         is_superuser=current_user.is_superuser
#     )


# @user.post('/login', summary='验证码登录', description='必须启用redis', response_model=Token)
# async def user_login(request: Request, obj: Auth2):
#     current_user = await UserDao.get_user_by_username(obj.username)
#     if not current_user:
#         raise HTTPException(status_code=404, detail='用户名不存在', headers=headers)
#     elif not jwt_security.verity_password(obj.password, current_user.password):
#         raise HTTPException(status_code=401, detail='密码错误', headers=headers)
#     elif not current_user.is_active:
#         raise HTTPException(status_code=401, detail='用户已被锁定', headers=headers)
#     try:
#         captcha_code = request.app.state.captcha_uid
#         redis_code = redis_client.get(f"{captcha_code}")
#         if not redis_code:
#             raise HTTPException(status_code=403, detail='验证码失效，请重新获取', headers=headers)
#     except AttributeError:
#         raise HTTPException(status_code=403, detail='验证码失效，请重新获取', headers=headers)
#     if redis_code.lower() != obj.captcha.lower() or redis_code.upper() != obj.captcha.upper():
#         raise HTTPException(status_code=412, detail='验证码输入错误', headers=headers)
#     await UserDao.update_user_login_time(current_user.pk)
#     access_token = jwt_security.create_access_token(current_user.pk)
#     log.success('用户 {} 登陆成功', obj.username)
#     return Token(
#         access_token=access_token,
#         token_type='Bearer',
#         is_superuser=current_user.is_superuser
#     )


@user.post('/logout', summary='登出', dependencies=[Depends(jwt_security.get_current_user)])
async def user_logout():
    return Response200()


@user.post('/register', summary='注册', response_model=Response200)
async def create_user(request: Request, obj: CreateUser):
    username = await UserDao.get_user_by_username(name=obj.username)
    if username:
        raise HTTPException(status_code=403, detail='该用户名已被注册~')
    email = await UserDao.check_email(email=obj.email)
    if email:
        raise HTTPException(status_code=403, detail='该邮箱已被注册~')
    try:
        validate_email(obj.email).email
    except EmailNotValidError:
        raise HTTPException(status_code=403, detail='邮箱格式错误，请重新输入')
    new_user = await UserDao.register_user(obj)
    new_user.creator = request.client.host
    await new_user.save()
    data = await GetUserInfo.from_tortoise_orm(new_user)
    return Response200(data=data)


@user.get('/me', summary='获取用户信息', response_model=GetUserInfo)
async def get_user_info(userinfo=Depends(jwt_security.get_current_user)):
    return userinfo
