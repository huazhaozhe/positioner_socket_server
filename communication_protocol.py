# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 13:09
# @Author   : zhe
# @FileName : data_structure.py
# @Project  : PyCharm

import time
from orm import *

startwith = (0x78, 0x78)
endwith = (0x0d, 0x0a)

client = []
session = DBSession()


class BaseCase():
    def __init__(self, startwith, endwith):
        self.startwith = startwith
        self.endwith = endwith

    def pretreatment(self, data_list):
        try:
            if (data_list[0], data_list[1]) != self.startwith:
                return False
            if (data_list[-2], data_list[-1]) != self.endwith:
                return False
        except:
            return False
        return True


class LoginCase(BaseCase):

    def __init__(self, number, length):
        super(LoginCase, self).__init__(startwith, endwith)
        self.number = number
        self.length = length
        self.error = {
            'protocol': False,
        }

    def test(self, data):
        self.data_list = list(data)
        print('data_list', self.data_list)
        if not self.pretreatment(self.data_list):
            print('预处理失败')
            return False
        if self.data_list[3] != self.number:
            print('不是这个操作')
            return self.error['protocol']
        return True

    def login_success(self, dev_str):
        send_msg = chr(self.startwith[0]) + chr(self.startwith[1]) + chr(
            0x01) + chr(self.endwith[0]) + chr(self.endwith[1])
        print('%s 登录成功' % dev_str)
        self.transport.transport.write(send_msg.encode())
        dev_info = {
            'id': dev_str,
            'login_status': 1,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        self.transport.dev_info = dev_info
        client.append(self.transport)
        return True

    def login_failure(self, dev_str):
        print('%s 登录失败' % dev_str)
        send_msg = chr(self.startwith[0]) + chr(self.startwith[1]) + chr(
            0x44) + chr(self.endwith[0]) + chr(self.endwith[1])
        self.transport.transport.write(send_msg.encode())
        self.transport.transport.loseConnection()
        return True

    def check_dev(self):
        dev_str = ''
        for i in self.data_list[4:4 + 8]:
            dev_str += hex(i)[2:] if len(hex(i)[2:]) == 2 else '0' + hex(i)[2:]
        dev = session.query(EmployeeInfoCard).filter(
            EmployeeInfoCard.dev_id == dev_str).all()
        if len(dev) > 1:
            raise
        elif len(dev) == 1 and dev[0].dev_id == dev_str:
            return (True, dev_str)
        else:
            return (False, dev_str)

    def act(self, transport):
        self.transport = transport
        dev = self.check_dev()
        if dev[0]:
            self.login_success(dev[1])
        else:
            self.login_failure(dev[1])


class Handler():
    logincase = LoginCase(number=0x01, length=0x0a)
    Case = []

    def handler(self, data, transport):
        if transport in client:
            for case in self.Case:
                if case.test(data):
                    case.act(transport)
                    break
        else:
            if self.logincase.test(data):
                self.logincase.act(transport)