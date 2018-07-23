# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 8:52
# @Author   : zhe
# @FileName : client_socket.py
# @Project  : PyCharm

import socket
import struct

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

host = '192.168.16.70'
port = 10086
client_socket.connect((host, port))
accept = client_socket.recv(10240)
print(accept.decode())

# while True:
#     send_msg = input('输入发送的信息, 输入exit退出:')
#     client_socket.send(send_msg.encode())
#     # print(client_socket.recv(10240).decode())
#     if send_msg == 'exit':
#         break

login_struct = struct.Struct('BBBBBBBBBBBBBBB')
value = (0x78, 0x78, 0x0a, 0x01, b'0123456789012345', 0x01,0x0d,0x0a)
packed = login_struct.pack(*value)
client_socket.send(packed)


client_socket.close()
print('客户端关闭连接')