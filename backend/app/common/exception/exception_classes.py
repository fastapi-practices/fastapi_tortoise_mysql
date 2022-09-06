#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class AuthorizationException(Exception):
    """
    权限异常
    """

    def __init__(self, err: str = 'Permission denied'):
        self.err = err


class TokenException(Exception):
    """
    token 异常
    """

    def __init__(self, err: str = 'Token is invalid'):
        self.err = err
