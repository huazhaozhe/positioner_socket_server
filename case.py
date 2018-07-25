# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/25 9:11
# @Author   : zhe
# @FileName : case.py
# @Project  : PyCharm


import time
from datetime import datetime
from base_case import *


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
        time_bytes = bytes().fromhex(time_str)
        self.set_time(transport, time_bytes)

    def set_time(self, transport, time_bytes):
        send_msg = (''.join(map(chr, self.startwith)) + chr(0x07) + chr(
            self.number)).encode() + time_bytes + ''.join(
            map(chr, self.endwith)).encode()
        transport.transport.write(send_msg)


class WifiPositioning(BaseCase):

    def __init__(self, number, startwith, endwith):
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
