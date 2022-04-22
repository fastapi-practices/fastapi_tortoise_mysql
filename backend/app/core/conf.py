#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import secrets
from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    """ 配置类 """

    # FastAPI
    TITLE: str = 'DEMO'
    VERSION: str = 'v0.0.1'
    DESCRIPTION: str = """
项目描述  
"""
    DOCS_URL: str = '/v1/docs'
    OPENAPI_URL: str = '/v1/openapi'
    REDOCS_URL: bool = False

    DEBUG = True

    # Uvicorn
    HOST: str = '127.0.0.1'
    PORT: int = 8000
    RELOAD: bool = True

    # DB
    ADD_EXCEPTION_HANDLERS = True  # 线上环境请使用 False
    DB_ECHO = False  # 是否显示SQL语句
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: str = '123456'
    DB_DATABASE: str = 'autotest'
    DB_ENCODING: str = 'utf8mb4'

    # Token
    ALGORITHM: str = 'HS256'
    SECRET_KEY: str = '0ou59yzj-QwX8JT8Mq8o2rIOvxpwtVWH3aFH2-QLo7c'  # 密钥 (py生成方法：print(secrets.token_urlsafe(32)))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3  # token 时效 60 * 24 * 3 = 3 天

    # 中间件
    CORS: bool = True
    GZIP: bool = True
    ACCESS: bool = True


@lru_cache
def get_settings():
    """ 读取配置优化写法 """
    return Settings()


settings = get_settings()
