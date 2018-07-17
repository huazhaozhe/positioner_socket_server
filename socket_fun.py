# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 9:35
# @Author   : zhe
# @FileName : socket_fun.py
# @Project  : PyCharm

import time
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


def tcplink(sock, addr):
    print('新的客户端连接: %s:%s...' % addr)
    sock.send(('%s:%s OK' %addr).encode())
    while True:
        data = sock.recv(10240)
        send_msg = data.decode() + '\n%s' % time.strftime('%Y-%m-%d %H:%M:%S')
        sock.send(send_msg.encode())
        if not data or data == 'exit':
            break
    sock.close()
    print('客户端 %s:%s 连接断开' % addr)