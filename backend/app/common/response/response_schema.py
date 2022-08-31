#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Any

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from backend.app.common.response.response_code import ErrorCode


class __ResponseBase(BaseModel):
    code: int = 200
    msg: Optional[Any] = Field(default='Success')
    data: Optional[Any] = None


class Response200(__ResponseBase):
    ...


class Response301(__ResponseBase):
    code: int = 301
    msg: Optional[Any] = Field(default='Moved Permanently')


class Response400(__ResponseBase):
    code: int = 400
    msg: Optional[Any] = Field(default='Bad Request')


class Response401(__ResponseBase):
    code: int = 401
    msg: Optional[Any] = Field(default='Unauthorized')


class Response403(__ResponseBase):
    code: int = 403
    msg: Optional[Any] = Field(default='Forbidden')


class Response404(__ResponseBase):
    code: int = 404
    msg: Optional[Any] = Field(default='Not Found')


class Response422(__ResponseBase):
    code: int = 422
    msg: Optional[Any] = Field(default='Request Validation Error')


class Response500(__ResponseBase):
    code: int = 500
    msg: Optional[Any] = Field(default='Internal Server Error')


class Response502(__ResponseBase):
    code: int = 502
    msg: Optional[Any] = Field(default='Bad Gateway')


class ResponseError:
    """
    返回自定义错误码

    example: ResponseError(ErrorCode.Request_Validation_Error)
    """

    def __init__(self, error: ErrorCode):
        self.error = error

    def __call__(self, *args, **kwargs):
        return JSONResponse(status_code=self.error.code, content=self.error.msg)
