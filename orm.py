# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 16:51
# @Author   : zhe
# @FileName : models.py
# @Project  : PyCharm


import time
from datetime import datetime
from sqlalchemy import String, Column, create_engine, Float, Integer, MetaData, \
    Table, DateTime
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


employeeinfo_card = Table('employeeinfo_card', metadata,
                          Column('dev_id', String(20), nullable=False,
                                 primary_key=True),
                          Column('name', String(20), nullable=True),
                          Column('TEL', String(20), nullable=True),
                          Column('ICCID', String(22), nullable=True),
                          Column('work_place', String(300), nullable=True),
                          Column('area', String(20), nullable=True),
                          Column('worktime', String(20), nullable=True),
                          Column('work_area_detailed', String(30),
                                 nullable=True))


class EmployeeInfoCard(Base):
    __tablename__ = 'employeeinfo_card'

    dev_id = Column(String(20), primary_key=True)
    name = Column(String(20), default='zhe')
    TEL = Column(String(20))
    ICCID = Column(String(22))
    work_place = Column(String(300))
    area = Column(String(20), default='bc')
    worktime = Column(String(20))
    work_area_detailed = Column(String(30))


hisdata = Table('hisdata', metadata,
                Column('id', Integer, primary_key=True),
                Column('dev_id', String(20), nullable=False),
                Column('name', String(20), nullable=True),
                # Column('time', String(25), nullable=True),
                Column('time', DateTime, nullable=True),
                Column('lng', String(50), nullable=True),
                Column('lat', String(50), nullable=True))


class HisData(Base):
    __tablename__ = 'hisdata'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(20), nullable=False)
    name = Column(String(20), nullable=True)
    # time = Column(String(25))
    time = Column(DateTime, nullable=True)
    lng = Column(String(50), nullable=True)
    lat = Column(String(50), nullable=True)


location_card = Table('location_card', metadata,
                      Column('dev_id', String(25), primary_key=True,
                             nullable=False),
                      Column('name', String(30), nullable=True),
                      # Column('time', String(30), nullable=True),
                      Column('time', DateTime, nullable=True),
                      Column('lng', String(50), nullable=True),
                      Column('lat', String(50), nullable=True),
                      Column('area', String(30), nullable=True),
                      Column('connect', Integer, nullable=True),
                      Column('battery', Integer, nullable=True),
                      Column('link', String(5), nullable=True),
                      Column('last_time', DateTime, nullable=True))


class LocationCard(Base):
    __tablename__ = 'location_card'

    dev_id = Column(String(25), primary_key=True)
    name = Column(String(30), nullable=True)
    # time = Column(String(30))
    time = Column(DateTime, nullable=True)
    lng = Column(String(50), nullable=True)
    lat = Column(String(50), nullable=True)
    area = Column(String(30), nullable=True)
    connect = Column(Integer, nullable=True)
    battery = Column(Integer, nullable=True)
    link = Column(String(5), nullable=True)
    last_time = Column(DateTime, nullable=True)


to_send_device = Table('to_send_device', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('dev_id', String(25), nullable=False),
                       Column('msg', String(300), nullable=False),
                       Column('status', Integer, default=0, nullable=False),
                       Column('created_at', DateTime, nullable=True),
                       Column('sent_at', DateTime, nullable=True))


class ToSendModel(Base):
    __tablename__ = 'to_send_device'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(25), nullable=False)
    msg = Column(String(300), nullable=False)
    status = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    sent_at = Column(DateTime, nullable=True)


DBSession = sessionmaker(bind=engine)
metadata.create_all(engine)
