#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from uuid import uuid4


def use_uuid() -> str:
    """
    生成uuid字符串
    :return:
    """
    return uuid4().hex
