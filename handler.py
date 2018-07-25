# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 13:09
# @Author   : zhe
# @FileName : data_structure.py
# @Project  : PyCharm


from case import *

DEBUG = True

startwith = (0x78, 0x78)
endwith = (0x0d, 0x0a)

login_case = LoginCase(number=0x01, length=0x0a, startwith=startwith,
                       endwith=endwith)
case = [
    HeartBeat(number=0x08, length=0x01, startwith=startwith,
              endwith=endwith),
    GpsPositioning(number=0x10, length=0x12, startwith=startwith,
                   endwith=endwith),
    DeviceStatus(number=0x13, length=0x06, startwith=startwith,
                 endwith=endwith),
    FactoryReset(number=0x15, length=0x01, startwith=startwith,
                 endwith=endwith),
    DeviceTimeUpdate(number=0x30, length=0x01, startwith=startwith,
                     endwith=endwith),
    WifiPositioning(number=0x69, startwith=startwith, endwith=endwith),
]

to_send_case = [
    RebootDevice(number=0x48, length=0x01, startwith=startwith,
                 endwith=endwith),
]


class Handler():

    def __init__(self, startwith=startwith, endwith=endwith):
        self.startwith = startwith
        self.endwith = endwith
        self.login_client = []
        self.to_send_enable = 0

    def add_case(self, login_case=login_case, case=case):
        self.login_case = login_case
        self.case = case

    def handler(self, data, transport):
        data_tuple = tuple(data)

        if transport in self.login_client:
            transport.dev_info['last_time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S')
            print('在 %s 收到设备的消息: %s\n字符串: %s\n元组: %s\n' % (
                transport.dev_info['last_time'],
                transport.dev_info['dev_id'], data, data_tuple))
            for case in self.case:
                if case.test(data_tuple, data):
                    case.act(transport)
                    break
            return True
        elif self.login_case.test(data_tuple, data):
            if self.login_case.act(transport):
                self.login_client.append(transport)
                if self.to_send_enable and transport.dev_info[
                    'dev_id'] in self.msg_dict:
                    self.to_send_device(transport)
                return True
        elif DEBUG and transport not in self.login_client:
            dev = session.query(EmployeeInfoCard).filter(
                EmployeeInfoCard.dev_id == '0123456789012345').one()
            self.login_case.login_success(dev, transport)
            self.login_client.append(transport)
            if self.to_send_enable and transport.dev_info[
                'dev_id'] in self.msg_dict:
                self.to_send_device(transport)
            return True

        transport.transport.loseConnection()
        # transport.transport.abortConnection()

    def to_send_init(self):
        msg_list = session.query(ToSendModel).filter(
            ToSendModel.status == 0).all()
        msg_dict = {}
        for msg in msg_list:
            if msg.dev_id not in msg_dict:
                msg_dict[msg.dev_id] = []
            msg_dict[msg.dev_id].append((msg.id, msg.msg))
        self.to_send_enable = 1
        self.msg_dict = msg_dict
        self.to_send_case = to_send_case
        print('原始msg_dict', msg_dict)
        return msg_dict

    def to_send_device(self, transport):
        for id, msg in self.msg_dict[transport.dev_info['dev_id']]:
            for case in self.to_send_case:
                if case.test(msg):
                    if case.act(transport, id):
                        self.msg_dict[transport.dev_info['dev_id']].remove(
                            (id, msg))
        if len(self.msg_dict[transport.dev_info['dev_id']]) == 0:
            del self.msg_dict[transport.dev_info['dev_id']]
        print('新的msg_dict', self.msg_dict)