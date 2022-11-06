#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from backend.app.models.user import User

Auth = pydantic_model_creator(
    User,
    include=('username', 'password'),
    name='Auth'
)


class Auth2(Auth):
    captcha_code: str


CreateUser = pydantic_model_creator(
    User,
    include=('username', 'password', 'email'),
    name='CreateUser'
)


class UpdateUser(BaseModel):
    username: str
    email: str
    mobile_number: Optional[str] = None
    wechat: Optional[str] = None
    qq: Optional[str] = None
    blog_address: Optional[str] = None
    introduction: Optional[str] = None


GetUserInfo = pydantic_model_creator(
    User,
    exclude=('password',),
    name='GetUserInfo'
)


class ResetPassword(BaseModel):
    code: str
    password1: str
    password2: str
