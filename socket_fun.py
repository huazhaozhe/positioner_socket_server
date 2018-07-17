# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 9:35
# @Author   : zhe
# @FileName : socket_fun.py
# @Project  : PyCharm

import socket

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