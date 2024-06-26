#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from pathlib import Path

# 获取项目根目录
# 或使用绝对路径，指到backend目录为止：BasePath = D:\git_project\FastAutoTest\backend
BasePath = Path(__file__).resolve().parent.parent

# 日志文件路径
LogPath = os.path.join(BasePath, 'log')

# 图片上传存放路径: /static/media/uploads/
ImgPath = os.path.join(BasePath, 'static', 'media', 'uploads')

# 头像上传存放路径: /static/media/uploads/avatars/
AvatarPath = os.path.join(ImgPath, 'avatars', '')
