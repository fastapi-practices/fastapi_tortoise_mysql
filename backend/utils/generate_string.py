#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import uuid


def get_uuid4_str() -> str:
    """
    获取 uuid4 字符串

    :return: str(uuid)
    """
    return str(uuid.uuid4())


def get_current_timestamp() -> float:
    """
    获取当前时间戳

    :return:
    """
    return datetime.datetime.now().timestamp()
