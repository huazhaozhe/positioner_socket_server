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
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from config import mysql_conf, sql_echo

Base = declarative_base()
engine_str = 'mysql+pymysql://' + mysql_conf['user'] + ':' + \
             mysql_conf['password'] + '@' + mysql_conf['host'] + ':' + \
             mysql_conf['port'] + '/' + mysql_conf['database']
engine = create_engine(engine_str, echo=sql_echo)
metadata = MetaData(engine)


def time_now():
    return time.strftime('%Y-%m-%d %H:%M:%S')


employeeinfo_card = Table('employeeinfo_card', metadata,
                          Column('dev_id', String(20), nullable=False,
                                 primary_key=True),
                          Column('name', String(20), nullable=True,
                                 index=True),
                          Column('TEL', String(20), nullable=True, index=True),
                          Column('ICCID', String(22), nullable=True),
                          Column('work_place', String(300), nullable=True),
                          Column('area', String(20), nullable=True),
                          Column('worktime', String(20), nullable=True),
                          Column('work_area_detailed', String(30),
                                 nullable=True),
                          Column('note', String(300), nullable=True))


class EmployeeInfoCard(Base):
    __tablename__ = 'employeeinfo_card'

    dev_id = Column(String(20), primary_key=True)
    name = Column(String(20), default='name', nullable=True, index=True)
    TEL = Column(String(20), nullable=True, index=True)
    ICCID = Column(String(22), nullable=True)
    work_place = Column(String(300), nullable=True)
    area = Column(String(20), default='bc', nullable=True)
    worktime = Column(String(20), nullable=True)
    work_area_detailed = Column(String(30), nullable=True)
    note = Column(String(300), nullable=True)


hisdata = Table('hisdata', metadata,
                Column('id', Integer, primary_key=True),
                Column('dev_id', String(20), nullable=False, index=True),
                Column('name', String(20), nullable=True, index=True),
                # Column('time', String(25), nullable=True),
                Column('time', DateTime, nullable=True),
                Column('lng', String(50), nullable=True),
                Column('lat', String(50), nullable=True))


class HisData(Base):
    __tablename__ = 'hisdata'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(20), nullable=False, index=True)
    name = Column(String(20), nullable=True, index=True)
    # time = Column(String(25))
    time = Column(DateTime, nullable=True)
    lng = Column(String(50), nullable=True)
    lat = Column(String(50), nullable=True)


location_card = Table('location_card', metadata,
                      Column('dev_id', String(25), primary_key=True,
                             nullable=False),
                      Column('name', String(30), nullable=True, index=True),
                      # Column('time', String(30), nullable=True),
                      Column('time', DateTime, nullable=True),
                      Column('lng', String(50), nullable=True),
                      Column('lat', String(50), nullable=True),
                      Column('area', String(30), nullable=True),
                      Column('connect', Integer, nullable=True, index=True),
                      Column('battery', Integer, nullable=True),
                      Column('link', String(5), nullable=True),
                      Column('last_time', DateTime, nullable=True),
                      Column('note', String(300), nullable=True))


class LocationCard(Base):
    __tablename__ = 'location_card'

    dev_id = Column(String(25), primary_key=True)
    name = Column(String(30), nullable=True, index=True)
    # time = Column(String(30))
    time = Column(DateTime, nullable=True)
    lng = Column(String(50), nullable=True)
    lat = Column(String(50), nullable=True)
    area = Column(String(30), nullable=True)
    connect = Column(Integer, nullable=True, index=True)
    battery = Column(Integer, nullable=True)
    link = Column(String(5), nullable=True)
    last_time = Column(DateTime, nullable=True)
    note = Column(String(300), nullable=True)


to_send_device = Table('to_send_device', metadata,
                       Column('id', Integer, primary_key=True),
                       Column('dev_id', String(25), nullable=False,
                              index=True),
                       Column('msg', String(300), nullable=False, index=True),
                       Column('status', Integer, default=0, nullable=False,
                              index=True),
                       Column('created_at', DateTime, nullable=True),
                       Column('sent_at', DateTime, nullable=True),
                       Column('note', String(300), nullable=True))


class ToSendModel(Base):
    __tablename__ = 'to_send_device'

    id = Column(Integer, primary_key=True)
    dev_id = Column(String(25), nullable=False, index=True)
    msg = Column(String(300), nullable=False, index=True)
    status = Column(Integer, default=0, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now, nullable=True)
    sent_at = Column(DateTime, nullable=True)
    note = Column(String(300), nullable=True)


metadata.create_all(engine)
session_factory = sessionmaker(bind=engine)
DBSession = scoped_session(session_factory)
