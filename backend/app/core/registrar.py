#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from tortoise.contrib.fastapi import register_tortoise

from backend.app.api.routers import v1
from backend.app.common.exception.exception_handler import register_exception
from backend.app.common.redis import redis_client
from backend.app.core.conf import settings
from backend.app.database.db_mysql import mysql_config
from backend.app.middleware.access_middle import AccessMiddleware
from backend.app.utils.health_check import ensure_unique_route_names, http_limit_callback


def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.TITLE,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        docs_url=settings.DOCS_URL,
        redoc_url=settings.REDOCS_URL,
        openapi_url=settings.OPENAPI_URL,
    )

    # 注册静态文件
    register_static_file(app)

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app)

    # 初始化
    register_init(app)

    # 数据库
    register_db(app)

    # 分页
    register_page(app)

    # 全局异常处理
    register_exception(app)

    return app


def register_static_file(app: FastAPI):
    """
    静态文件交互开发模式, 生产使用 nginx 静态资源服务

    :param app:
    :return:
    """
    if settings.STATIC_FILE:
        import os

        from fastapi.staticfiles import StaticFiles

        if not os.path.exists('./static'):
            os.mkdir('./static')
        app.mount('/static', StaticFiles(directory='static'), name='static')


def register_middleware(app) -> None:
    # 跨域
    if settings.MIDDLEWARE_CORS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )
    # gzip
    if settings.MIDDLEWARE_GZIP:
        app.add_middleware(GZipMiddleware)
    # 接口访问日志
    if settings.MIDDLEWARE_ACCESS:
        app.add_middleware(AccessMiddleware)


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """
    app.include_router(v1)

    # Extra
    ensure_unique_route_names(app)


def register_init(app: FastAPI):
    """
    初始化连接

    :param app: FastAPI
    :return:
    """

    @app.on_event('startup')
    async def startup():
        # 连接redis
        await redis_client.open()
        # 初始化 limiter
        await FastAPILimiter.init(redis_client, prefix=settings.LIMITER_REDIS_PREFIX, http_callback=http_limit_callback)

    @app.on_event('shutdown')
    async def shutdown():
        # 关闭redis连接
        await redis_client.close()


def register_db(app: FastAPI):
    register_tortoise(
        app,
        config=mysql_config,
        generate_schemas=settings.DB_AUTO_GENERATE_SCHEMAS,
    )


def register_page(app: FastAPI):
    """
    分页查询

    :param app:
    :return:
    """
    add_pagination(app)
