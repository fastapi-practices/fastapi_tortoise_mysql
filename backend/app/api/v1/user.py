#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from fastapi import APIRouter, Request, Response, UploadFile

from backend.app.common.jwt import CurrentUser, DependsJwtUser
from backend.app.common.pagination import PageDepends, paging_data
from backend.app.common.response.response_schema import response_base
from backend.app.schemas.user import CreateUser, GetUserInfo, ResetPassword, UpdateUser
from backend.app.services.user_service import UserService

router = APIRouter()


@router.post('/register', summary='注册')
async def create_user(obj: CreateUser):
    await UserService.register(obj)
    return await response_base.success(msg='用户注册成功')


@router.post('/password/reset/code', summary='获取密码重置验证码', description='可以通过用户名或者邮箱重置密码')
async def password_reset_captcha(username_or_email: str, response: Response):
    await UserService.get_pwd_rest_captcha(username_or_email=username_or_email, response=response)
    return await response_base.success(msg='验证码发送成功')


@router.post('/password/reset', summary='密码重置请求')
async def password_reset(obj: ResetPassword, request: Request, response: Response):
    await UserService.pwd_reset(obj=obj, request=request, response=response)
    return await response_base.success(msg='密码重置成功')


@router.get('/password/reset/done', summary='重置密码完成')
async def password_reset_done():
    return await response_base.success(msg='重置密码完成')


@router.get('/{username}', summary='查看用户信息', dependencies=[DependsJwtUser])
async def get_user_info(username: str):
    current_user = await UserService.get_user_info(username)
    return await response_base.success(data=current_user, exclude={'password'})


@router.put('/{username}', summary='更新用户信息')
async def update_userinfo(username: str, obj: UpdateUser, current_user: CurrentUser):
    count = await UserService.update(username=username, current_user=current_user, obj=obj)
    if count > 0:
        return await response_base.success(msg='更新用户信息成功')
    return await response_base.fail()


@router.put('/{username}/avatar', summary='更新头像')
async def update_avatar(username: str, avatar: UploadFile, current_user: CurrentUser):
    count = await UserService.update_avatar(username=username, current_user=current_user, avatar=avatar)
    if count > 0:
        return await response_base.success(msg='更新头像成功')
    return await response_base.fail()


@router.delete('/{username}/avatar', summary='删除头像文件')
async def delete_avatar(username: str, current_user: CurrentUser):
    count = await UserService.delete_avatar(username=username, current_user=current_user)
    if count > 0:
        return await response_base.success(msg='删除用户头像成功')
    return await response_base.fail()


@router.get('', summary='获取所有用户', dependencies=[DependsJwtUser, PageDepends])
async def get_all_users():
    data = await UserService.get_user_list()
    page_data = await paging_data(data, GetUserInfo)
    return await response_base.success(data=page_data)


@router.post('/{pk}/super', summary='修改用户超级权限', dependencies=[DependsJwtUser])
async def super_set(pk: int):
    count = await UserService.update_permission(pk)
    if count > 0:
        return await response_base.success(msg='修改超级权限成功')
    return await response_base.fail()


@router.post('/{pk}/action', summary='修改用户状态', dependencies=[DependsJwtUser])
async def status_set(pk: int):
    count = await UserService.update_status(pk)
    if count > 0:
        return await response_base.success(msg='修改用户状态成功')
    return await response_base.fail()


@router.delete(
    '/{username}',
    summary='用户注销',
    description='用户注销 != 用户退出，注销之后用户将从数据库删除',
    dependencies=[DependsJwtUser],
)
async def delete_user(username: str, current_user: CurrentUser):
    count = await UserService.delete(username=username, current_user=current_user)
    if count > 0:
        return await response_base.success(msg='用户注销成功')
    return await response_base.fail()
