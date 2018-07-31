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

    def act(self, transport, data):
        time_now = datetime.now()
        time_list = [time_now.year, time_now.month, time_now.day,
                     time_now.hour, time_now.minute, time_now.second]
        time_str = ''.join(
            map(
                lambda x: hex(x)[2:]
                if len(hex(x)[2:]) % 2 == 0 else '0' + hex(x)[2:], time_list
            )
        )
        log_str = '协议 %s 心跳包' % self.number
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)
        send_msg = self.startwith + '0730' + time_str + self.endwith
        self.send_to_device(transport, send_msg, log=False)
        return True


class GpsPositioning(BaseCase):

    def act(self, transport, data):
        data_tuple = tuple(data)
        gps_date = self.gps_date_time(data_tuple[4:4 + 6])
        gps_longitude = self.hexadecimal_to_sexagesimal(
            data_tuple[11:11 + 4])
        gps_latitude = self.hexadecimal_to_sexagesimal(
            data_tuple[11 + 4:11 + 8])
        gps_data = {
            'dev_id': transport.dev_info['dev_id'],
            'name': transport.dev_info['name'],
            'time': gps_date,
            'lng': gps_longitude,
            'lat': gps_latitude
        }
        self.update_to_location(gps_data)
        self.insert_to_hisdata(gps_data)
        send_msg = self.startwith + '0010' + str(
            binascii.b2a_hex(data[4:4 + 6]))[2:-1] + self.endwith
        self.send_to_device(transport, send_msg)
        log_str = '协议 %s GPS数据\t经纬度 %sE%sN\t定位时间 %s' \
                  % (
                      self.number,
                      gps_longitude,
                      gps_latitude,
                      gps_date.strftime('%Y-%m-%d %H:%M:%S')
                  )
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
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
        session = DBSession()
        try:
            session.add(hisdata)
            session.commit()
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' % data['dev_id']
            logger.error_log('error.log', log_str)
        finally:
            session.close()

    def update_to_location(self, data):
        session = DBSession()
        try:
            location = session.query(LocationCard).filter_by(
                dev_id=data['dev_id']).first()
            if location:
                location.time = data['time']
                location.lng = data['lng']
                location.lat = data['lat']
                session.commit()
            else:
                log_str = '协议 %s location不存在设备 %s' % (
                    self.number, data['dev_id'])
                logger.info_log(data['dev_id'] + '.log', log_str,
                                level=logging.WARNING)
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' % data['dev_id']
            logger.error_log('error.log', log_str)
        finally:
            session.close()


class DeviceStatus(BaseCase):

    def act(self, transport, data):
        data_tuple = tuple(data)
        status_data = {
            'dev_id': transport.dev_info['dev_id'],
            'battery': data_tuple[4],
        }
        self.update_to_location(status_data)
        log_str = '协议 %s 状态更新\t电量 %s' % (self.number, status_data['battery'])
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)

    def update_to_location(self, data):
        session = DBSession()
        try:
            location = session.query(LocationCard).filter_by(
                dev_id=data['dev_id']).first()
            if location:
                location.battery = data['battery']
                session.commit()
            else:
                log_str = '协议 %s location不存在设备 %s' % (
                    self.number, data['dev_id'])
                logger.info_log(data['dev_id'] + '.log', log_str,
                                level=logging.WARNING)
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' % data['dev_id']
            logger.error_log('error.log', log_str)
        finally:
            session.close()


class FactoryReset(BaseCase):

    def act(self, transport, data):
        send_msg = self.startwith + '0115' + self.endwith
        self.send_to_device(transport, send_msg)
        log_str = '协议 %s 恢复出厂' % self.number
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)


class DeviceTimeUpdate(BaseCase):

    def act(self, transport, data):
        time_now = datetime.now() - timedelta(hours=8)
        time_list = [time_now.year, time_now.month, time_now.day,
                     time_now.hour, time_now.minute, time_now.second]
        time_str = ''.join(
            map(
                lambda x: hex(x)[2:]
                if len(hex(x)[2:]) % 2 == 0 else '0' + hex(x)[2:], time_list
            )
        )
        send_msg = self.startwith + '0730' + time_str + self.endwith
        self.send_to_device(transport, send_msg)
        log_str = '协议 %s 更新时间' % self.number
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)


