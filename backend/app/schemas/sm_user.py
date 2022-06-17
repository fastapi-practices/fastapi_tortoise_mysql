#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pydantic import BaseModel
from tortoise.contrib.pydantic import pydantic_model_creator

from backend.app.models.user import User

Auth = pydantic_model_creator(User, include=('username', 'password'), name='Auth')


class Auth2(Auth):
    captcha_code: str


CreateUser = pydantic_model_creator(User, include=('username', 'password', 'email'), name='CreateUser')


class UpdateUser(BaseModel):
    ...


GetUserInfo = pydantic_model_creator(User, exclude=('password',), name='GetUserInfo')


class ResetPassword(BaseModel):
    code: str
    password1: str
    password2: str
