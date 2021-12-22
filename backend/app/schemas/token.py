#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """
    token 返回
    """
    code: int
    msg: Optional[str] = None
    token: str
    token_type: str
    is_superuser: Optional[bool]
