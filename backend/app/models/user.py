#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator

from backend.app.database import use_uuid


class User(models.Model):
    """
    用户类
    """
    uid = fields.CharField(max_length=32, default=use_uuid, unique=True, description="用户UID")
    username = fields.CharField(max_length=20, unique=True, description='用户名')
    password = fields.CharField(max_length=256, description='密码')
    email = fields.CharField(max_length=50, unique=True, description='邮箱')
    is_active = fields.BooleanField(default=True, description='是否激活')
    is_superuser = fields.BooleanField(default=False, description='是否超级管理员')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    update_time = fields.DatetimeField(auto_now=True, description='更新时间')

    def __str__(self):
        return self.username


User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude=('uid', 'is_active', 'is_superuser'),
                                         exclude_readonly=True)
