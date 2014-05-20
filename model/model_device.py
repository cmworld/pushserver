# -*- coding: utf-8 -*-

from model import Model

class DeviceModel(Model):

    def enable_token(self, token,enable):
        sql = "update xs_user_device set enable=%s where token=%s"
        return self.db.execute(sql,enable,token)

    def add_device(self,platform,token,uid,pushset,enable,createtime):
        sql = "insert into xs_user_device (platform,token, uid,pushset,enable,createtime) values(%s,%s,%s,%s,%s,%s)"
        return self.db.execute(sql,platform,token,uid,pushset,enable,createtime)

    def update_device(self,update={},where={}):
        update_sql = self.parse_dict(update)
        where_sql = self.parse_dict(where,' and ')

        sql = "update xs_user_device set %s where %s" % (update_sql,where_sql)
        return self.db.execute(sql)
          
    def get_deviceByToken(self,token):
        sql = "select * from xs_user_device where token=%s"
        return self.db.get(sql,token)

    def get_deviceByPid(self,pid):
        sql = "select * from xs_user_device where pid=%s"
        return self.db.get(sql,pid)

    def get_devices(self,where={} ,pushset=0, offset=0,limit=0):
        where_sql = ''
        if where:
            where_sql = " where %s " % self.parse_dict(where,' and ')
        
        if pushset:
            where_sql = where_sql + " and pushset > 0 "

        limit_sql = ''
        if limit and offset:
            limit_sql = ' limit %s,%s ' % (offset,limit)
        sql = "select * from xs_user_device %s %s" % (where_sql,limit_sql)
        return self.db.query(sql)