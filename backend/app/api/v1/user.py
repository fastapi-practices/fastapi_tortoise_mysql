#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.crud.user_crud import register
from backend.app.models.user import UserIn_Pydantic
from backend.app.schemas import Response200

user = APIRouter()


@user.post('/login', summary='登录')
async def login():
    pass


@user.post('/register', summary='注册test', response_model=Response200)
async def create_user(post: UserIn_Pydantic):
    data = await register(post)
    return Response200(msg='success', data={
        'username': data.username,
        'password': data.password
    })
