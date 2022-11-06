#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import Model, fields

from backend.app.database import use_uuid


class User(Model):
    """
    用户类
    """
    id = fields.BigIntField(pk=True, index=True, description='主键id')
    uid = fields.CharField(max_length=64, default=use_uuid, unique=True, description="用户UID")
    username = fields.CharField(max_length=32, unique=True, description='用户名')
    password = fields.CharField(max_length=256, description='密码')
    email = fields.CharField(max_length=64, unique=True, description='邮箱')
    is_active = fields.BooleanField(default=True, description='是否激活')
    is_superuser = fields.BooleanField(default=False, description='是否超级管理员')
    avatar = fields.CharField(max_length=256, null=True, description='头像')
    mobile_number = fields.CharField(max_length=16, null=True, description='手机号')
    wechat = fields.CharField(max_length=32, null=True, description='微信')
    qq = fields.CharField(max_length=16, null=True, description='QQ')
    blog_address = fields.CharField(max_length=128, null=True, description='博客地址')
    introduction = fields.TextField(max_length=16, null=True, description='自我介绍')
    last_login = fields.DatetimeField(null=True, description='上次登录时间')
    created_time = fields.DatetimeField(auto_now_add=True, description='注册时间')
    updated_time = fields.DatetimeField(auto_now=True, description='更新时间')

    class Meta:
        table = 'user'
