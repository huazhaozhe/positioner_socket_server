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


class Handler():

    def __init__(self, startwith=startwith, endwith=endwith):
        self.startwith = startwith
        self.endwith = endwith
        self.login_client = []

    def add_case(self, login_case=login_case, case=case):
        self.login_case = login_case
        self.case = case

    def handler(self, data, transport):
        data_tuple = tuple(data)
        if DEBUG and transport not in self.login_client:
            dev = session.query(EmployeeInfoCard).filter(
                EmployeeInfoCard.dev_id == '0123456789012345').one()
            self.login_case.login_success(dev, transport)
            self.login_client.append(transport)
        if transport in self.login_client:
            transport.dev_info['last_time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S')
            print('在 %s 收到设备的消息: %s\n字符串: %s\n元组: %s\n' % (
                transport.dev_info['last_time'],
                transport.dev_info['dev_id'], data, data_tuple))
            for case in self.case:
                if case.test(data_tuple):
                    case.act(transport)
                    break
            return True
        elif self.login_case.test(data_tuple):
            if self.login_case.act(transport):
                self.login_client.append(transport)
                return True

        transport.transport.loseConnection()
        # transport.transport.abortConnection()
