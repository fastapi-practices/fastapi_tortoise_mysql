#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from pathlib import Path

# 获取项目根目录
# 或使用绝对路径，指到backend目录为止：BasePath = D:\git_project\FastAutoTest\backend
BasePath = Path(__file__).resolve().parent.parent

# 日志文件路径
LOG_DIR = os.path.join(BasePath, 'log')

# 挂载静态目录
STATIC_DIR = os.path.join(BasePath, 'static')
