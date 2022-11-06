#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from hashlib import sha256

from email_validator import validate_email, EmailNotValidError
from fast_captcha import text_captcha
from fastapi import Request, HTTPException, Response, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_pagination.ext.tortoise import paginate

from backend.app.api import jwt
from backend.app.common.exception import errors
from backend.app.common.log import log
from backend.app.core.conf import settings
from backend.app.core.path_conf import AvatarPath
from backend.app.crud.crud_user import UserDao
from backend.app.models.user import User
from backend.app.schemas.user import CreateUser, ResetPassword, UpdateUser
from backend.app.utils import re_verify
from backend.app.utils.generate_string import get_current_timestamp
from backend.app.utils.send_email import send_verification_code_email


async def login(form_data: OAuth2PasswordRequestForm):
    current_user = await UserDao.get_user_by_username(form_data.username)
    if not current_user:
        raise errors.NotFoundError(msg='用户名不存在')
    elif not jwt.verity_password(form_data.password, current_user.password):
        raise errors.AuthorizationError(msg='密码错误')
    elif not current_user.is_active:
        raise errors.AuthorizationError(msg='该用户已被锁定，无法登录')
    await UserDao.update_user_login_time(current_user.pk)
    access_token = jwt.create_access_token(current_user.pk)
    return access_token, current_user.is_superuser


# async def login(obj: Auth):
#     current_user = await UserDao.get_user_by_username(obj.username)
#     if not current_user:
#         raise errors.NotFoundError(msg='用户名不存在')
#     elif not jwt.verity_password(obj.password, current_user.password):
#         raise errors.AuthorizationError(msg='密码错误')
#     elif not current_user.is_active:
#         raise errors.AuthorizationError(msg='该用户已被锁定，无法登录')
#     await UserDao.update_user_login_time(current_user.pk)
#     access_token = jwt.create_access_token(current_user.pk)
#     return access_token, current_user.is_superuser


# async def login(*, obj: Auth2, request: Request):
#     current_user = await UserDao.get_user_by_username(obj.username)
#     if not current_user:
#         raise errors.NotFoundError(msg='用户名不存在')
#     elif not jwt.verity_password(obj.password, current_user.password):
#         raise errors.AuthorizationError(msg='密码错误')
#     elif not current_user.is_active:
#         raise errors.AuthorizationError(msg='该用户已被锁定，无法登录')
#     try:
#         captcha_code = request.app.state.captcha_uid
#         redis_code = await redis_client.get(f"{captcha_code}")
#         if not redis_code:
#             raise errors.ForbiddenError(msg='验证码失效，请重新获取')
#     except AttributeError:
#         raise errors.ForbiddenError(msg='验证码失效，请重新获取')
#     if redis_code.lower() != obj.captcha_code.lower():
#         raise errors.CodeError(error=CodeEnum.CAPTCHA_ERROR)
#     await UserDao.update_user_login_time(current_user.pk)
#     access_token = jwt.create_access_token(current_user.pk)
#     return access_token, current_user.is_superuser


async def register(obj: CreateUser):
    username = await UserDao.get_user_by_username(name=obj.username)
    if username:
        raise errors.ForbiddenError(msg='该用户名已被注册~')
    email = await UserDao.check_email(email=obj.email)
    if email:
        raise errors.ForbiddenError(msg='该邮箱已被注册~')
    try:
        validate_email(obj.email, check_deliverability=False).email
    except EmailNotValidError:
        raise errors.ForbiddenError(msg='邮箱格式错误，请重新输入')
    await UserDao.register_user(obj)


async def get_pwd_rest_captcha(*, username_or_email: str, response: Response):
    code = text_captcha()
    if await UserDao.get_user_by_username(username_or_email):
        try:
            response.delete_cookie(key='fastapi_reset_pwd_code')
            response.delete_cookie(key='fastapi_reset_pwd_username')
            response.set_cookie(
                key='fastapi_reset_pwd_code',
                value=sha256(code.encode('utf-8')).hexdigest(),
                max_age=settings.COOKIES_MAX_AGE
            )
            response.set_cookie(
                key='fastapi_reset_pwd_username',
                value=username_or_email,
                max_age=settings.COOKIES_MAX_AGE
            )
        except Exception as e:
            log.exception('无法发送验证码 {}', e)
            raise e
        current_user_email = await UserDao.get_email_by_username(username_or_email)
        await send_verification_code_email(current_user_email, code)
    else:
        try:
            validate_email(username_or_email, check_deliverability=False)
        except EmailNotValidError:
            raise HTTPException(status_code=404, detail='用户名不存在')
        email_result = await UserDao.check_email(username_or_email)
        if not email_result:
            raise HTTPException(status_code=404, detail='邮箱不存在')
        try:
            response.delete_cookie(key='fastapi_reset_pwd_code')
            response.delete_cookie(key='fastapi_reset_pwd_username')
            response.set_cookie(
                key='fastapi_reset_pwd_code',
                value=sha256(code.encode('utf-8')).hexdigest(),
                max_age=settings.COOKIES_MAX_AGE
            )
            username = await UserDao.get_username_by_email(username_or_email)
            response.set_cookie(
                key='fastapi_reset_pwd_username',
                value=username,
                max_age=settings.COOKIES_MAX_AGE
            )
        except Exception as e:
            log.exception('无法发送验证码 {}', e)
            raise e
        await send_verification_code_email(username_or_email, code)


