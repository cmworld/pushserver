# -*- coding:utf-8 -*-
import redis
import torndb

rds = None
db = None

def RdsConn(host,port,db):
    global rds

    if rds == None:
        rds = redis.Redis(host=host, port=port, db=db)
    return rds


def DBConn(host,database,user,password):
    global db
    if db == None:
        setting = {
            'host': host,
            'database': database,
            'user': user,
            'password': password
        }
        db = torndb.Connection(**setting)

    return db

rdsconn = RdsConn
dbconn = DBConn