# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 9:35
# @Author   : zhe
# @FileName : socket_fun.py
# @Project  : PyCharm


import time
import socket
from orm import Message


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


def tcplink(sock, addr, db_session):
    print('新的客户端连接: %s:%s...' % addr)
    sock.send(('%s:%s OK' % addr).encode())
    id = '0'
    while True:
        try:
            data = sock.recv(10240)
        except sock.error:
            print('socket连接错误')
            sock.close()
            break
        try:
            if id == '0' and data.decode()[0] == '#' and data.decode()[
                -1] == '#':
                id = data.decode()[1:-1]
                message = id + ' connected'
                new_msg = Message(message=message)
            elif id != '0':
                new_msg = Message(message=id + data.decode())
            else:
                print('数据格式错误')
                continue
        except:
            continue
        db_session.add(new_msg)
        db_session.commit()
        sock.send('accept'.encode())


    sock.close()
    print('客户端 %s:%s 连接断开' % addr)
