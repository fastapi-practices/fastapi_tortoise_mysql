#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import timezone

from backend.app.api import jwt_security
from backend.app.crud.base import CRUDBase
from backend.app.models.user import User
from backend.app.schemas.sm_user import CreateUser, UpdateUser


class CRUDUser(CRUDBase[User, CreateUser, UpdateUser]):
    async def get_user_by_id(self, pk: int) -> User:
        return await super().get(pk)

    async def get_user_by_username(self, name: str) -> User:
        return await self.model.filter(username=name).first()

    async def update_user_login_time(self, pk: int) -> int:
        return await self.model.filter(id=pk).update(last_login=timezone.now())

    async def check_email(self, email: str) -> bool:
        return await self.model.filter(email=email).exists()

    async def register_user(self, user: CreateUser) -> User:
        user.password = jwt_security.get_hash_password(user.password)
        user_obj = await super().create(user)
        return user_obj

    async def get_email_by_username(self, username: str) -> str:
        user = await self.model.filter(username=username).first()
        return user.email

    async def get_username_by_email(self, email: str) -> str:
        user = await self.model.filter(email=email).first()
        return user.username

    async def reset_password(self, username: str, password: str) -> None:
        new_pwd = jwt_security.get_hash_password(password)
        await self.model.filter(username=username).update(password=new_pwd)
        return

    async def update_userinfo(self, current_user: User, username: str, email: str, mobile_number: str, wechat: str,
                              qq: str, blog_address: str, introduction: str, avatar: str) -> User:
        new_info = {
            "username": username,
            "email": email,
            "mobile_number": mobile_number,
            "wechat": wechat,
            "qq": qq,
            "blog_address": blog_address,
            "introduction": introduction,
            "avatar": avatar
        }
        new_user = await super().update_one(current_user.pk, new_info)
        return new_user

    async def get_avatar_by_pk(self, pk: int):
        user = await super().get(pk)
        return user.avatar

    async def delete_avatar(self, pk: int) -> None:
        await self.model.filter(id=pk).update(avatar=None)
        return

    async def super_set(self, pk: int) -> None:
        super_status = await self.get_user_super_status(pk)
        if super_status:
            await self.model.filter(id=pk).update(is_superuser=False)
        else:
            await self.model.filter(id=pk).update(is_superuser=True)
        return

    async def get_user_super_status(self, pk: int) -> bool:
        user = await super().get(pk)
        return user.is_superuser

    async def active_set(self, pk: int) -> None:
        active_status = await self.get_user_active_status(pk)
        if active_status:
            await self.model.filter(id=pk).update(is_active=False)
        else:
            await self.model.filter(id=pk).update(is_active=True)
        return

    async def get_user_active_status(self, pk: int) -> bool:
        user = await super().get(pk)
        return user.is_active

    async def delete_user(self, pk: int) -> User:
        return await super().delete_one(pk)


UserDao = CRUDUser(User)
