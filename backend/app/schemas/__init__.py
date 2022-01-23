#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Any

from pydantic import BaseModel


class ResponseBase(BaseModel):
    msg: Optional[str] = None
    data: Optional[Any] = None


class Response200(ResponseBase):
    code: int = 200


class Response301(ResponseBase):
    code: int = 301


class Response401(ResponseBase):
    code: int = 401


class Response403(ResponseBase):
    code: int = 403


class Response404(ResponseBase):
    code: int = 404


class Response500(ResponseBase):
    code: int = 500


class Response502(ResponseBase):
    code: int = 502
