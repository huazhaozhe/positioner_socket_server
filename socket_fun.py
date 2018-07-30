# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 9:35
# @Author   : zhe
# @FileName : socket_fun.py
# @Project  : PyCharm


import time
import os
import logging
import socket
from config import DEBUG, LOG_DIR as log_dir
from logging.handlers import RotatingFileHandler


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


class Logger():

    def __init__(self, log_dir=log_dir, maxBytes=100 * 1024 * 1024,
                 backupCount=5):
        self.log_formatter = logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s')
        self.logger = logging.getLogger('logger')
        self.DEBUG = DEBUG
        self.log_dir = log_dir
        self.maxBytes = maxBytes
        self.backupCount = backupCount

    def info_log(self, file_name, info, level=logging.INFO):
        log_path = os.path.join(self.log_dir, file_name)
        self.logger.setLevel(level)
        rthandler = RotatingFileHandler(log_path, maxBytes=self.maxBytes,
                                        backupCount=self.backupCount,
                                        encoding='utf-8')
        rthandler.setFormatter(self.log_formatter)
        self.logger.addHandler(rthandler)
        self.logger.log(msg=info, level=level)
        self.logger.removeHandler(rthandler)

    def error_log(self, file_name, info):
        log_path = os.path.join(self.log_dir, file_name)
        rthandler = RotatingFileHandler(log_path, maxBytes=self.maxBytes,
                                        backupCount=self.backupCount,
                                        encoding='utf-8')
        rthandler.setFormatter(
            logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
        self.logger = logging.getLogger('logger')
        self.logger.addHandler(rthandler)
        self.logger.exception(info)
        self.logger.removeHandler(rthandler)

    def std_log(self, info, level=logging.INFO):
        fh = logging.StreamHandler()
        fh.setFormatter(self.log_formatter)
        self.logger.setLevel(level)
        self.logger.addHandler(fh)
        self.logger.log(msg=info, level=level)
        self.logger.removeHandler(fh)
