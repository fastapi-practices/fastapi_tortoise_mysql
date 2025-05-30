#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import Request
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.admin.crud.crud_user import user_dao
from backend.app.admin.model.user import User
from backend.app.admin.schema.token import GetLoginToken
from backend.app.admin.schema.user import AuthLoginParam
from backend.common.exception import errors
from backend.common.response.response_code import CustomErrorCode
from backend.common.security.jwt import create_access_token, password_verify
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.utils.timezone import timezone


class AuthService:
    @staticmethod
    async def user_verify(username: str, password: str) -> User:
        user = await user_dao.get_by_username(username)
        if not user:
            raise errors.NotFoundError(msg='用户名或密码有误')
        elif not password_verify(password, user.password):
            raise errors.AuthorizationError(msg='用户名或密码有误')
        elif not user.status:
            raise errors.AuthorizationError(msg='用户已被锁定, 请联系统管理员')
        return user

    async def swagger_login(self, *, form_data: OAuth2PasswordRequestForm) -> tuple[str, User]:
        user = await self.user_verify(form_data.username, form_data.password)
        await user_dao.update_login_time(user.username, login_time=timezone.now())
        token = create_access_token(str(user.id))
        return token, user

    async def login(self, *, request: Request, obj: AuthLoginParam) -> GetLoginToken:
        user = await self.user_verify(obj.username, obj.password)
        try:
            captcha_uuid = request.app.state.captcha_uuid
            redis_code = await redis_client.get(f'{settings.CAPTCHA_LOGIN_REDIS_PREFIX}:{captcha_uuid}')
            if not redis_code:
                raise errors.ForbiddenError(msg='验证码失效，请重新获取')
        except AttributeError:
            raise errors.ForbiddenError(msg='验证码失效，请重新获取')
        if redis_code.lower() != obj.captcha.lower():
            raise errors.CustomError(error=CustomErrorCode.CAPTCHA_ERROR)
        await user_dao.update_login_time(user.username, login_time=timezone.now())
        token = create_access_token(str(user.id))
        data = GetLoginToken(access_token=token, user=user)
        return data


auth_service: AuthService = AuthService()
