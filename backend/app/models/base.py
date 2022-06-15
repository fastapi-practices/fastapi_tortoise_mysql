#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import models, fields


class ModelsBase(models.Model):
    """
    基本模型
    """
    creator = fields.CharField(max_length=32, null=True, verbose_name='创建者')
    modifier = fields.CharField(max_length=32, null=True, verbose_name='修改者')
    created_time = fields.DatetimeField(auto_now_add=True, verbose_name='创建时间')
    updated_time = fields.DatetimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        abstract = True
