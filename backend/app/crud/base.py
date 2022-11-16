#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import TypeVar, Generic, Type, Optional, List, Union, Any, Dict

from pydantic import BaseModel
from tortoise import Model

ModelType = TypeVar('ModelType', bound=Model)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, pk: int) -> ModelType:
        return await self.model.filter(id=pk).first()

    async def get_or_none(self, pk: int) -> Optional[ModelType]:
        return await self.model.get_or_none(id=pk)

    async def get_all(self) -> List[ModelType]:
        return await self.model.all()

    async def get_values(self, pk: int, *args: str, **kwargs: str) -> Union[List[dict], dict]:
        return await self.model.get(id=pk).values(*args, **kwargs)

    async def get_values_list(self, pk: int, *fields: str, flat: bool = False) -> Union[List[Any], tuple]:
        return await self.model.get(id=pk).values_list(*fields, flat=flat)

    async def create(self, obj_in: CreateSchemaType, user_id: Optional[int] = None) -> ModelType:
        if user_id:
            model = self.model(**obj_in.dict(), create_user=user_id)
            await model.save()
        else:
            model = await self.model.create(**obj_in.dict())
        return model

    async def update(
            self, pk: int, obj_in: Union[UpdateSchemaType, Dict[str, Any]], user_id: Optional[int] = None
    ) -> int:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict()
        if user_id:
            update_data.update({'update_user': user_id})
        count = await self.model.filter(id=pk).update(**update_data)
        return count

    async def delete(self, pk: int) -> int:
        count = await self.model.filter(id=pk).delete()
        return count
