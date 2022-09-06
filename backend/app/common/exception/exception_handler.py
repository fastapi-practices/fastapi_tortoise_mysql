#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Request, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.responses import JSONResponse

from backend.app.common.exception.exception_classes import AuthorizationException, TokenException
from backend.app.common.response.response_schema import Response401, Response400, Response500, Response422


def register_exception(app: FastAPI):
    @app.exception_handler(AuthorizationException)
    def authorization_error(request: Request, exc: AuthorizationException):
        """
        用户权限异常

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=401,
            content=jsonable_encoder(Response401(msg=exc.err))
        )

    @app.exception_handler(TokenException)
    def token_error(request: Request, exc: TokenException):
        """
        Token异常

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=401,
            content=jsonable_encoder(Response401(msg=exc.err))
        )

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
            content=jsonable_encoder(Response400(code=exc.status_code, msg=exc.detail)),
            headers=exc.headers
        )

    @app.exception_handler(Exception)
    def all_exception_handler(request: Request, exc: Exception):
        """
        全局异常处理

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=500,
            content=jsonable_encoder(Response500(msg=exc.args))
        )

    @app.exception_handler(ValidationError)
    def validation_error(request: Request, exc: ValidationError):
        """
        全局请求数据验证异常处理, 此异常处理主要用于Pydantic类中的数据验证

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(Response422(data={'errors': exc.errors()})),
        )

    @app.exception_handler(RequestValidationError)
    def request_validation_error(request: Request, exc: RequestValidationError):
        """
        全局请求数据验证异常处理

        :param request:
        :param exc:
        :return:
        """
        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(Response422(data={'body': exc.body, 'errors': exc.errors()})),
        )
