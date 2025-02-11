#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4

from tortoise import Model, fields


class User(Model):
    """
    用户类
    """

    id = fields.BigIntField(pk=True, index=True, description='主键id')
    uuid = fields.CharField(max_length=36, default=str(uuid4()), unique=True, description='用户UID')
    username = fields.CharField(max_length=32, unique=True, description='用户名')
    password = fields.CharField(max_length=255, description='密码')
    salt = fields.BinaryField(comment='加密盐')
    email = fields.CharField(max_length=64, unique=True, description='邮箱')
    status = fields.SmallIntField(default=1, description='是否激活')
    is_superuser = fields.BooleanField(default=False, description='是否超级管理员')
    avatar = fields.CharField(max_length=256, null=True, description='头像')
    phone = fields.CharField(max_length=16, null=True, description='手机号')
    join_time = fields.DatetimeField(auto_now_add=True, description='注册时间')
    last_login_time = fields.DatetimeField(null=True, description='上次登录时间')

    class Meta:
        table = 'user'
