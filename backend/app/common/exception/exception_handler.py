#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from backend.app.common.exception.exception_classes import AuthorizationException, TokenException
from backend.app.common.response.response_schema import response_base
from backend.app.core.conf import settings


def register_exception(app: FastAPI):
    @app.exception_handler(HTTPException)
    def http_exception_handler(request: Request, exc: HTTPException):
        """
        全局HTTP异常处理

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(response_base.fail(code=exc.status_code, msg=exc.detail)),
            headers=exc.headers
        )

    @app.exception_handler(Exception)
    def all_exception_handler(request: Request, exc):
        """
        全局异常处理

        :param request:
        :param exc:
        :return:
        """
        # 常规
        if isinstance(exc, (ValidationError, RequestValidationError)):
            message = ""
            data = {}
            print(exc.raw_errors)
            for raw_error in exc.raw_errors:
                if isinstance(raw_error.exc, ValidationError):
                    exc = raw_error.exc
                    if hasattr(exc, 'model'):
                        fields = exc.model.__dict__.get('__fields__')
                        for field_key in fields.keys():
                            field_title = fields.get(field_key).field_info.title
                            data[field_key] = field_title if field_title else field_key
                    for error in exc.errors():
                        field = str(error.get('loc')[-1])
                        _msg = error.get("msg")
                        message += f"{data.get(field, field)}{_msg},"
                elif isinstance(raw_error.exc, json.JSONDecodeError):
                    message += 'json解析失败'
            return JSONResponse(
                status_code=422,
                content=jsonable_encoder(
                    response_base.response_422(
                        msg='请求参数非法' if len(message) == 0 else f"请求参数非法, {message[:-1]}",
                        data={'errors': exc.errors()} if message == "" and settings.UVICORN_RELOAD is True else None
                    )
                )
            )

        # 自定义
        if isinstance(exc, AuthorizationException):
            return JSONResponse(
                status_code=401,
                content=jsonable_encoder(response_base.fail(msg=exc.err))
            )

        if isinstance(exc, TokenException):
            return JSONResponse(
                status_code=401,
                content=jsonable_encoder(response_base.fail(msg=exc.err))
            )

        else:
            return JSONResponse(
                status_code=500,
                content=jsonable_encoder(response_base.response_500(msg=str(exc)))
            )
