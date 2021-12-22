#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import fields, models
from tortoise.contrib.pydantic import pydantic_model_creator


class Project(models.Model):
    """
    项目管理
    """
    name = fields.CharField(max_length=255, unique=True, description='项目名称')
    description = fields.TextField(null=True, description='项目描述')
    created_time = fields.DatetimeField(auto_now_add=True, description='创建时间')
    modified_time = fields.DatetimeField(auto_now=True, description='修改时间')

    def __str__(self):
        return self.name


Project_Pydantic = pydantic_model_creator(Project, name='Project')
ProjectIn_Pydantic = pydantic_model_creator(Project, name='ProjectIn', exclude_readonly=True)
