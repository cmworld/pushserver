# -*- coding: utf-8 -*-

from model import Model

class AdModel(Model):

    def add_ad(self,title,picurl,linkurl,sort_order,expire,enable,createtime):
        sql = "insert into xs_advertis (title,picurl,linkurl,sort_order,expire,enable,createtime) values(%s,%s,%s,%s,%s,%s,%s)"
        return self.db.execute_lastrowid(sql,title,picurl,linkurl,sort_order,expire,enable,createtime)

    def update_ad(self,update={},where={}):
        update_sql = self.parse_dict(update)
        where_sql = self.parse_dict(where,' and ')

        sql = "update xs_advertis set %s where %s" % (update_sql,where_sql)
        print sql
        return self.db.execute(sql)
          
    def get_adByAid(self,aid):
        sql = "select * from xs_advertis where aid=%s"
        return self.db.get(sql,aid)

    def get_ads(self,where={} , offset=0,limit=0):
        where_sql = ''
        if where:
            where_sql = " where %s " % self.parse_dict(where,' and ')
        
        limit_sql = ''
        if limit and offset:
            limit_sql = ' limit %s,%s ' % (offset,limit)
        sql = "select * from xs_advertis %s %s" % (where_sql,limit_sql)
        return self.db.query(sql)