async def pwd_reset(*, obj: ResetPassword, request: Request, response: Response):
    pwd1 = obj.password1
    pwd2 = obj.password2
    cookie_reset_pwd_code = request.cookies.get('fastapi_reset_pwd_code')
    cookie_reset_pwd_username = request.cookies.get('fastapi_reset_pwd_username')
    if pwd1 != pwd2:
        raise errors.ForbiddenError(msg='两次密码输入不一致')
    if cookie_reset_pwd_username is None or cookie_reset_pwd_code is None:
        raise errors.NotFoundError(msg='验证码已失效，请重新获取验证码')
    if cookie_reset_pwd_code != sha256(obj.code.encode('utf-8')).hexdigest():
        raise errors.ForbiddenError(msg='验证码错误')
    await UserDao.reset_password(cookie_reset_pwd_username, obj.password2)
    response.delete_cookie(key='fastapi_reset_pwd_code')
    response.delete_cookie(key='fastapi_reset_pwd_username')


async def get_user_info(username: str):
    user = await UserDao.get_user_by_username(username)
    if not user:
        raise errors.NotFoundError(msg='用户不存在')
    return user


async def update(*, current_user: User, obj: UpdateUser):
    if current_user.username != obj.username:
        username = await UserDao.get_user_by_username(obj.username)
        if username:
            raise errors.ForbiddenError(msg='该用户名已存在')
    if current_user.email != obj.email:
        _email = await UserDao.check_email(obj.email)
        if _email:
            raise errors.ForbiddenError(msg='该邮箱已注册')
        try:
            validate_email(obj.email, check_deliverability=False).email
        except EmailNotValidError:
            raise errors.ForbiddenError(msg='邮箱格式错误')
    if obj.mobile_number is not None:
        if not re_verify.is_mobile(obj.mobile_number):
            raise errors.ForbiddenError(msg='手机号码输入有误')
    if obj.wechat is not None:
        if not re_verify.is_wechat(obj.wechat):
            raise errors.ForbiddenError(msg='微信号码输入有误')
    if obj.qq is not None:
        if not re_verify.is_qq(obj.qq):
            raise errors.ForbiddenError(msg='QQ号码输入有误')
    count = await UserDao.update_userinfo(current_user, obj)
    return count


async def update_avatar(*, current_user: User, avatar: UploadFile):
    current_filename = await UserDao.get_avatar_by_username(current_user.username)
    if avatar is not None:
        if current_filename is not None:
            try:
                os.remove(AvatarPath + current_filename)
            except Exception as e:
                log.error('用户 {} 更新头像时，原头像文件 {} 删除失败\n{}', current_user.username, current_filename,
                          e)
        new_file = avatar.file.read()
        if 'image' not in avatar.content_type:
            raise errors.ForbiddenError(msg='图片格式错误，请重新选择图片')
        _file_name = str(get_current_timestamp()) + '_' + avatar.filename
        if not os.path.exists(AvatarPath):
            os.makedirs(AvatarPath)
        with open(AvatarPath + f'{_file_name}', 'wb') as f:
            f.write(new_file)
    else:
        _file_name = current_filename
    count = await UserDao.update_avatar(current_user, _file_name)
    return count


async def delete_avatar(current_user: User):
    current_filename = await UserDao.get_avatar_by_username(current_user.username)
    if current_filename is not None:
        try:
            os.remove(AvatarPath + current_filename)
        except Exception as e:
            log.error('用户 {} 删除头像文件 {} 失败\n{}', current_user.username, current_filename, e)
    else:
        raise errors.NotFoundError(msg='用户没有头像文件，请上传头像文件后再执行此操作')
    count = await UserDao.delete_avatar(current_user.id)
    return count


async def get_user_list():
    return await paginate(UserDao.model.all().order_by('-id'))


async def update_permission(pk: int):
    if await UserDao.get_user_by_id(pk):
        count = await UserDao.super_set(pk)
        return count
    else:
        raise errors.NotFoundError(msg='用户不存在')


async def update_active(pk: int):
    if await UserDao.get_user_by_id(pk):
        count = await UserDao.active_set(pk)
        return count
    else:
        raise errors.NotFoundError(msg='用户不存在')


async def delete(current_user: User):
    current_filename = await UserDao.get_avatar_by_username(current_user.username)
    try:
        if current_filename is not None:
            os.remove(AvatarPath + current_filename)
    except Exception as e:
        log.error(f'删除用户 {current_user.username} 头像文件:{current_filename} 失败\n{e}')
    finally:
        count = await UserDao.delete_user(current_user.id)
        return count
