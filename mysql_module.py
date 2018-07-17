# !/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time     : 2018/7/17 14:49
# @Author   : zhe
# @FileName : mysql_module.py
# @Project  : PyCharm

import pymysql
from config import mysql_conf

db = pymysql.connect(mysql_conf['ip'], mysql_conf['user'], mysql_conf['password'], mysql_conf['database'])
cursor = db.cursor()
sql = """CREATE TABLE EMPLOYEE (
         FIRST_NAME  CHAR(20) NOT NULL,
         LAST_NAME  CHAR(20),
         AGE INT,  
         SEX CHAR(1),
         INCOME FLOAT )"""
try:
    cursor.execute(sql)
except:
    pass
cursor.execute('select version()')
data = cursor.fetchone()
print('Database version : %s' % data)
db.close()