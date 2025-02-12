#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime

import bcrypt
from tortoise.queryset import QuerySet
from tortoise.expressions import Q
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
        return await self.update_model(input_user, obj_in)

    @atomic()
    async def update_avatar(self, input_user: int, avatar: Avatar) -> int:
        return await self.update_model(input_user, {'avatar': avatar.url})

    async def get_list(self, username: str = None, phone: str = None, status: int = None) -> QuerySet:
        where_list = []
        if username:
            where_list.append(Q(username=username))
        if phone:
            where_list.append(Q(phone=phone))
        if status:
            where_list.append(Q(status=status))
        return self.model.filter(Q(*where_list)).order_by('-id').all()

    @atomic()
    async def delete(self, pk: int) -> int:
        return await self.delete_model(pk)


user_dao: CRUDUser = CRUDUser(User)
