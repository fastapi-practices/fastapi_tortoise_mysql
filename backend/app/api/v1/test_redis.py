#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter

from backend.app.common.redis import redis_client
from backend.app.common.response.response_schema import response_base

redis = APIRouter()


@redis.post('')
async def test_redis():
    result = await redis_client.set('test', 'test')
    if result:
        return response_base.response_200(data=result)


@redis.get('')
async def get_redis():
    result = await redis_client.get('test')
    if result:
        return response_base.response_200(data=result)


@redis.delete('')
async def test_redis():
    result = await redis_client.delete('test')
    if result:
        return response_base.response_200(data=result)
