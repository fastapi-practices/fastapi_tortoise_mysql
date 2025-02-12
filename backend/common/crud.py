#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel
from tortoise import Model

ModelT = TypeVar('ModelT', bound=Model)
CreateSchemaT = TypeVar('CreateSchemaT', bound=BaseModel)
UpdateSchemaT = TypeVar('UpdateSchemaT', bound=BaseModel)


class CRUDBase(Generic[ModelT]):
    def __init__(self, model: Type[ModelT]):
        self.model = model

    async def get(self, pk: int) -> ModelT:
        return await self.model.filter(id=pk).first()

    async def get_or_none(self, pk: int) -> ModelT | None:
        return await self.model.get_or_none(id=pk)

    async def get_all(self) -> list[Type[ModelT]]:
        return await self.model.all().order_by('-id')

    async def get_values(self, pk: int, *args: str, **kwargs: str) -> list[dict[str, Any]] | dict[str, Any]:
        return await self.model.get(id=pk).values(*args, **kwargs)

    async def get_values_list(self, pk: int, *fields: str, flat: bool = False) -> list[Any] | tuple:
        return await self.model.get(id=pk).values_list(*fields, flat=flat)

    async def create_model(self, obj_in: CreateSchemaT, **kwargs) -> ModelT:
        if kwargs:
            model = self.model(**obj_in.model_dump(), **kwargs)
            await model.save()
        else:
            model = await self.model.create(**obj_in.model_dump())
        await model.save()
        return model

    async def update_model(self, pk: int, obj_in: UpdateSchemaT | Dict[str, Any], **kwargs) -> int:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump()
        if kwargs:
            update_data.update(**kwargs)
        count = await self.model.filter(id=pk).update(**update_data)
        return count

    async def delete_model(self, pk: int) -> int:
        count = await self.model.filter(id=pk).delete()
        return count
