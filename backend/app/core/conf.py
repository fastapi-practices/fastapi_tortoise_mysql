#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

    # 静态文件代理
    STATIC_FILE: bool = True

    # Uvicorn
    UVICORN_HOST: str = '127.0.0.1'
    UVICORN_PORT: int = 8000
    UVICORN_RELOAD: bool = True

    # DB
    DB_ADD_EXCEPTION_HANDLERS: bool = True  # 线上环境请使用 False
    DB_ECHO: bool = False  # 是否显示SQL语句
    DB_HOST: str = '127.0.0.1'
    DB_PORT: int = 3306
    DB_USER: str = 'root'
    DB_PASSWORD: str = '123456'
    DB_DATABASE: str = 'ftm'
    DB_ENCODING: str = 'utf8mb4'

    # Redis
    REDIS_OPEN: bool = False  # 是否开启Redis, 默认关闭
    REDIS_HOST: str = '127.0.0.1'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ''
    REDIS_DATABASE: int = 0
    REDIS_TIMEOUT: int = 10

    # Token
    TOKEN_ALGORITHM: str = 'HS256'
    TOKEN_SECRET_KEY: str = '0ou59yzj-QwX8JT8Mq8o2rIOvxpwtVWH3aFH2-QLo7c'  # 密钥 (py生成方法：print(secrets.token_urlsafe(32)))
    TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 3  # token 时效 60 * 24 * 3 = 3 天

    # 中间件
    MIDDLEWARE_CORS: bool = True
    MIDDLEWARE_GZIP: bool = True
    MIDDLEWARE_ACCESS: bool = True


@lru_cache
def get_settings():
    """ 读取配置优化写法 """
    return Settings()


settings = get_settings()