class WifiPositioning(BaseCase):

    def __init__(self, number, startwith, endwith):
        self.startwith = startwith
        self.endwith = endwith
        self.number = number
        self.error = {
            'protocol': False,
        }

    def act(self, transport, data):
        data_tuple = tuple(data)
        dev_id = transport.dev_info['dev_id']
        date_time = self.wifi_date_time(data[4:4 + 6])
        wifi_data = {
            'dev_id': transport.dev_info['dev_id'],
            'name': transport.dev_info['name'],
            'lng': None,
            'lat': None,
            'time': date_time
        }
        if data_tuple[2] > 0:
            mac_dict = self.get_wifi_mac(data_tuple, dev_id, date_time)
            transport.dev_info['mac_dict'] = mac_dict
            wifi_data['lng'] = 'wifi#' + mac_dict['bssid']
        lbs_offset = 10 + data_tuple[2] * 7
        lbs_num = data_tuple[lbs_offset]
        if lbs_num > 0:
            lbs_dict = self.get_lbs(data_tuple, dev_id, date_time, lbs_num, lbs_offset)
            transport.dev_info['lbs_dict'] = lbs_dict
            wifi_data['lat'] = '#'.join(map(str,
                                       ['lbs', lbs_dict['mcc'],
                                        lbs_dict['mnc'], lbs_dict['lac'],
                                        lbs_dict['cellid']]))
        self.insert_to_hosdata(wifi_data)
        self.update_to_location(wifi_data)
        send_msg = self.startwith + '00' + self.number + date_time.strftime(
            '%y%m%d%H%M%S') + self.endwith
        self.send_to_device(transport, send_msg)
        log_str = '协议 %s WIFI数据\tlng %s lat %s\t时间 %s' \
                  % (
                      self.number,
                      data['lng'],
                      data['lat'],
                      data['time'].strftime('%Y-%m-%d %H:%M:%S')
                  )
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)

    def get_wifi_mac(self, data_tuple, dev_id, date_time):
        mac_dict = {
            'dev_id': dev_id,
            'mac_num': data_tuple[2],
            'bssid': ':'.join(
                map(lambda x: hex(x)[2:], data_tuple[10:16])),
            'rssi': data_tuple[16],
            'time': date_time,
        }
        return mac_dict

    def get_lbs(self, data_tuple, dev_id, date_time, lbs_num, lbs_offset):
        lbs_dict = {
            'dev_id': dev_id,
            'lbs_num': lbs_num,
            'mcc': bytes_to_dec(data_tuple[lbs_offset + 1:lbs_offset + 3]),
            'mnc': data_tuple[lbs_offset + 3],
            'lac': bytes_to_dec(data_tuple[lbs_offset + 4:lbs_offset + 6]),
            'cellid': bytes_to_dec(
                data_tuple[lbs_offset + 6:lbs_offset + 8]),
            'mciss': data_tuple[lbs_offset + 8],
            'time': date_time,
        }
        return lbs_dict

    def update_to_location(self, data):
        session = DBSession()
        try:
            location = session.query(LocationCard).filter_by(
                dev_id=data['dev_id']).first()
            if location:
                location.time = data['time']
                if data['lng']:
                    location.lng = data['lng']
                if data['lat']:
                    location.lat = data['lat']
                session.commit()
            else:
                log_str = '协议 %s location不存在设备 %s' % (
                    self.number, data['dev_id'])
                logger.info_log(data['dev_id'] + '.log', log_str,
                                level=logging.WARNING)
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' % data['dev_id']
            logger.error_log('error.log', log_str)
        finally:
            session.close()

    def insert_to_hosdata(self, data):
        hisdata = HisData(
            dev_id=data['dev_id'],
            name=data['name'],
            time=data['time'],
            lng=data['lng'],
            lat=data['lat']
        )
        session = DBSession()
        try:
            session.add(hisdata)
            session.commit()
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' % data['dev_id']
            logger.error_log('error.log', log_str)
        finally:
            session.close()

    def wifi_date_time(self, date_time):
        date_time = str(binascii.b2a_hex(date_time))[2:-1]
        date_time_list = []
        for i in range(0, len(date_time), 2):
            date_time_list.append(date_time[i:i + 2])
        date_time_str = '-'.join(date_time_list[:3]) + ' ' + ':'.join(
            date_time_list[3:])
        return datetime.strptime(date_time_str, '%y-%m-%d %H:%M:%S')


class OffWifiPositioning(WifiPositioning):
    pass


class SetUploadIntervalBySms(BaseCase):

    def act(self, transport, data):
        send_msg = str(binascii.b2a_hex(data))[2:-1]
        self.send_to_device(transport, send_msg)
        log_str = '协议 %s 短信设置上传间隔' % self.number
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)


class DeviceSleep(BaseCase):

    def act(self, transport, data):
        log_str = '协议 %s 设备休眠' % self.number
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
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
