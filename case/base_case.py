# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/25 9:12
# @Author   : zhe
# @FileName : base_case.py
# @Project  : PyCharm

import time
import os
import logging
import binascii
from datetime import datetime
from orm.orm import *
from socket_fun import Logger
from twisted.internet import defer

logger = Logger()


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
            if data[:2] != bytes().fromhex(self.startwith):
                return False
            if data[-2:] != bytes().fromhex(self.endwith):
                return False
        except:
            return False
        return True

    def test(self, data):
        try:
            if not self.pretreatment(data):
                return -1
            if data[3:4] != bytes().fromhex(self.number):
                return self.error['protocol']
            # self.data_list = data_tuple
            # self.data = data
            return 1
        except:
            return False

    def act(self, transport, data):
        pass

    def send_to_device(self, transport, msg, log=False):
        try:
            transport.transport.write(bytes().fromhex(msg))
            if log:
                log_str = '协议 %s 服务器回复消息成功\t内容 %s' % (self.number, msg)
                logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                                level=logging.INFO)
            return True
        except:
            log_str = '协议 %s 服务器回复消息失败\t内容 %s' % (self.number, msg)
            logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                            level=logging.WARNING)
            log_str = '协议 %s 服务器回复消息发生错误\t内容 %s \t设备 %s' \
                      % (self.number, msg, transport.dev_info['dev_id'])
            logger.error_log('error.log', log_str)
            return False


class ToSendCase():

    def __init__(self, number):
        self.number = number

    def test(self, data):
        try:
            if data[6:8] == self.number:
                # self.data = data
                return True
            else:
                return False
        except:
            return False

    def act(self, transport, id, data):
        if self.number == '00':
            log_str = '协议 %s 服务器发送未能理解的消息\t内容 %s' \
                      % (self.number, data)
            logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                            level=logging.WARNING)
        self.send_to_device(transport, id, data)

    def send_to_device(self, transport, id, data):
        try:
            transport.transport.write(bytes().fromhex(data))
            log_str = '协议 %s 服务器主动发送消息成功\t内容 %s ID %s' % (
                self.number, data, id)
            logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                            level=logging.INFO)
        except:
            log_str = '协议 %s 服务器回复消息失败\t内容 %s ID %s' \
                      % (self.number, data, id)
            logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                            level=logging.WARNING)
            log_str = '协议 %s 服务器发主动送消息错误\t内容 %s ID%s\t设备 %s' \
                      % (
                      self.number, data, id, transport.dev_info['dev_id'])
            logger.error_log('error.log', log_str)
        session = DBSession()
        try:
            msg = session.query(ToSendModel).filter(
                ToSendModel.id == id).first()
            msg.status = 1
            msg.sent_at = datetime.now()
            session.commit()
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' \
                      % (transport.dev_info['dev_id'])
            logger.error_log('error.log', log_str)
        finally:
            session.close()


class LoginCase(BaseCase):

    def login_success(self, dev, transport):
        dev_info = {
            'dev_id': dev.dev_id,
            'name': dev.name,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        transport.dev_info = dev_info
        send_msg = self.startwith + '0101' + self.endwith
        if self.send_to_device(transport, send_msg):
            session = DBSession()
            try:
                location = session.query(LocationCard).filter(
                    LocationCard.dev_id == dev.dev_id).first()
                location.connect = 1
                location.last_time = datetime.now()
                session.commit()
            except:
                session.rollback()
                log_str = '数据库错误\t设备 %s' \
                          % (transport.dev_info['dev_id'])
                logger.error_log('error.log', log_str)
            finally:
                session.close()

            (host, port) = transport.transport.client
            log_str = '设备 %s 登录成功 地址 %s:%s' % (dev.dev_id, host, port)
            logger.info_log('login.log', log_str, level=logging.INFO)
            logger.info_log(dev.dev_id + '.log', log_str, level=logging.INFO)
            return True
        return False

    def login_failure(self, dev_id, transport):
        send_msg = self.startwith + '0144' + self.endwith
        self.send_to_device(transport, send_msg)
        (host, port) = transport.transport.client
        log_str = '设备 %s 登录失败 地址 %s:%s' % (dev_id, host, port)
        logger.info_log('login.log', log_str, level=logging.WARNING)
        return False

    def check_dev(self, data):
        dev_str = str(binascii.b2a_hex(data[4:-3]))[2:-1]
        session = DBSession()
        try:
            dev = session.query(EmployeeInfoCard).filter(
                EmployeeInfoCard.dev_id == dev_str).first()
            if dev:
                return (True, dev)
            else:
                return (False, dev_str)
        except:
            log_str = '数据库错误\t设备 %s' % dev_str
            logger.error_log('error.log', log_str)
            return (False, dev_str)
        finally:
            session.close()

    def act(self, transport, data):
        dev_checked = self.check_dev(data)
        if dev_checked[0]:
            return self.login_success(dev_checked[1], transport)
        else:
            return self.login_failure(dev_checked[1], transport)


class ToSendMsgNoNumber(ToSendCase):

    def test(self, data):
        # self.data = data
        return True
