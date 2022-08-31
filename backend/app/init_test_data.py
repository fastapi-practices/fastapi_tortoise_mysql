#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from email_validator import validate_email, EmailNotValidError
from tortoise import Tortoise, run_async

from backend.app.common.security.jwt_security import get_hash_password
from backend.app.common.log import log
from backend.app.database.mysql_db import db_config
from backend.app.models.user import User


class InitData:
    """
    初始化数据
    """

    @staticmethod
    async def create_superuser():
        print('开始创建活跃管理员用户')
        print('请输入用户名:')
        username = input()
        print('请输入密码:')
        password = input()
        print('请输入邮箱:')
        success_email = None
        while True:
            email = input()
            try:
                success_email = validate_email(email).email
            except EmailNotValidError:
                print('邮箱不符合规范，请重新输入：')
                continue
            break
        await User.create(
            username=username,
            password=get_hash_password(password),
            email=success_email,
            is_superuser=True,
            creator='init'
        )
        log.success(f'管理员用户创建成功，账号：{username}，密码：{password}')

    async def init_data(self):
        """
        初始化集
        """
        log.info('--------------- 初始化数据库连接 ---------------')
        await Tortoise.init(config=db_config)
        log.success('--------------- 连接数据库成功 ---------------')

        log.info('--------------- 开始初始化数据 ---------------')
        await self.create_superuser()
        log.info('--------------- 数据初始化完成 ---------------')


if __name__ == '__main__':
    init = InitData()
    run_async(init.init_data())
