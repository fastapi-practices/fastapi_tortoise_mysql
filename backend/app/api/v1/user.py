#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from fastapi import APIRouter, Depends

from backend.app.api import jwt_security
from backend.app.api.jwt_security import get_current_user
from backend.app.schemas.token import Token

user = APIRouter()

headers = {"WWW-Authenticate": "Bearer"}


@user.post('/login', summary='用户登录', response_model=Token)
async def user_login():
    pass


@user.post('/logout', summary='用户退出')
async def user_logout():
    pass


@user.post('/register', summary='用户注册')
async def user_register():
    pass


@user.get('/userinfo', summary='查看用户信息')
async def get_userinfo(current_user: list = Depends(get_current_user)):
    pass


@user.get('/user_list', summary='用户列表')
async def get_user_list(current_user=Depends(jwt_security.get_current_is_superuser)):
    pass


@user.post('/user_super_set', summary='修改用户超级权限')
async def super_set(user_id: int, current_user=Depends(jwt_security.get_current_is_superuser), ):
    pass


@user.post('/user_action_set', summary='修改用户状态')
async def active_set(user_id: int, current_user=Depends(jwt_security.get_current_is_superuser), ):
    pass


@user.delete('/user_delete', summary='用户注销', description='用户注销 != 用户退出，注销之后用户将从数据库删除', )
async def user_delete(current_user=Depends(get_current_user)):
    pass
