#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from loguru import logger
from backend.app.core import path_conf


class Logger(object):

    @staticmethod
    def log():
        # 判定文件夹
        if not os.path.exists(path_conf.LogPath):
            os.mkdir(path_conf.LogPath)

        # 日志文件名称
        log_file = os.path.join(path_conf.LogPath, "FastAutoTest.log")

        # loguru日志
        logger.add(
            log_file,
            level="DEBUG",
            rotation='00:00',
            retention="7 days",
            encoding='utf-8',
            enqueue=True,
            backtrace=True,
            diagnose=True
        )

        return logger


log = Logger().log()
