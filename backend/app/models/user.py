#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class User(models.Model):
    """
    用户类
    """
    username = fields.CharField(max_length=20, unique=True, description='用户名')
    password = fields.CharField(max_length=256, description='密码')
    email = fields.CharField(max_length=50, unique=True, description='邮箱')
    create_time = fields.DatetimeField(auto_now_add=True, description='创建时间')

    def __str__(self):
        return self.username


User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)
