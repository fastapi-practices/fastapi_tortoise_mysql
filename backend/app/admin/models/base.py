#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import Model, fields


class UserMixin:
    """
    用户 Mixin 数据类
    """

    create_user = fields.BigIntField(null=False, verbose_name='创建者')
    update_user = fields.BigIntField(null=True, verbose_name='修改者')


class Base(Model):
    """
    基本模型
    """

    created_time = fields.DatetimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = fields.DatetimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        table = ''
        abstract = True
