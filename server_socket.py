# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 8:37
# @Author   : zhe
# @FileName : socket.py
# @Project  : PyCharm


import os, sys, time
import socket
from socket_fun import get_host_ip

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = get_host_ip()
port = 10086

server_socket.bind((host, port))
server_socket.listen(5)
print('server_socket run at %s:%s' % (host, port))

while True:
    client_socket, addr = server_socket.accept()
    print('客户端连接地址: %s' % str(addr))
    msg = 'IP %s 已连接服务端' % str(addr)
    client_socket.send(msg.encode())
    client_socket.close()
    time.sleep(0.5)

