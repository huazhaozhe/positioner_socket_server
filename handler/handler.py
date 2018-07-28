# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 13:09
# @Author   : zhe
# @FileName : data_structure.py
# @Project  : PyCharm


from case.case import *
from config import DEBUG

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
    OffWifiPositioning(number=0x17, startwith=startwith, endwith=endwith),
    SetUploadIntervalBySms(number=0x98, length=0x03, startwith=startwith,
                           endwith=endwith),
    DeviceSleep(number=0x14, length=0x01, startwith=startwith,
                endwith=endwith),
]

to_send_case = [
    RebootDevice(number=0x48, length=0x01, startwith=startwith,
                 endwith=endwith),
    SetHostPort(number=0x66, length=0x07, startwith=startwith,
                endwith=endwith),
    ManualPositioning(number=0x80, length=0x01, startwith=startwith,
                      endwith=endwith),
    SetUploadIntervalByServer(number=0x97, length=0x03, startwith=startwith,
                              endwith=endwith),
    SetHeartBeat(number=0x13, length=0x02, startwith=startwith,
                 endwith=endwith),
    ForbiddenToUpload(number=0x44, length=0x01, startwith=startwith,
                      endwith=endwith),
]


class Handler():

    def __init__(self, to_send_enable=False):
        self.login_client = []
        self.to_send_enable = to_send_enable
        self.msg_dict = {}

    def add_case(self, login_case=login_case, case=case,
                 to_send_case=to_send_case):
        self.login_case = login_case
        self.case = case
        self.to_send_case = to_send_case

    def handler(self, data, transport):
        data_tuple = tuple(data)

        if transport in self.login_client:
            transport.dev_info['last_time'] = time.strftime(
                '%Y-%m-%d %H:%M:%S')
            print('在 %s 收到设备的消息: %s\n字符串: %s\n元组: %s\n' % (
                transport.dev_info['last_time'],
                transport.dev_info['dev_id'], data, data_tuple))
            for case in self.case:
                test = case.test(data_tuple, data)
                print('test', test)
                if test is True:
                    case.act(transport)
                    break
                elif test is 0:
                    break

        elif self.login_case.test(data_tuple, data):
            if self.login_case.act(transport):
                self.login_client.append(transport)

        elif DEBUG and transport not in self.login_client:
            dev = session.query(EmployeeInfoCard).filter(
                EmployeeInfoCard.dev_id == '0123456789012345').one()
            self.login_case.login_success(dev, transport)
            self.login_client.append(transport)

        if transport in self.login_client:
            if self.to_send_enable:
                self.to_send_init(transport.dev_info['dev_id'])
                if transport.dev_info['dev_id'] in self.msg_dict:
                    self.to_send_device(transport)
            return True

        transport.transport.loseConnection()
        # transport.transport.abortConnection()

    def to_send_init(self, dev_id):
        msg_list = session.query(ToSendModel).filter(
            ToSendModel.dev_id == dev_id,
            ToSendModel.status == 0
        ).all()
        if len(msg_list) > 0:
            if dev_id not in self.msg_dict:
                self.msg_dict[dev_id] = []
            for msg in msg_list:
                self.msg_dict[msg.dev_id].append((msg.id, msg.msg))
        print('原始msg_dict', self.msg_dict)
        return self.msg_dict

    def to_send_device(self, transport):
        # for id, msg in self.msg_dict[transport.dev_info['dev_id']]:
        while self.msg_dict[transport.dev_info['dev_id']]:
            (id, msg) = self.msg_dict[transport.dev_info['dev_id']].pop(0)
            new_msg = msg.replace(' ', '').replace(':', '').replace('#', '')
            for case in self.to_send_case:
                if case.test(new_msg):
                    case.act(transport, id)
        if len(self.msg_dict[transport.dev_info['dev_id']]) == 0:
            del self.msg_dict[transport.dev_info['dev_id']]
        print('新的msg_dict', self.msg_dict)

    def add_msg(self, msg_data):
        try:
            dev_id_list = []
            dev_all = session.query(EmployeeInfoCard).all()
            for dev in dev_all:
                dev_id_list.append(dev.dev_id)
            print(dev_id_list)
            id_list = []
            msg_list = []
            for msg in msg_data[1]:
                new_msg = msg.replace(' ', '').replace(':', '').replace('#',
                                                                        '')
                if len(new_msg) % 2 != 0:
                    print('msg长度不正确: ', msg)
                    continue
                try:
                    bytes().fromhex(new_msg)
                except:
                    print('msg不是16进制字节串: ', msg)
                    continue
                msg_list.append(new_msg)
            if msg_data[0] == 'all':
                id_list = dev_id_list
            else:
                id_list = msg_data[0]
            for id in id_list:
                if id not in dev_id_list:
                    print('数据库中不存在的设备: ', id)
                for msg in msg_list:
                    new_msg = ToSendModel(dev_id=id, msg=msg,
                                          created_at=datetime.now(), status=0)
                    session.add(new_msg)
            session.commit()
        except:
            print('添加发生错误')

    def logout(self, transport):
        location = session.query(LocationCard).filter(
            LocationCard.dev_id == transport.dev_info['dev_id']).first()
        location.connect = 0
        location.last_time = datetime.now()
        session.commit()
        del transport.dev_info
