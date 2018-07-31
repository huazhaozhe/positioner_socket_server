# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 13:09
# @Author   : zhe
# @FileName : data_structure.py
# @Project  : PyCharm


from case.case import *
from config import DEBUG
from twisted.internet import defer

startwith = '7878'
endwith = '0D0A'

login_case = LoginCase(number='01', length=0x0a, startwith=startwith,
                       endwith=endwith)
receive_case = [
    HeartBeat(number='08', length=0x01, startwith=startwith,
              endwith=endwith),
    GpsPositioning(number='10', length=0x12, startwith=startwith,
                   endwith=endwith),
    DeviceStatus(number='13', length=0x06, startwith=startwith,
                 endwith=endwith),
    FactoryReset(number='15', length=0x01, startwith=startwith,
                 endwith=endwith),
    DeviceTimeUpdate(number='30', length=0x01, startwith=startwith,
                     endwith=endwith),
    WifiPositioning(number='69', startwith=startwith, endwith=endwith),
    OffWifiPositioning(number='17', startwith=startwith, endwith=endwith),
    SetUploadIntervalBySms(number='98', length=0x03, startwith=startwith,
                           endwith=endwith),
    DeviceSleep(number='14', length=0x01, startwith=startwith,
                endwith=endwith),
]

to_send_case = [
    RebootDevice(number='48'),
    SetHostPort(number='66'),
    ManualPositioning(number='80'),
    SetUploadIntervalByServer(number='97'),
    SetHeartBeat(number='13'),
    ForbiddenToUpload(number='44'),
    ToSendMsgNoNumber(number='00'),
]


class Handler():

    def __init__(self, to_send_enable=False):
        self.login_client = []
        self.to_send_enable = to_send_enable
        self.msg_dict = {}

    # def add_case(self, login_case=login_case, case=case,
    #              to_send_case=to_send_case):
    #     self.login_case = login_case
    #     self.case = case
    #     self.to_send_case = to_send_case

    def handler(self, transport, data):
        try:
            data_tuple = tuple(data)
        except:
            transport.transport.loseConnection()
            return False

        if transport in self.login_client:
            transport.dev_info['last_time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S')
            flag = 1
            for case in receive_case:
                test = case.test(data)
                if test == 1:
                    flag = 0
                    case.act(transport, data)
                    break
                elif test == -1:
                    logger.info_log(transport.dev_info['dev_id'] + '.log',
                                    '头尾检测失败\t原始字节串 %s\t10进制元组 %s'
                                    % (data, data_tuple),
                                    level=logging.ERROR
                                    )
                    break
            if flag and test != -1:
                logger.info_log(transport.dev_info['dev_id'] + '.log',
                                '协议 %s 不能够解析\t16进制字节串 %s 原始字节串 %s 10进制元组 %s'
                                % (
                                    str(binascii.b2a_hex(data[3:4]))[2:-1],
                                    str(binascii.b2a_hex(data))[2:-1], data,
                                    data_tuple),
                                level=logging.WARNING
                                )

        elif login_case.test(data) == 1:
            if login_case.act(transport, data):
                for tcp in self.login_client:
                    if tcp.dev_info['dev_id'] == transport.dev_info['dev_id']:
                        tcp.transport.loseConnection()
                self.login_client.append(transport)

        elif DEBUG and transport not in self.login_client:
            session = DBSession()
            dev = session.query(EmployeeInfoCard).filter(
                EmployeeInfoCard.dev_id == '0123456789012345').one()
            session.close()
            login_case.login_success(dev, transport)
            self.login_client.append(transport)

        if transport in self.login_client:
            if self.to_send_enable:
                if self.to_send_init(transport.dev_info['dev_id']):
                     self.to_send_device(transport)
            return True
        else:
            transport.transport.loseConnection()
            return False
        # transport.transport.abortConnection()

    def to_send_init(self, dev_id):
        session = DBSession()
        try:
            msg_list = session.query(ToSendModel).filter(
                ToSendModel.dev_id == dev_id,
                ToSendModel.status == 0
            ).all()
            if len(msg_list) > 0:
                if dev_id not in self.msg_dict:
                    self.msg_dict[dev_id] = []
                for msg in msg_list:
                    if (msg.id, msg.msg) in self.msg_dict[dev_id]:
                        continue
                    self.msg_dict[dev_id].append((msg.id, msg.msg))
            return len(msg_list)
        except:
            log_str = '数据库错误\t设备 %s' % dev_id
            logger.error_log('error.log', log_str)
            return 0
        finally:
            # finally一定会执行，即使except中return 0
            session.close()

    def to_send_device(self, transport):
        while self.msg_dict[transport.dev_info['dev_id']]:
            (id, msg) = self.msg_dict[transport.dev_info['dev_id']].pop(0)
            new_msg = msg.replace(' ', '').replace(':', '').replace('#', '')
            if transport in self.login_client:
                for case in to_send_case:
                    if case.test(new_msg):
                        case.act(transport, id, new_msg)
                        break
            else:
                transport.transport.loseConnection()
                break
        if len(self.msg_dict[transport.dev_info['dev_id']]) == 0:
            del self.msg_dict[transport.dev_info['dev_id']]
        return True

    def add_msg(self, msg_data):
        session = DBSession()
        try:
            dev_id_list = []
            dev_all = session.query(EmployeeInfoCard).all()
            for dev in dev_all:
                dev_id_list.append(dev.dev_id)
            id_list = []
            msg_list = []
            for msg in msg_data[1]:
                new_msg = msg.replace(' ', '').replace(':', '').replace('#',
                                                                        '')
                if len(new_msg) % 2 != 0:
                    logger.info_log('handler.log',
                                    'msg %s 长度不正确, 放弃添加本条msg' % msg,
                                    level=logging.WARNING, log_debug=True)
                    continue
                try:
                    bytes().fromhex(new_msg)
                except:
                    logger.info_log('handler.log',
                                    'msg %s 不是16进制字节串, 放弃添加本条msg' % msg,
                                    level=logging.WARNING, log_debug=True)
                    continue
                msg_list.append(new_msg)
            if msg_data[0] == 'all':
                id_list = dev_id_list
            else:
                id_list = msg_data[0]
            for id in id_list:
                if id not in dev_id_list:
                    logger.info_log('handler.log',
                                    '数据库中不存在设备ID %s, 但任然添加至发送数据库中' % id,
                                    level=logging.WARNING, log_debug=True)
                for msg in msg_list:
                    new_msg = ToSendModel(dev_id=id, msg=msg,
                                          created_at=datetime.now(), status=0)
                    session.add(new_msg)
            session.commit()
        except:
            logger.error_log('error.log', '数据库错误')
        finally:
            session.close()

    def logout(self, transport):
        session = DBSession()
        try:
            location = session.query(LocationCard).filter(
                LocationCard.dev_id == transport.dev_info['dev_id']).first()
            if location:
                location.connect = 0
                location.last_time = datetime.now()
                session.commit()
            else:
                log_str = 'location不存在设备 %s' % transport.dev_info['dev_id']
                logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                                level=logging.WARNING)
        except:
            session.rollback()
            log_str = '数据库错误\t设备 %s' % transport.dev_info['dev_id']
            logger.error_log('error.log', log_str)
        finally:
            session.close()
        (host, port) = transport.transport.client
        log_str = '设备 %s 注销成功 地址 %s:%s' \
                  % (transport.dev_info['dev_id'], host, port)
        logger.info_log('login.log', log_str, level=logging.INFO)
        logger.info_log(transport.dev_info['dev_id'] + '.log', log_str,
                        level=logging.INFO)
        del transport.dev_info
