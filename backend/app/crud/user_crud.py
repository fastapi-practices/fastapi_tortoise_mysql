#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from backend.app.api import jwt_security
from backend.app.models.user import User, User_Pydantic


async def get_user_by_id(pk: int) -> User:
    return await User.filter(id=pk).first()


async def get_user_by_username(name: str) -> User:
    return await User.filter(username=name).first()


async def register_user(user):
    user.password = jwt_security.get_hash_password(user.password)
    user_obj = await User.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)
