#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import transactions

from backend.app.api import jwt_security
from backend.app.models.user import User, User_Pydantic, UserIn_Pydantic


async def get_user_by_id(pk: int) -> User:
    return await User.filter(id=pk).first()


async def get_user_by_username(name: str) -> User:
    return await User.filter(username=name).first()


async def check_email(email: str) -> bool:
    return await User.filter(email=email).exists()


@transactions.atomic
async def register_user(user: UserIn_Pydantic) -> User:
    user.password = jwt_security.get_hash_password(user.password)
    user_obj = await User.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)
