# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 13:09
# @Author   : zhe
# @FileName : data_structure.py
# @Project  : PyCharm

import time
from datetime import datetime
from orm import *

DEBUG = True
startwith = (0x78, 0x78)
endwith = (0x0d, 0x0a)

login_client = []
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

    def __init__(self, number, length, startwith=startwith, endwith=endwith):
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

    def test(self, data):
        try:
            if not self.pretreatment(data):
                print('预处理失败')
                return False
            if data[3] != self.number:
                return self.error['protocol']
            self.data_list = data
            return True
        except:
            return False

    def act(self, transport):
        pass


class LoginCase(BaseCase):

    def login_success(self, dev, transport):
        send_msg = ''.join(map(chr, self.startwith)) + chr(
            0x01) + chr(0x01) + ''.join(map(chr, self.endwith))
        print('%s 登录成功' % dev.dev_id)
        transport.transport.write(send_msg.encode())
        dev_info = {
            'dev_id': dev.dev_id,
            'name': dev.name,
            'login_status': 1,
            'login_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'last_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        }
        transport.dev_info = dev_info
        login_client.append(transport)
        return True

    def login_failure(self, dev_str, transport):
        print('%s 登录失败' % dev_str)
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x01) + chr(
            0x44) + ''.join(map(chr, self.endwith))
        transport.transport.write(send_msg.encode())
        transport.transport.loseConnection()
        return True

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
            self.login_success(dev_checked[1], transport)
        else:
            self.login_failure(dev_checked[1], transport)


class HeartBeat(BaseCase):

    def act(self, transport):
        print('收到设备 %s 心跳包' % transport.dev_info['dev_id'])


class GpsPositioning(BaseCase):

    def act(self, transport):
        gps_date = self.gps_date_time(self.data_list[4:4 + 6])
        gps_longitude = self.hexadecimal_to_sexagesimal(
            self.data_list[11:11 + 4])
        gps_latitude = self.hexadecimal_to_sexagesimal(
            self.data_list[11 + 4:11 + 8])
        data = {
            'dev_id': transport.dev_info['dev_id'],
            'name': transport.dev_info['name'],
            'time': gps_date,
            'lng': gps_longitude,
            'lat': gps_latitude
        }
        self.update_to_location(data)
        self.insert_to_hisdata(data)
        self.server_response(transport)

    def hexadecimal_to_sexagesimal(self, value):
        value = bytes_to_dec(value)
        return str(value / 30000 / 60)

    def gps_date_time(self, date_time):
        date_time = list(map(str, date_time))
        return '-'.join(date_time[:3]) + ' ' + ':'.join(date_time[3:])

    def insert_to_hisdata(self, data):
        hisdata = HisData(
            dev_id=data['dev_id'],
            name=data['name'],
            time=data['time'],
            lng=data['lng'],
            lat=data['lat']
        )
        session.add(hisdata)
        session.commit()

    def update_to_location(self, data):
        location = session.query(LocationCard).filter_by(
            dev_id=data['dev_id']).all()
        if len(location) > 1:
            pass
            # raise ValueError
        elif len(location) == 1:
            location = location[0]
            location.time = data['time']
            location.lng = data['lng']
            location.lat = data['lat']
            session.commit()
        else:
            pass
            # raise ValueError

    def server_response(self, transport):
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x00) + chr(
            self.number) + ''.join(
            map(chr, self.data_list[4:4 + 6])) + ''.join(
            map(chr, self.endwith))
        transport.transport.write(send_msg.encode())
        return True


class DeviceStatus(BaseCase):

    def act(self, transport):
        data = {
            'dev_id': transport.dev_info['dev_id'],
            'battery': self.data_list[4],
        }
        self.update_to_location(data)

    def update_to_location(self, data):
        location = session.query(LocationCard).filter_by(
            dev_id=data['dev_id']).all()
        if len(location) > 1:
            pass
            # raise ValueError
        elif len(location) == 1:
            location = location[0]
            location.battery = data['battery']
            session.commit()
        else:
            pass
            # raise ValueError

    def set_heart_beat(self, transport, interval=0x03):
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x02) + chr(
            self.number) + chr(interval) + ''.join(map(chr, self.endwith))
        transport.transport.write(send_msg.encode())


class FactoryReset(BaseCase):

    def act(self, transport):
        self.factory_reset(transport)

    def factory_reset(self, transport):
        send_mag = ''.join(map(chr, self.startwith)) + chr(0x01) + chr(
            self.number) + ''.join(map(chr, self.endwith))
        transport.transport.write(send_mag.encode())


class DeviceTimeUpdate(BaseCase):

    def act(self, transport):
        time_now = datetime.now()
        time_list = [time_now.year, time_now.month, time_now.day,
                     time_now.hour, time_now.minute, time_now.second]
        print(time_list)
        time_str = ''.join(
            map(
                lambda x: hex(x)[2:]
                if len(hex(x)[2:]) % 2 == 0 else '0' + hex(x)[2:], time_list
            )
        )
        print(time_str)
        self.set_time(transport, time_str)

    def set_time(self, transport, time_str):
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x07) + chr(
            self.number) + time_str + ''.join(map(chr, self.endwith))
        transport.transport.write(send_msg.encode())


