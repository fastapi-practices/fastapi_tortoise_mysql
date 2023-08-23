#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
from typing import Optional

from email_validator import validate_email, EmailNotValidError
from pydantic import UUID4, EmailStr, field_validator, ConfigDict

from backend.app.schemas.base import SchemaBase


class Auth(SchemaBase):
    username: str
    password: str


class Auth2(Auth):
    captcha_code: str


class CreateUser(SchemaBase):
    username: str
    password: str
    email: str

    @field_validator('email')
    @classmethod
    def email_validate(cls, v: str):
        try:
            validate_email(v, check_deliverability=False).email
        except EmailNotValidError:
            raise ValueError()
        return v


class UpdateUser(SchemaBase):
    username: str
    email: str
    phone: Optional[str] = None

    @field_validator('email')
    @classmethod
    def email_validate(cls, v: str):
        try:
            validate_email(v, check_deliverability=False).email
        except EmailNotValidError:
            raise ValueError('邮箱格式错误')
        return v


class GetUserInfo(SchemaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    uuid: UUID4
    username: str
    email: EmailStr
    status: int
    is_superuser: bool
    avatar: Optional[str] = None
    phone: Optional[str] = None
    joined_time: datetime.datetime
    last_login_time: Optional[datetime.datetime] = None


class ResetPassword(SchemaBase):
    code: str
    password1: str
    password2: str
