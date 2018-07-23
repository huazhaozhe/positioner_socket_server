# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 10:32
# @Author   : zhe
# @FileName : twisted_server.py
# @Project  : PyCharm

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from communication_protocol import Handler, login_client

handler = Handler()
client = []


class MyProtocal(Protocol):
    def connectionMade(self):
        self.transport.write(('欢迎客户端 %s:%s' % self.transport.client).encode())
        client.append(self)
        print('来自%s:%s的客户端已连接' % self.transport.client)

    def connectionLost(self, reason):
        if self in login_client:
            print('已经登录的客户端 %s:%s已断开' % self.transport.client)
            login_client.remove(self)
        else:
            print('未登录的客户端%s:%s已断开' % self.transport.client)
            client.remove(self)

    def dataReceived(self, data):
        print('收到原始字符：', data)
        print(data[3], type(data[3]))
        print(data[1:4], type(data[1:4]))
        handler.handler(data, self)


if __name__ == '__main__':
    factory = Factory()
    factory.protocol = MyProtocal
    info = reactor.listenTCP(10086, factory)
    print('server at %s' % info.port)
    reactor.run()