class WifiPositioning(BaseCase):

    def __init__(self, number, startwith=startwith, endwith=endwith):
        self.startwith = startwith
        self.endwith = endwith
        self.number = number
        self.error = {
            'protocol': False,
        }

    def act(self, transport):
        dev_id = transport.dev_info['dev_id']
        date_time = self.wifi_date_time(self.data_list[4:4 + 6])
        data = {
            'dev_id': transport.dev_info['dev_id'],
            'name': transport.dev_info['name'],
            'lng': None,
            'lat': None,
            'time': date_time
        }
        if self.data_list[2] > 0:
            mac_dict = self.get_wifi_mac(dev_id, date_time)
            transport.dev_info['mac_dict'] = mac_dict
            data['lng'] = 'wifi#' + mac_dict['bssid']
        lbs_offset = 10 + self.data_list[2] * 7
        lbs_num = self.data_list[lbs_offset]
        if lbs_num > 0:
            lbs_dict = self.get_lbs(dev_id, date_time, lbs_num, lbs_offset)
            transport.dev_info['lbs_dict'] = lbs_dict
            data['lat'] = '#'.join(map(str,
                                       ['lbs', lbs_dict['mcc'],
                                        lbs_dict['mnc'], lbs_dict['lac'],
                                        lbs_dict['cellid']]))
        self.insert_to_hosdata(data)
        self.update_to_location(data)
        self.server_response(transport)

    def get_wifi_mac(self, dev_id, date_time):
        mac_dict = {
            'dev_id': dev_id,
            'mac_num': self.data_list[2],
            'bssid': ':'.join(
                map(lambda x: hex(x)[2:], self.data_list[10:16])),
            'rssi': self.data_list[16],
            'time': date_time,
        }
        return mac_dict

    def get_lbs(self, dev_id, date_time, lbs_num, lbs_offset):
        lbs_dict = {
            'dev_id': dev_id,
            'lbs_num': lbs_num,
            'mcc': bytes_to_dec(self.data_list[lbs_offset + 1:lbs_offset + 3]),
            'mnc': self.data_list[lbs_offset + 3],
            'lac': bytes_to_dec(self.data_list[lbs_offset + 4:lbs_offset + 6]),
            'cellid': bytes_to_dec(
                self.data_list[lbs_offset + 6:lbs_offset + 8]),
            'mciss': self.data_list[lbs_offset + 8],
            'time': date_time,
        }
        return lbs_dict

    def update_to_location(self, data):
        location = session.query(LocationCard).filter_by(
            dev_id=data['dev_id']).all()
        if len(location) > 1:
            pass
            # raise ValueError
        elif len(location) == 1:
            location = location[0]
            location.time = data['time']
            if data['lng']:
                location.lng = data['lng']
            if data['lat']:
                location.lat = data['lat']
            session.commit()
        else:
            pass
            # raise ValueError

    def insert_to_hosdata(self, data):
        hisdata = HisData(
            dev_id=data['dev_id'],
            name=data['name'],
            time=data['time'],
            lng=data['lng'],
            lat=data['lat']
        )
        session.add(hisdata)
        session.commit()

    def wifi_date_time(self, date_time):
        date_time = list(map(str, date_time))
        return '-'.join(date_time[:3]) + ' ' + ':'.join(date_time[3:])

    def server_response(self, transport):
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x00) + chr(
            self.number) + ''.join(
            map(chr, self.data_list[4:4 + 6])) + ''.join(
            map(chr, self.endwith))
        transport.transport.write(send_msg.encode())
        return True


class Handler():
    logincase = LoginCase(number=0x01, length=0x0a)
    Case = [
        HeartBeat(number=0x08, length=0x01),
        GpsPositioning(number=0x10, length=0x12),
        DeviceStatus(number=0x13, length=0x06),
        FactoryReset(number=0x15, length=0x01),
        DeviceTimeUpdate(number=0x30, length=0x01),
        WifiPositioning(number=0x69),
    ]

    def handler(self, data, transport):
        data_tuple = tuple(data)
        if DEBUG and transport not in login_client:
            dev = session.query(EmployeeInfoCard).filter(
                EmployeeInfoCard.dev_id == '0123456789012345').one()
            self.logincase.login_success(dev, transport)
            login_client.append(transport)
        if transport in login_client:
            transport.dev_info['last_time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S')
            print('在 %s 收到设备的消息: %s\n字符串: %s\n元组: %s\n' % (
                transport.dev_info['last_time'],
                transport.dev_info['dev_id'], data, data_tuple))
            for case in self.Case:
                if case.test(data_tuple):
                    case.act(transport)
                    break
        elif self.logincase.test(data_tuple):
            self.logincase.act(transport)
        else:
            transport.transport.loseConnection()
            # transport.transport.abortConnection()
