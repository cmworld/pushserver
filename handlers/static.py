# -*- coding:utf-8 -*-
from handler import APIHandler
from model import Model
import sys
class staticHandler(APIHandler):
    def get(self):

        serv = self.application.serv
        rds = self.application.rds

        redis_isrun = True

        try:
            if rds.ping() == False:
                redis_isrun = False
        except:
            redis_isrun = False

        res = {}
        res['redis_runing'] = redis_isrun
        res['thread_working_count'] = len(serv.notifiers)
        res['thread_works'] = serv.notifiers.keys()
        #test the  mysql        
        try:
            setting = {'host': '127.0.0.1:3306', 'password': 'kdis83%l0l1i$', 'user': 'wlserver', 'database': 'hupu_apex'}
            Model.setup_dbs(setting)
            res['mysql_error'] = 'successful'
            
        except:
            e = sys.exc_info()
            print setting
            res['mysql_error'] = "Cannot connect to MySQL: %s" % e[1]

        
        
        token_count = 0
        if redis_isrun:
            token_count = len(rds.keys('tokens:info:*'))
        res['token_count'] = token_count

        invaildtokens_count = 0 
        if redis_isrun:
            invaildtokens_count = rds.scard('push:invaildtokens')
        res['feedback_token_count'] = invaildtokens_count

        self.finish(chunk=res)

handlers = [(r"/status", staticHandler)]