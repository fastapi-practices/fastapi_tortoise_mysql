#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_pagination import add_pagination
from tortoise.contrib.fastapi import RegisterTortoise

from backend.app.router import route
from backend.common.exception.exception_handler import register_exception
from backend.core.conf import settings
from backend.core.path_conf import STATIC_DIR
from backend.database.db import mysql_config
from backend.database.redis import redis_client
from backend.utils.demo_site import demo_site
from backend.utils.health_check import ensure_unique_route_names, http_limit_callback
from backend.utils.openapi import simplify_operation_ids


@asynccontextmanager
async def register_init(app: FastAPI):
    """
    启动初始化

    :return:
    """
    # 连接redis
    await redis_client.open()
    # 初始化 limiter
    await FastAPILimiter.init(redis_client, prefix=settings.LIMITER_REDIS_PREFIX, http_callback=http_limit_callback)
    # 连接 db
    async with RegisterTortoise(
        app=app,
        config=mysql_config,
        generate_schemas=True,
    ):
        yield

    yield

    # 关闭redis连接
    await redis_client.close()
    # 关闭 limiter
    await FastAPILimiter.close()


def register_app():
    # FastAPI
    app = FastAPI(
        title=settings.FASTAPI_TITLE,
        version=settings.FASTAPI_VERSION,
        description=settings.FASTAPI_DESCRIPTION,
        docs_url=settings.FASTAPI_DOCS_URL,
        redoc_url=settings.FASTAPI_REDOC_URL,
        openapi_url=settings.FASTAPI_OPENAPI_URL,
        lifespan=register_init,
    )

    # 注册静态文件
    register_static_file(app)

    # 中间件
    register_middleware(app)

    # 路由
    register_router(app)

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
    if settings.FASTAPI_STATIC_FILES:
        from fastapi.staticfiles import StaticFiles

        if not os.path.exists(STATIC_DIR):
            os.makedirs(STATIC_DIR)

        app.mount('/static', StaticFiles(directory=STATIC_DIR), name='static')


def register_middleware(app) -> None:
    # 接口访问日志
    if settings.MIDDLEWARE_ACCESS:
        from backend.middleware.access_middle import AccessMiddleware

        app.add_middleware(AccessMiddleware)
    # 跨域
    if settings.MIDDLEWARE_CORS:
        from starlette.middleware.cors import CORSMiddleware

        app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=['*'],
            allow_headers=['*'],
        )


def register_router(app: FastAPI):
    """
    路由

    :param app: FastAPI
    :return:
    """
    dependencies = [Depends(demo_site)] if settings.DEMO_MODE else None

    # API
    app.include_router(route, dependencies=dependencies)

    # Extra
    ensure_unique_route_names(app)
    simplify_operation_ids(app)


def register_page(app: FastAPI):
    """
    分页查询

    :param app:
    :return:
    """
    add_pagination(app)
