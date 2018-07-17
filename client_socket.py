# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 8:52
# @Author   : zhe
# @FileName : client_socket.py
# @Project  : PyCharm

import socket
import sys
from socket_fun import get_host_ip

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = get_host_ip()
port = 10086
client_socket.connect((host, port))

msg = client_socket.recv(1024)
client_socket.close()
print(msg.decode())
