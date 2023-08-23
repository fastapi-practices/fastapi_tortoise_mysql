#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import TypeVar, Generic, Type, Any, Dict

from asgiref.sync import sync_to_async
from pydantic import BaseModel
from tortoise import Model
from tortoise.queryset import QuerySet

ModelType = TypeVar('ModelType', bound=Model)
CreateSchemaType = TypeVar('CreateSchemaType', bound=BaseModel)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, pk: int) -> ModelType:
        return await self.model.filter(id=pk).first()

    async def get_or_none(self, pk: int) -> ModelType | None:
        return await self.model.get_or_none(id=pk)

    @sync_to_async
    def get_all(self) -> QuerySet[ModelType]:
        return self.model.all()

    async def get_values(self, pk: int, *args: str, **kwargs: str) -> list[dict] | dict:
        return await self.model.get(id=pk).values(*args, **kwargs)

    async def get_values_list(self, pk: int, *fields: str, flat: bool = False) -> list[Any] | tuple:
        return await self.model.get(id=pk).values_list(*fields, flat=flat)

    async def create(self, obj_in: CreateSchemaType, user_id: int | None = None) -> ModelType:
        if user_id:
            model = self.model(**obj_in.model_dump(), create_user=user_id)
            await model.save()
        else:
            model = await self.model.create(**obj_in.model_dump())
        return model

    async def update(
            self, pk: int, obj_in: UpdateSchemaType | Dict[str, Any], user_id: int | None = None
    ) -> int:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump()
        if user_id:
            update_data.update({'update_user': user_id})
        count = await self.model.filter(id=pk).update(**update_data)
        return count

    async def delete(self, pk: int) -> int:
        count = await self.model.filter(id=pk).delete()
        return count
