#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request, Response, UploadFile

from backend.app.admin.schema.user import CreateUser, ResetPassword, UpdateUser
from backend.app.admin.service.user_service import UserService
from backend.common.pagination import DependsPagination, paging_data
from backend.common.response.response_schema import response_base
from backend.common.security.jwt import CurrentUser, DependsJwtAuth

router = APIRouter()


@router.post('/register', summary='注册')
async def create_user(obj: CreateUser):
    await UserService.register(obj)
    return response_base.success()


@router.post('/password/reset/code', summary='获取密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_captcha(username_or_email: str, response: Response):
    await UserService.get_pwd_rest_captcha(username_or_email=username_or_email, response=response)
    return response_base.success()


@router.post('/password/reset', summary='密码重置请求')
async def password_reset(obj: ResetPassword, request: Request, response: Response):
    await UserService.pwd_reset(obj=obj, request=request, response=response)
    return response_base.success()


@router.get('/password/reset/done', summary='重置密码完成')
async def password_reset_done():
    return response_base.success()


@router.get('/{username}', summary='查看用户信息', dependencies=[DependsJwtAuth])
async def get_user_info(username: str):
    current_user = await UserService.get_user_info(username)
    return response_base.success(data=current_user, exclude={'password'})


@router.put('/{username}', summary='更新用户信息')
async def update_userinfo(username: str, obj: UpdateUser, current_user: CurrentUser):
    count = await UserService.update(username=username, current_user=current_user, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.put('/{username}/avatar', summary='更新头像')
async def update_avatar(username: str, avatar: UploadFile, current_user: CurrentUser):
    count = await UserService.update_avatar(username=username, avatar=avatar)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete('/{username}/avatar', summary='删除头像文件')
async def delete_avatar(username: str, current_user: CurrentUser):
    count = await UserService.delete_avatar(username=username, current_user=current_user)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.get('', summary='获取所有用户', dependencies=[DependsJwtAuth, DependsPagination])
async def get_all_users():
    data = await UserService.get_list()
    page_data = await paging_data(data)
    return response_base.success(data=page_data)


@router.post('/{pk}/super', summary='修改用户超级权限', dependencies=[DependsJwtAuth])
async def super_set(pk: int):
    count = await UserService.update_permission(pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.post('/{pk}/action', summary='修改用户状态', dependencies=[DependsJwtAuth])
async def status_set(pk: int):
    count = await UserService.update_status(pk)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/{username}',
    summary='用户注销',
    description='用户注销 != 用户退出，注销之后用户将从数据库删除',
    dependencies=[DependsJwtAuth],
)
async def delete_user(username: str, current_user: CurrentUser):
    count = await UserService.delete(username=username, current_user=current_user)
    if count > 0:
        return response_base.success()
    return response_base.fail()
