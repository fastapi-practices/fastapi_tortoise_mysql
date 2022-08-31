#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from hashlib import sha256

import aiofiles
from email_validator import validate_email, EmailNotValidError
from fast_captcha import text_captcha
from fastapi import APIRouter, HTTPException, Depends, Request, Response, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination.ext.tortoise import paginate
from tortoise import timezone

from backend.app.common.redis import redis_client
from backend.app.common.response.response_code import ErrorCode
from backend.app.common.security import jwt_security
from backend.app.common.log import log
from backend.app.common.pagination import Page
from backend.app.common.response.response_schema import Response200, Response404, ResponseError
from backend.app.core.conf import settings
from backend.app.core.path_conf import AvatarPath
from backend.app.crud.crud_user import UserDao
from backend.app.schemas.token import Token
from backend.app.schemas.user import CreateUser, GetUserInfo, ResetPassword, Auth2, Auth
from backend.app.utils import re_verify
from backend.app.utils.format_string import cut_path
from backend.app.utils.send_email import send_verification_code_email

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
#         return ResponseError(ErrorCode.IMAGE_CODE_ERROR)
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
        validate_email(obj.email, check_deliverability=False).email
    except EmailNotValidError:
        raise HTTPException(status_code=403, detail='邮箱格式错误，请重新输入')
    new_user = await UserDao.register_user(obj)
    new_user.creator = request.client.host
    await new_user.save()
    data = await GetUserInfo.from_tortoise_orm(new_user)
    return Response200(data=data)


