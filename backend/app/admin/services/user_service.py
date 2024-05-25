#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from hashlib import sha256

from email_validator import EmailNotValidError, validate_email
from fast_captcha import text_captcha
from fastapi import HTTPException, Request, Response, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.admin.crud.crud_user import UserDao
from backend.app.admin.models.user import User
from backend.app.admin.schemas.user import Auth, Auth2, CreateUser, ResetPassword, UpdateUser
from backend.common import jwt
from backend.common.exception import errors
from backend.common.jwt import superuser_verify
from backend.common.log import log
from backend.common.redis import redis_client
from backend.common.response.response_code import CustomCode
from backend.core.conf import settings
from backend.core.path_conf import AvatarPath
from backend.utils import re_verify
from backend.utils.format_string import cut_path
from backend.utils.generate_string import get_current_timestamp
from backend.utils.send_email import send_verification_code_email


class UserService:
    @staticmethod
    async def user_verify(username: str, password: str):
        user = await UserDao.get_user_by_username(username)
        if not user:
            raise errors.NotFoundError(msg='用户名不存在')
        elif not await jwt.password_verify(password, user.password):
            raise errors.AuthorizationError(msg='密码错误')
        elif not user.status:
            raise errors.AuthorizationError(msg='该用户已被锁定，无法登录')
        return user

    @staticmethod
    async def login_swagger(form_data: OAuth2PasswordRequestForm):
        user = await UserService.user_verify(form_data.username, form_data.password)
        await UserDao.update_user_login_time(user.pk)
        access_token = await jwt.create_access_token(user.pk)
        return access_token, user

    @staticmethod
    async def login_json(obj: Auth):
        user = await UserService.user_verify(obj.username, obj.password)
        await UserDao.update_user_login_time(user.pk)
        access_token = await jwt.create_access_token(user.pk)
        return access_token, user

    @staticmethod
    async def login_captcha(*, obj: Auth2, request: Request):
        user = await UserService.user_verify(obj.username, obj.password)
        try:
            captcha_code = request.app.state.captcha_uid
            redis_code = await redis_client.get(f'{captcha_code}')
            if not redis_code:
                raise errors.ForbiddenError(msg='验证码失效，请重新获取')
        except AttributeError:
            raise errors.ForbiddenError(msg='验证码失效，请重新获取')
        if redis_code.lower() != obj.captcha_code.lower():
            raise errors.CustomError(error=CustomCode.CAPTCHA_ERROR)
        await UserDao.update_user_login_time(user.pk)
        access_token = await jwt.create_access_token(user.pk)
        return access_token, user

    @staticmethod
    async def register(obj: CreateUser):
        username = await UserDao.get_user_by_username(name=obj.username)
        if username:
            raise errors.ForbiddenError(msg='该用户名已被注册')
        email = await UserDao.check_email(email=obj.email)
        if email:
            raise errors.ForbiddenError(msg='该邮箱已被注册')
        await UserDao.register_user(obj)

    @staticmethod
    async def get_pwd_rest_captcha(*, username_or_email: str, response: Response):
        code = text_captcha()
        if await UserDao.get_user_by_username(username_or_email):
            try:
                response.delete_cookie(key='fastapi_reset_pwd_code')
                response.delete_cookie(key='fastapi_reset_pwd_username')
                response.set_cookie(
                    key='fastapi_reset_pwd_code',
                    value=sha256(code.encode('utf-8')).hexdigest(),
                    max_age=settings.COOKIES_MAX_AGE,
                )
                response.set_cookie(
                    key='fastapi_reset_pwd_username', value=username_or_email, max_age=settings.COOKIES_MAX_AGE
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
                    max_age=settings.COOKIES_MAX_AGE,
                )
                username = await UserDao.get_username_by_email(username_or_email)
                response.set_cookie(key='fastapi_reset_pwd_username', value=username, max_age=settings.COOKIES_MAX_AGE)
            except Exception as e:
                log.exception('无法发送验证码 {}', e)
                raise e
            await send_verification_code_email(username_or_email, code)

    @staticmethod
    async def pwd_reset(*, obj: ResetPassword, request: Request, response: Response):
        pwd1 = obj.password1
        pwd2 = obj.password2
        cookie_reset_pwd_code = request.cookies.get('fastapi_reset_pwd_code')
        cookie_reset_pwd_username = request.cookies.get('fastapi_reset_pwd_username')
        if pwd1 != pwd2:
            raise errors.ForbiddenError(msg='两次密码输入不一致')
        if cookie_reset_pwd_username is None or cookie_reset_pwd_code is None:
            raise errors.NotFoundError(msg='验证码已失效，请重新获取')
        if cookie_reset_pwd_code != sha256(obj.code.encode('utf-8')).hexdigest():
            raise errors.ForbiddenError(msg='验证码错误')
        await UserDao.reset_password(cookie_reset_pwd_username, obj.password2)
        response.delete_cookie(key='fastapi_reset_pwd_code')
        response.delete_cookie(key='fastapi_reset_pwd_username')

    @staticmethod
    async def get_user_info(username: str):
        user = await UserDao.get_user_by_username(username)
        if not user:
            raise errors.NotFoundError(msg='用户不存在')
        if user.avatar is not None:
            user.avatar = cut_path(AvatarPath + user.avatar)[1]
        return user

    @staticmethod
    async def update(*, username: str, current_user: User, obj: UpdateUser):
        await superuser_verify(current_user)
        input_user = await UserDao.get_user_by_username(username)
        if not input_user:
            raise errors.NotFoundError(msg='用户不存在')
        if input_user.username != obj.username:
            username = await UserDao.get_user_by_username(obj.username)
            if username:
                raise errors.ForbiddenError(msg='该用户名已存在')
        if input_user.email != obj.email:
            _email = await UserDao.check_email(obj.email)
            if _email:
                raise errors.ForbiddenError(msg='该邮箱已注册')
        if obj.phone is not None:
            if not re_verify.is_phone(obj.phone):
                raise errors.ForbiddenError(msg='手机号码输入有误')
        count = await UserDao.update_userinfo(input_user, obj)
        return count

    @staticmethod
    async def update_avatar(*, username: str, current_user: User, avatar: UploadFile):
        await superuser_verify(current_user)
        input_user = await UserDao.get_user_by_username(username)
        if not input_user:
            raise errors.NotFoundError(msg='用户不存在')
        input_user_avatar = input_user.avatar
        if avatar is not None:
            if input_user_avatar is not None:
                try:
                    os.remove(AvatarPath + input_user_avatar)
                except Exception as e:
                    log.error('用户 {} 更新头像时，原头像文件 {} 删除失败\n{}', username, input_user_avatar, e)
            new_file = avatar.file.read()
            if 'image' not in avatar.content_type:
                raise errors.ForbiddenError(msg='图片格式错误，请重新选择图片')
            file_name = str(get_current_timestamp()) + '_' + avatar.filename
            if not os.path.exists(AvatarPath):
                os.makedirs(AvatarPath)
            with open(AvatarPath + f'{file_name}', 'wb') as f:
                f.write(new_file)
        else:
            file_name = input_user_avatar
        count = await UserDao.update_avatar(input_user, file_name)
        return count

    @staticmethod
    async def delete_avatar(*, username: str, current_user: User):
        await superuser_verify(current_user)
        input_user = await UserDao.get_user_by_username(username)
        if not input_user:
            raise errors.NotFoundError(msg='用户不存在')
        input_user_avatar = input_user.avatar
        if input_user_avatar is not None:
            try:
                os.remove(AvatarPath + input_user_avatar)
            except Exception as e:
                log.error('用户 {} 删除头像文件 {} 失败\n{}', input_user.username, input_user_avatar, e)
        else:
            raise errors.NotFoundError(msg='用户没有头像文件，请上传头像文件后再执行此操作')
        count = await UserDao.delete_avatar(input_user.id)
        return count

    @staticmethod
    async def get_user_list():
        data = await UserDao.get_all()
        return data.order_by('-id')

    @staticmethod
    async def update_permission(pk: int):
        user = await UserDao.get_user_by_id(pk)
        if user:
            await superuser_verify(user)
            count = await UserDao.super_set(pk)
            return count
        else:
            raise errors.NotFoundError(msg='用户不存在')

    @staticmethod
    async def update_status(pk: int):
        user = await UserDao.get_user_by_id(pk)
        if user:
            await superuser_verify(user)
            count = await UserDao.status_set(pk)
            return count
        else:
            raise errors.NotFoundError(msg='用户不存在')

    @staticmethod
    async def delete(*, username: str, current_user: User):
        await superuser_verify(current_user)
        input_user = await UserDao.get_user_by_username(username)
        if not input_user:
            raise errors.NotFoundError(msg='用户不存在')
        input_user_avatar = input_user.avatar
        try:
            if input_user_avatar is not None:
                os.remove(AvatarPath + input_user_avatar)
        except Exception as e:
            log.error(f'删除用户 {input_user.username} 头像文件:{input_user_avatar} 失败\n{e}')
        finally:
            count = await UserDao.delete_user(input_user.id)
            return count
