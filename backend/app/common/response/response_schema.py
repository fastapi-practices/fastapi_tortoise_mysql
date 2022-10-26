#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional, Any, Union, Set, Dict

from fastapi.encoders import jsonable_encoder
from pydantic import validate_arguments, BaseModel

from backend.app.common.response.response_code import ErrorCode

_JsonEncoder = Union[Set[Union[int, str]], Dict[Union[int, str], Any]]


class ResponseModel(BaseModel):
    """
    统一返回模型, 可以在 FastAPI 接口请求中使用 response_model=ResponseModel 及更多操作, 前提是当它是一个非 200 响应时
    """
    code: int
    msg: str
    data: Optional[Any] = None


class ResponseBase:

    @staticmethod
    def __encode_json(data: Any):
        return jsonable_encoder(
            data,
            custom_encoder={
                # datetime: lambda x: x.strftime("%Y-%m-%d %H:%M:%S")  # 格式化时区时间
            }
        )

    @staticmethod
    @validate_arguments
    def success(*, code: int = 200, msg: str = 'Success', data: Optional[Any] = None,
                exclude: Optional[_JsonEncoder] = None):
        """
        请求成功返回通用方法

        `Pydantic exclude <https://pydantic-docs.helpmanual.io/usage/exporting_models/#advanced-include-and-exclude>`__

        :param code: 返回状态码
        :param msg: 返回信息
        :param data: 返回数据
        :param exclude: 排除返回数据(data)字段, 参考 Pydantic exclude
        :return:
        """
        return ResponseModel(code=code, msg=msg, data=ResponseBase.__encode_json(data)).dict(exclude={'data': exclude})

    @staticmethod
    @validate_arguments
    def fail(*, code: int = 400, msg: str = 'Bad Request', data: Any = None):
        return dict(code=code, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_200(*, msg: str = 'Success', data: Optional[Any] = None, exclude: Optional[_JsonEncoder] = None):
        return ResponseModel(code=200, msg=msg, data=ResponseBase.__encode_json(data)).dict(exclude={'data': exclude})

    @staticmethod
    @validate_arguments
    def response_301(*, msg: str = 'Redirect', data: Any = None):
        return ResponseModel(code=301, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_400(*, msg: str = 'Bad Request', data: Any = None):
        return ResponseModel(code=400, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_401(*, msg: str = 'Unauthorized', data: Any = None):
        return ResponseModel(code=401, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_403(*, msg: str = 'Forbidden', data: Any = None):
        return ResponseModel(code=403, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_404(*, msg: str = 'Not Found', data: Any = None):
        return ResponseModel(code=404, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_422(*, msg: str = 'Request Validation Error', data: Any = None):
        return ResponseModel(code=422, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_500(*, msg: str = 'Internal Server Error', data: Any = None):
        return ResponseModel(code=500, msg=msg, data=data)

    @staticmethod
    @validate_arguments
    def response_502(*, msg: str = 'Bad Gateway', data: Any = None):
        return ResponseModel(code=502, msg=msg, data=data)


class ResponseCustomizeError:
    """
    返回自定义错误状态码和信息

    E.g.::

        response_error(ErrorCode.Request_Validation_Error)
    """

    def __call__(self, error: ErrorCode, data=None):
        return ResponseModel(code=error.code, msg=error.msg, data=data)


response_base = ResponseBase()
response_error = ResponseCustomizeError()

__all__ = [
    'response_base',
    'response_error'
]
