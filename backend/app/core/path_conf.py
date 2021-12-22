#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

# 获取项目根目录
# 或使用绝对路径，指到backend目录为止：BasePath = D:\git_project\FastAutoTest\backend
BasePath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 日志文件路径
LogPath = os.path.join(BasePath, 'app', 'log')
