# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 16:51
# @Author   : zhe
# @FileName : models.py
# @Project  : PyCharm


import time
from sqlalchemy import String, Column, create_engine, Float, Integer, MetaData, \
    Table
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from config import mysql_conf

Base = declarative_base()
engine_str = 'mysql+pymysql://' + mysql_conf['user'] + ':' + \
             mysql_conf['password'] + '@' + mysql_conf['host'] + ':' + \
             mysql_conf['port'] + '/' + mysql_conf['database']
engine = create_engine(engine_str, echo=True)
metadata = MetaData(engine)


def time_now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


class Message(Base):
    __tablename__ = 'message'

    id = Column(Integer, primary_key=True)
    message = Column(String(100))
    created_at = Column(String(50), default=time_now)


msg = Table('message', metadata,
            Column('id', Integer, primary_key=True),
            Column('message', String(100)),
            Column('created_at', String(50), default=time_now))

DBSession = sessionmaker(bind=engine)
metadata.create_all(engine)
