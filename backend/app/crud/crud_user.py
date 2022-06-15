#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from tortoise import timezone

from backend.app.api import jwt_security
from backend.app.crud.base import CRUDBase
from backend.app.models.user import User
from backend.app.schemas.sm_user import CreateUser, UpdateUser


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
        user.password = jwt_security.get_hash_password(user.password)
        user_obj = await self.create(user)
        return user_obj


UserDao = CRUDUser(User)
