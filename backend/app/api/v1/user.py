#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends, Request, Response, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.api import jwt
from backend.app.api.service import user_service
from backend.app.common.pagination import Page
from backend.app.common.response.response_schema import response_base
from backend.app.models.user import User
from backend.app.schemas.token import Token
from backend.app.schemas.user import CreateUser, GetUserInfo, ResetPassword, UpdateUser

user = APIRouter()


@user.post('/login', summary='表单登录', response_model=Token)
async def user_login(form_data: OAuth2PasswordRequestForm = Depends()):
    token, is_super = await user_service.login(form_data)
    return Token(access_token=token, is_superuser=is_super)


# @user.post('/login', summary='json登录', response_model=Token)
# async def user_login(obj: Auth):
#     token, is_super = await user_service.login(obj)
#     return Token(access_token=token, is_superuser=is_super)


# @user.post('/login', summary='验证码登录', response_model=Token)
# async def user_login(request: Request, obj: Auth2):
#     token, is_super = await user_service.login(obj=obj, request=request)
#     return Token(access_token=token, is_superuser=is_super)


@user.post('/logout', summary='登出', dependencies=[Depends(jwt.get_current_user)])
async def user_logout():
    return response_base.response_200(msg='退出登录成功')


@user.post('/register', summary='注册')
async def create_user(obj: CreateUser):
    await user_service.register(obj)
    return response_base.response_200(msg='用户注册成功')


@user.post('/password/reset/code', summary='获取密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_captcha(username_or_email: str, response: Response):
    await user_service.get_pwd_rest_captcha(username_or_email=username_or_email, response=response)
    return response_base.response_200(msg='验证码发送成功')


@user.post('/password/reset', summary='密码重置请求')
async def password_reset(obj: ResetPassword, request: Request, response: Response):
    await user_service.pwd_reset(obj=obj, request=request, response=response)
    return response_base.response_200(msg='密码重置成功')


@user.get('/password/reset/done', summary='重置密码完成')
def password_reset_done():
    return response_base.response_200(msg='重置密码完成')


@user.get('/{username}', summary='查看用户信息')
async def get_user_info(username: str):
    current_user = await user_service.get_user_info(username)
    return response_base.response_200(
        msg='查看用户信息成功',
        data=current_user,
        exclude={'password'}
    )


@user.put('/{username}', summary='更新用户信息')
async def update_userinfo(username: str, obj: UpdateUser, current_user: User = Depends(jwt.get_current_user)):
    count = await user_service.update(username=username, current_user=current_user, obj=obj)
    if count > 0:
        return response_base.response_200(msg='更新用户信息成功')
    return response_base.fail()


@user.put('/{username}/avatar', summary='更新头像')
async def update_avatar(username: str, avatar: UploadFile, current_user: User = Depends(jwt.get_current_user)):
    count = await user_service.update_avatar(username=username, current_user=current_user, avatar=avatar)
    if count > 0:
        return response_base.response_200(msg='更新头像成功')
    return response_base.fail()


@user.delete('/{username}/avatar', summary='删除头像文件')
async def delete_avatar(username: str, current_user: User = Depends(jwt.get_current_user)):
    count = await user_service.delete_avatar(username=username, current_user=current_user)
    if count > 0:
        return response_base.response_200(msg='删除用户头像成功')
    return response_base.fail()


@user.get('', summary='获取所有用户', response_model=Page[GetUserInfo], dependencies=[Depends(jwt.get_current_user)])
async def get_all_users():
    return await user_service.get_user_list()


@user.post('/{pk}/super', summary='修改用户超级权限', dependencies=[Depends(jwt.get_current_is_superuser)])
async def super_set(pk: int):
    count = await user_service.update_permission(pk)
    if count > 0:
        return response_base.response_200(msg='修改超级权限成功')
    return response_base.fail()


@user.post('/{pk}/action', summary='修改用户状态', dependencies=[Depends(jwt.get_current_is_superuser)])
async def active_set(pk: int):
    count = await user_service.update_active(pk)
    if count > 0:
        return response_base.response_200(msg='修改用户状态成功')
    return response_base.fail()


@user.delete('/{username}', summary='用户注销', description='用户注销 != 用户退出，注销之后用户将从数据库删除')
async def delete_user(username: str, current_user: User = Depends(jwt.get_current_user)):
    count = await user_service.delete(username=username, current_user=current_user)
    if count > 0:
        return response_base.response_200(msg='用户注销成功')
    return response_base.fail()