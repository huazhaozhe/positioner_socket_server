# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/25 9:12
# @Author   : zhe
# @FileName : base_case.py
# @Project  : PyCharm

import time
import os
import logging
from datetime import datetime
from orm.orm import *
from socket_fun import write_logger

session = DBSession()


def bytes_to_dec(value):
    '''
    :param value:数组或者元组,不能是字符串
    :return: 十进制整数
    如将[0xee, 0xff, 0x05, 0x12],也就是[238, 255, 5, 18]
    转换为0xeeff0512的十进制4009690386
    每个元素对应一个字节,每个元素最大0xff
    '''
    value_str = ''.join(
        map(
            lambda x: hex(x)[2:]
            if len(hex(x)[2:]) == 2 else '0' + hex(x)[2:], value
        )
    )
    return int(value_str, 16)


class BaseCase():

    def __init__(self, number, length, startwith, endwith):
        self.startwith = startwith
        self.endwith = endwith
        self.number = number
        self.length = length
        self.error = {
            'protocol': False,
        }

    def pretreatment(self, data):
        try:
            if (data[0], data[1]) != self.startwith:
                return False
            if (data[-2], data[-1]) != self.endwith:
                return False
        except:
            return False
        return True

    def test(self, data_tuple, data):
        try:
            if not self.pretreatment(data_tuple):
                return 0
            if data_tuple[3] != self.number:
                return self.error['protocol']
            self.data_list = data_tuple
            self.data = data
            return True
        except:
            return False

    def act(self, transport):
        pass


class ToSendCase():

    def __init__(self, number):
        self.number = number

    def test(self, data):
        try:
            if int(data[6:8], 16) == self.number:
                self.data = data
                return True
            else:
                return False
        except:
            return False

    def act(self, transport, id):
        self.send_to_device(transport, id)
        if self.number == 0x00:
            log_str = '协议:%s服务器发送未能理解的消息 内容:%s' \
                      % (hex(self.number), self.data)
        else:
            log_str = '协议:%s服务器主动发送消息 内容:%s' \
                      % (hex(self.number), self.data)
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

    def send_to_device(self, transport, id):
        try:
            transport.transport.write(bytes().fromhex(self.data))
            msg = session.query(ToSendModel).filter(ToSendModel.id == id).all()
            if len(msg) > 1:
                return False
            elif len(msg) == 1:
                msg = msg[0]
                msg.status = 1
                msg.sent_at = datetime.now()
                session.commit()
                return True
            else:
                return False
        except:
            return False


class LoginCase(BaseCase):

    def login_success(self, dev, transport):
        send_msg = ''.join(map(chr, self.startwith)) + chr(
            0x01) + chr(0x01) + ''.join(map(chr, self.endwith))
        dev_info = {
            'dev_id': dev.dev_id,
            'name': dev.name,
            'login_status': 1,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        transport.dev_info = dev_info
        location = session.query(LocationCard).filter(
            LocationCard.dev_id == dev.dev_id).first()
        location.connect = 1
        session.commit()
        (host, port) = transport.transport.client
        log_str = '设备 %s 登录成功 地址 %s:%s' \
                  % (dev.dev_id, host, port)
        write_logger('login.log', log_str, level=logging.INFO)
        write_logger(dev.dev_id + '.log', log_str, level=logging.INFO)
        transport.transport.write(send_msg.encode())
        return True

    def login_failure(self, dev_str, transport):
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x01) + chr(
            0x44) + ''.join(map(chr, self.endwith))
        transport.transport.write(send_msg.encode())
        transport.transport.loseConnection()
        write_logger('login.log', '设备 ' + dev_str + ' 登录失败',
                     level=logging.INFO)
        return False

    def check_dev(self):
        dev_str = ''
        for i in self.data_list[4:4 + 8]:
            dev_str += hex(i)[2:] if len(hex(i)[2:]) > 1 else '0' + hex(i)[2:]
        dev = session.query(EmployeeInfoCard).filter(
            EmployeeInfoCard.dev_id == dev_str).all()
        if len(dev) > 1:
            pass
            # raise
        elif len(dev) == 1 and dev[0].dev_id == dev_str:
            return (True, dev[0])
        else:
            return (False, dev_str)

    def act(self, transport):
        dev_checked = self.check_dev()
        if dev_checked[0]:
            return self.login_success(dev_checked[1], transport)
        else:
            return self.login_failure(dev_checked[1], transport)


class ToSendMsgNoNumber(ToSendCase):

    def test(self):
        return True