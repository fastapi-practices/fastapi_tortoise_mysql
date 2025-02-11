#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import bcrypt

from tortoise.transactions import atomic

from backend.app.admin.model.user import User
from backend.app.admin.schema.user import Avatar, CreateUser, UpdateUser
from backend.common.crud import CRUDBase
from backend.common.security.jwt import get_hash_password


class CRUDUser(CRUDBase[User]):
    async def get_by_id(self, pk: int) -> User:
        return await self.get(pk)

    async def get_by_username(self, name: str) -> User:
        return await self.model.filter(username=name).first()

    @atomic()
    async def update_login_time(self, username: str, login_time: datetime) -> int:
        return await self.model.filter(username=username).update(last_login_time=login_time)

    async def check_email(self, email: str) -> bool:
        return await self.model.filter(email=email).exists()

    @atomic()
    async def register(self, obj: CreateUser) -> None:
        salt = bcrypt.gensalt()
        obj.password = get_hash_password(obj.password, salt)
        dict_obj = obj.model_dump()
        dict_obj.update({'salt': salt})
        new_user = self.model(**dict_obj)
        await new_user.save()

    @atomic()
    async def reset_password(self, pk: int, new_pwd: str) -> int:
        return await self.model.filter(id=pk).update(password=new_pwd)

    @atomic()
    async def update_userinfo(self, input_user: int, obj_in: UpdateUser) -> int:
        return await self.update(input_user, obj_in)

    @atomic()
    async def update_avatar(self, input_user: int, avatar: Avatar):
        return await self.update(input_user, {'avatar': avatar.url})

    @atomic()
    async def delete_avatar(self, pk: int) -> int:
        return await self.model.filter(id=pk).update(avatar=None)

    @atomic()
    async def delete_user(self, pk: int) -> int:
        return await self.delete(pk)


user_dao: CRUDUser = CRUDUser(User)
