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
accept = client_socket.recv(10240)
print(accept.decode())

while True:
    send_msg = input('输入发送的信息:')
    client_socket.send(send_msg.encode())
    print(client_socket.recv(10240).decode())
    if send_msg == 'exit':
        break

client_socket.close()
print('客户端关闭连接')