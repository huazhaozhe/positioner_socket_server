# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 10:32
# @Author   : zhe
# @FileName : twisted_server.py
# @Project  : PyCharm

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from handler import Handler
from config import server_port

handler = Handler(to_send_enable=True)
handler.add_case()
client = []


class MyProtocal(Protocol):
    def connectionMade(self):
        # self.transport.write(('欢迎客户端 %s:%s' % self.transport.client).encode())
        client.append(self)
        print('来自%s:%s的客户端已连接' % self.transport.client)

    def connectionLost(self, reason):
        if self in handler.login_client:
            print('已经登录的客户端 %s:%s已断开' % self.transport.client)
            handler.logout(self)
            handler.login_client.remove(self)
        elif self in client:
            print('未登录的客户端%s:%s已断开' % self.transport.client)
            client.remove(self)

    def dataReceived(self, data):
        handler.handler(data, self)


if __name__ == '__main__':
    factory = Factory()
    factory.protocol = MyProtocal
    info = reactor.listenTCP(server_port, factory)
    print('server at %s' % info.port)
    reactor.run()
