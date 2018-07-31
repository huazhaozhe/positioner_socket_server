# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/21 10:32
# @Author   : zhe
# @FileName : twisted_server.py
# @Project  : PyCharm

from twisted.internet import reactor
from twisted.internet.protocol import Protocol, Factory
from handler.handler import Handler
from config import server_port
from socket_fun import Logger

handler = Handler(to_send_enable=True)
# handler.add_case()
logger = Logger()

class MyProtocal(Protocol):
    def connectionMade(self):
        logger.std_log('客户端连接 %s:%s' % self.transport.client)

    def connectionLost(self, reason):
        if self in handler.login_client:
            handler.login_client.remove(self)
            handler.logout(self)
        logger.std_log('客户端断开 %s:%s' % self.transport.client)

    def dataReceived(self, data):
        handler.handler(self, data)


if __name__ == '__main__':
    factory = Factory()
    factory.protocol = MyProtocal
    info = reactor.listenTCP(server_port, factory)
    logger.std_log('sever port %s' % info.port)
    reactor.run()
