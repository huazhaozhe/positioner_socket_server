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


logger = logging.getLogger('logger')
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')


def write_logger(file_name, info, level=logging.INFO, log_debug=False):
    logger.setLevel(level)
    if DEBUG or log_debug:
        fh = logging.StreamHandler()
    else:
        log_path = os.path.join(log_dir, file_name)
        fh = logging.FileHandler(log_path, encoding='utf-8')
    # fh.setLevel(level)
    fh.setFormatter(log_formatter)
    logger.addHandler(fh)
    logger.log(msg=info, level=level)
    logger.removeHandler(fh)
