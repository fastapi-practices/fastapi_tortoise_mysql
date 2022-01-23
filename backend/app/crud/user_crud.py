#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from backend.app.models.user import User, User_Pydantic


async def register(user):
    user_obj = await User.create(**user.dict(exclude_unset=True))
    return await User_Pydantic.from_tortoise_orm(user_obj)
