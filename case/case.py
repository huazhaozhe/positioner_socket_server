# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/25 9:11
# @Author   : zhe
# @FileName : case.py
# @Project  : PyCharm


import time
import binascii
from datetime import datetime, timedelta
from case.base_case import *


class HeartBeat(BaseCase):

    def act(self, transport):
        write_logger(transport.dev_info['dev_id'] + '.log',
                     '协议%s心跳包' % hex(self.number),
                     level=logging.INFO)
        time_now = datetime.now()
        time_list = [time_now.year, time_now.month, time_now.day,
                     time_now.hour, time_now.minute, time_now.second]
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
        log_str = '协议:%s尝试设置时间 bytes字节串:%s 16进制字节串:%s' % (
                hex(self.number), send_msg, send_msg.hex())
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)
        transport.transport.write(send_msg)


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
        log_str = '协议:%sGPS数据 经纬度:%sE%sN 定位时间:%s' \
                  % (
                      hex(self.number),
                      gps_longitude,
                      gps_latitude,
                      gps_date.strftime('%Y-%m-%d %H:%M:%S')
                  )
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

    def hexadecimal_to_sexagesimal(self, value):
        value = bytes_to_dec(value)
        return str(value / 30000 / 60)

    def gps_date_time(self, date_time):
        date_time = list(map(str, date_time))
        date_time_str = '-'.join(date_time[:3]) + ' ' + ':'.join(date_time[3:])
        return datetime.strptime(date_time_str, '%y-%m-%d %H:%M:%S')

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
        log_str = '协议:%s状态更新 电量:%s' % (hex(self.number), data['battery'])
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

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
        log_str = '协议:%s恢复出厂' % (hex(self.number))
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

    def factory_reset(self, transport):
        transport.transport.write(self.data)


class DeviceTimeUpdate(BaseCase):

    def act(self, transport):
        time_now = datetime.now() - timedelta(hours=8)
        time_list = [time_now.year, time_now.month, time_now.day,
                     time_now.hour, time_now.minute, time_now.second]
        time_str = ''.join(
            map(
                lambda x: hex(x)[2:]
                if len(hex(x)[2:]) % 2 == 0 else '0' + hex(x)[2:], time_list
            )
        )
        time_bytes = bytes().fromhex(time_str)
        self.set_time(transport, time_bytes)
        log_str = '协议:%s更新时间' % (hex(self.number))
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

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
        date_time = self.wifi_date_time(self.data[4:4 + 6])
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
        log_str = '协议:%sWIFI数据 lng:%s lat:%s 时间:%s' \
                  % (
                      hex(self.number),
                      data['lng'],
                      data['lat'],
                      data['time'].strftime('%Y-%m-%d %H:%M:%S')
                  )
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

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
        date_time = str(binascii.b2a_hex(date_time))[2:-1]
        date_time_list = []
        for i in range(0, len(date_time), 2):
            date_time_list.append(date_time[i:i + 2])
        date_time_str = '-'.join(date_time_list[:3]) + ' ' + ':'.join(
            date_time_list[3:])
        return datetime.strptime(date_time_str, '%y-%m-%d %H:%M:%S')

    def server_response(self, transport):
        send_msg = ''.join(map(chr, self.startwith)) + chr(0x00) + chr(
            self.number) + ''.join(
            map(chr, self.data_list[4:4 + 6])) + ''.join(
            map(chr, self.endwith))
        transport.transport.write(send_msg.encode())
        return True


class OffWifiPositioning(WifiPositioning):
    pass


class SetUploadIntervalBySms(BaseCase):

    def act(self, transport):
        self.server_ack(transport)
        log_str = '协议:%s短信设置上传间隔' % (hex(self.number))
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)

    def server_ack(self, transport):
        transport.transport.write(self.data)


class DeviceSleep(BaseCase):

    def act(self, transport):
        log_str = '协议:%s设备休眠' % (hex(self.number))
        write_logger(transport.dev_info['dev_id'] + '.log', log_str,
                     level=logging.INFO)
        transport.transport.loseConnection()


class SyncSettings(ToSendCase):
    pass


class RebootDevice(ToSendCase):
    pass


class SetHostPort(ToSendCase):
    pass


class ManualPositioning(ToSendCase):
    pass


class SetUploadIntervalByServer(ToSendCase):
    pass


class SetHeartBeat(ToSendCase):
    pass


class ForbiddenToUpload(ToSendCase):
    pass
