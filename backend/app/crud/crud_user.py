#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import timezone

from backend.app.api import jwt
from backend.app.crud.base import CRUDBase
from backend.app.models.user import User
from backend.app.schemas.user import CreateUser, UpdateUser


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    async def get_user_by_id(self, pk: int) -> User:
        return await self.get(pk)

    async def get_user_by_username(self, name: str) -> User:
        return await self.model.filter(username=name).first()

    async def update_user_login_time(self, pk: int) -> int:
        return await self.model.filter(id=pk).update(last_login=timezone.now())

    async def check_email(self, email: str) -> bool:
        return await self.model.filter(email=email).exists()

    async def register_user(self, user: CreateUser) -> User:
        user.password = jwt.get_hash_password(user.password)
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

    async def reset_password(self, username: str, password: str) -> int:
        new_pwd = jwt.get_hash_password(password)
        return await self.model.filter(username=username).update(password=new_pwd)

    async def update_userinfo(self, current_user: User, obj_in: UpdateUser) -> int:
        return await self.update(current_user.pk, obj_in)

    async def update_avatar(self, current_user: User, avatar: str):
        return await self.update(current_user.pk, {'avatar': avatar})

    async def get_avatar_by_pk(self, pk: int):
        user = await self.get(pk)
        return user.avatar

    async def delete_avatar(self, pk: int) -> int:
        return await self.model.filter(id=pk).update(avatar=None)

    async def super_set(self, pk: int) -> int:
        super_status = await self.get_user_super_status(pk)
        return await self.model.filter(id=pk).update(is_superuser=False if super_status else True)

    async def get_user_super_status(self, pk: int) -> bool:
        user = await self.get(pk)
        return user.is_superuser

    async def active_set(self, pk: int) -> int:
        active_status = await self.get_user_active_status(pk)
        return await self.model.filter(id=pk).update(is_active=False if active_status else True)

    async def get_user_active_status(self, pk: int) -> bool:
        user = await self.get(pk)
        return user.is_active

    async def delete_user(self, pk: int) -> int:
        return await self.delete(pk)


UserDao = CRUDUser(User)
