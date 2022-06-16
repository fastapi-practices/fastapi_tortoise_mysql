#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination.ext.tortoise import paginate

from backend.app.api import jwt_security
from backend.app.common.log import log
from backend.app.common.pagination import Page
from backend.app.common.redis import redis_client
from backend.app.core.path_conf import AvatarPath
from backend.app.crud.crud_user import UserDao
from backend.app.schemas import Response200, Response404
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
#         redis_code = await redis_client.get(f"{captcha_code}")
#         if not redis_code:
#             raise HTTPException(status_code=403, detail='验证码失效，请重新获取', headers=headers)
#     except AttributeError:
#         raise HTTPException(status_code=403, detail='验证码失效，请重新获取', headers=headers)
#     if redis_code.lower() != obj.captcha_code.lower() or redis_code.upper() != obj.captcha_code.upper():
#         raise HTTPException(status_code=412, detail='验证码输入错误', headers=headers)
#     await UserDao.update_user_login_time(current_user.pk)
#     access_token = jwt_security.create_access_token(current_user.pk)
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


@user.post('/password/reset/captcha', summary='获取密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_captcha():
    return {'msg': 'on the way'}


@user.post('/password/reset', summary='密码重置请求')
async def password_reset():
    return {'msg': 'on the way'}


@user.get('/password/reset/done', summary='重置密码完成')
def password_reset_done():
    return Response200()


@user.put('/me', summary='更新用户信息')
async def update_userinfo(current_user=Depends(jwt_security.get_current_user)):
    return {'msg': 'on the way'}


@user.delete('/me/avatar', summary='删除头像文件')
async def delete_avatar(current_user=Depends(jwt_security.get_current_user)):
    current_filename = await UserDao.get_avatar_by_pk(current_user.id)
    if current_filename is not None:
        try:
            os.remove(AvatarPath + current_filename)
        except Exception as e:
            log.warning('用户 {} 删除头像文件 {} 失败\n{}', current_user.username, current_filename, e)
    else:
        return Response404(msg='未上传头像，请上传头像后再执行此操作')
    await UserDao.delete_avatar(current_user.id)
    return Response200()


@user.get('/me', summary='获取用户信息', response_model=GetUserInfo)
async def get_user_info(userinfo=Depends(jwt_security.get_current_user)):
    return userinfo


@user.get('', summary='获取所有用户', response_model=Page[GetUserInfo], dependencies=[Depends(jwt_security.get_current_user)])
async def get_all_users():
    return await paginate(UserDao.model.all().order_by('-id'))


@user.post('/{pk}/super', summary='修改用户超级权限', dependencies=[Depends(jwt_security.get_current_is_superuser)])
async def super_set(pk: int):
    if await UserDao.get_user_by_id(pk):
        await UserDao.super_set(pk)
        status = await UserDao.get_user_super_status(pk)
        return Response200(data=status)
    return Response404(msg=f'用户 {pk} 不存在')


@user.post('/{pk}/action', summary='修改用户状态', dependencies=[Depends(jwt_security.get_current_is_superuser)])
async def active_set(pk: int):
    if await UserDao.get_user_by_id(pk):
        await UserDao.active_set(pk)
        status = await UserDao.get_user_active_status(pk)
        return Response200(data=status)
    return Response404(msg=f'用户 {pk} 不存在')


@user.delete('/me', summary='用户注销', description='用户注销 != 用户退出，注销之后用户将从数据库删除')
async def delete_user(current_user=Depends(jwt_security.get_current_user)):
    current_filename = await UserDao.get_avatar_by_pk(current_user.id)
    try:
        if current_filename is not None:
            os.remove(AvatarPath + current_filename)
    except Exception as e:
        log.warning(f'删除用户 {current_user.username} 头像文件:{current_filename} 失败\n{e}')
    finally:
        await UserDao.delete_user(current_user.id)
        return Response200()
