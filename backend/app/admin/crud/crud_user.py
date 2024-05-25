#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import timezone
from tortoise.transactions import atomic

from backend.app.admin.crud.base import CRUDBase
from backend.app.admin.models.user import User
from backend.app.admin.schemas.user import CreateUser, UpdateUser
from backend.common import jwt


class CRUDUser(CRUDBase[User]):
    async def get_user_by_id(self, pk: int) -> User:
        return await self.get(pk)

    async def get_user_by_username(self, name: str) -> User:
        return await self.model.filter(username=name).first()

    @atomic()
    async def update_user_login_time(self, pk: int) -> int:
        return await self.model.filter(id=pk).update(last_login_time=timezone.now())

    async def check_email(self, email: str) -> bool:
        return await self.model.filter(email=email).exists()

    @atomic()
    async def register_user(self, user: CreateUser) -> User:
        user.password = await jwt.get_hash_password(user.password)
        user = await self.create(user)
        return user

    async def get_email_by_username(self, username: str) -> str:
        user = await self.model.filter(username=username).first()
        return user.email

    async def get_username_by_email(self, email: str) -> str:
        user = await self.model.filter(email=email).first()
        return user.username

    async def get_avatar_by_username(self, username: str) -> str:
        user = await self.get_user_by_username(username)
        return user.avatar

    @atomic()
    async def reset_password(self, username: str, password: str) -> int:
        new_password = await jwt.get_hash_password(password)
        return await self.model.filter(username=username).update(password=new_password)

    @atomic()
    async def update_userinfo(self, current_user: User, obj_in: UpdateUser) -> int:
        return await self.update(current_user.pk, obj_in)

    @atomic()
    async def update_avatar(self, current_user: User, avatar: str):
        return await self.update(current_user.pk, {'avatar': avatar})

    async def get_avatar_by_pk(self, pk: int):
        user = await self.get(pk)
        return user.avatar

    @atomic()
    async def delete_avatar(self, pk: int) -> int:
        return await self.model.filter(id=pk).update(avatar=None)

    async def get_user_super_status(self, pk: int) -> bool:
        user = await self.get(pk)
        return user.is_superuser

    async def get_user_active_status(self, pk: int) -> bool:
        user = await self.get(pk)
        return user.status

    @atomic()
    async def super_set(self, pk: int) -> int:
        super_status = await self.get_user_super_status(pk)
        return await self.model.filter(id=pk).update(is_superuser=False if super_status else True)

    @atomic()
    async def status_set(self, pk: int) -> int:
        status = await self.get_user_active_status(pk)
        return await self.model.filter(id=pk).update(status=False if status else True)

    @atomic()
    async def delete_user(self, pk: int) -> int:
        return await self.delete(pk)


UserDao: CRUDUser = CRUDUser(User)