@user.post('/password/reset/vcode', summary='获取密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_captcha(username_or_email: str, response: Response):
    code = text_captcha()
    # 输入为用户名时
    current_user = await UserDao.get_user_by_username(username_or_email)
    if current_user:
        try:
            response.delete_cookie(key='fastapi_reset_pwd_code')
            response.delete_cookie(key='fastapi_reset_pwd_username')
            response.set_cookie(key='fastapi_reset_pwd_code', value=sha256(code.encode('utf-8')).hexdigest(),
                                max_age=settings.COOKIES_MAX_AGE)
            response.set_cookie(key='fastapi_reset_pwd_username', value=username_or_email,
                                max_age=settings.COOKIES_MAX_AGE)
        except Exception as e:
            log.error('无法发送验证码 {}'.format(e))
            raise HTTPException(status_code=500, detail=f'内部错误，无法发送验证码 {e}')
        current_user_email = await UserDao.get_email_by_username(current_user.username)
        await send_verification_code_email(current_user_email, code)
        return Response200()
    # 输入为邮箱时
    else:
        try:
            validate_email(username_or_email, check_deliverability=False)
        except EmailNotValidError:
            raise HTTPException(status_code=404, detail='用户名不存在，请重新输入')
        current_email = await UserDao.check_email(username_or_email)
        if not current_email:
            raise HTTPException(status_code=404, detail='邮箱不存在，请重新输入')
        try:
            response.delete_cookie(key='fastapi_reset_pwd_code')
            response.delete_cookie(key='fastapi_reset_pwd_username')
            response.set_cookie(key='fastapi_reset_pwd_code', value=sha256(code.encode('utf-8')).hexdigest(),
                                max_age=settings.COOKIES_MAX_AGE)
            username = await UserDao.get_username_by_email(username_or_email)
            response.set_cookie(key='fastapi_reset_pwd_username', value=username, max_age=settings.COOKIES_MAX_AGE)
        except Exception as e:
            log.error('无法发送验证码 {}'.format(e))
            raise HTTPException(status_code=500, detail=f'内部错误，无法发送验证码 {e}')
        await send_verification_code_email(username_or_email, code)
        return Response200()


@user.post('/password/reset', summary='密码重置请求')
async def password_reset(obj: ResetPassword, request: Request, response: Response):
    pwd1 = obj.password1
    pwd2 = obj.password2
    cookie_reset_pwd_code = request.cookies.get('fastapi_reset_pwd_code')
    cookie_reset_pwd_username = request.cookies.get('fastapi_reset_pwd_username')
    if pwd1 != pwd2:
        raise HTTPException(status_code=403, detail='两次密码输入不一致，请重新输入')
    if cookie_reset_pwd_username is None or cookie_reset_pwd_code is None:
        raise HTTPException(status_code=404, detail='验证码已失效，请重新获取验证码')
    if cookie_reset_pwd_code != sha256(obj.code.encode('utf-8')).hexdigest():
        raise HTTPException(status_code=403, detail='验证码错误, 请重新输入')
    if not await UserDao.reset_password(cookie_reset_pwd_username, obj.password2):
        raise HTTPException(status_code=500, detail='内部错误，密码重置失败')
    response.delete_cookie(key='fastapi_reset_pwd_code')
    response.delete_cookie(key='fastapi_reset_pwd_username')
    return Response200()


@user.get('/password/reset/done', summary='重置密码完成')
def password_reset_done():
    return Response200()


@user.put('/me', summary='更新用户信息')
async def update_userinfo(
        username: str = Form(..., title='用户名'),
        email: str = Form(..., title='邮箱'),
        mobile_number: str = Form(None, title='手机号'),
        wechat: str = Form(None, title='微信'),
        qq: str = Form(None, title='QQ'),
        blog_address: str = Form(None, title='博客地址'),
        introduction: str = Form(None, title='自我介绍'),
        avatar: UploadFile = File(None),
        current_user=Depends(jwt_security.get_current_user)
):
    try:
        validate_email(email, check_deliverability=False).email
    except EmailNotValidError:
        raise HTTPException(status_code=403, detail='邮箱格式错误，请重新输入')
    if current_user.username != username:
        _username = await UserDao.get_user_by_username(username)
        if _username:
            raise HTTPException(status_code=403, detail='用户名已注册, 请更换用户名')
    if current_user.email != email:
        _email = await UserDao.check_email(email)
        if _email:
            raise HTTPException(status_code=403, detail='邮箱已注册, 请更换邮箱')
    if mobile_number is not None:
        if not re_verify.is_mobile(mobile_number):
            raise HTTPException(status_code=403, detail='手机号码格式错误')
    if wechat is not None:
        if not re_verify.is_wechat(wechat):
            raise HTTPException(status_code=403, detail='微信号码输入有误')
    if qq is not None:
        if not re_verify.is_qq(qq):
            raise HTTPException(status_code=403, detail='QQ号码输入有误')
    current_filename = await UserDao.get_avatar_by_pk(current_user.id)
    if avatar is not None:
        if current_filename is not None:
            try:
                os.remove(AvatarPath + current_filename)
            except Exception as e:
                log.warning('用户 {} 更新头像时，原头像文件 {} 删除失败\n{}', current_user.username, current_filename, e)
        new_file = await avatar.read()
        if 'image' not in avatar.content_type:
            raise HTTPException(status_code=403, detail='文件格式错误，请重新选择图片')
        _file_name = str(timezone.now().strftime('%Y%m%d%H%M%S.%f')) + '_' + avatar.filename
        if not os.path.exists(AvatarPath):
            os.makedirs(AvatarPath)
        async with aiofiles.open(AvatarPath + f'{_file_name}', 'wb') as f:
            await f.write(new_file)
    else:
        _file_name = current_filename
    new_user = await UserDao.update_userinfo(current_user, username, email, mobile_number, wechat, qq, blog_address,
                                             introduction, _file_name)
    data = await GetUserInfo.from_tortoise_orm(new_user)
    if isinstance(_file_name, str):
        data.avatar = cut_path(AvatarPath + _file_name)[1]
    return Response200(data=data)


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


@user.get('', summary='获取所有用户', response_model=Page[GetUserInfo], dependencies=[Depends(
    jwt_security.get_current_user)])
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
