#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

# 获取项目根目录
# 或使用绝对路径，指到backend目录为止：BasePath = D:\git_project\FastAutoTest\backend
BASE_PATH = Path(__file__).resolve().parent.parent

# 日志文件路径
LOG_DIR = BASE_PATH / 'log'

# 静态资源目录
STATIC_DIR = BASE_PATH / 'static'
