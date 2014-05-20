# -*- coding:utf-8 -*-
from handler import APIHandler
import exception

class DeviceRegisterHandler(APIHandler):
    def get(self):
        self.finish(chunk='')

    def post(self):
        token = self.get_argument("token",'')
        uid = self.get_argument("uid",0)
        platform = self.get_argument("platform",'')
        pushset = int(self.get_argument("pushset",0))

        if not token or not platform:
            raise exception.HTTPAPIError(status_code=400,error_detail="params missing")

        if not uid.isdigit():
            raise exception.HTTPAPIError(status_code=400,error_detail="params uid Invalid")

        if platform not in ['android','iphone']:
            raise exception.HTTPAPIError(status_code=400,error_detail="params platform Invalid")

        token = token.encode('utf-8');
        token_key = 'tokens:info:%s' % token

        data = {
            'enable':1,
            'pushset':pushset,
            'fail_count':0,
            'last_failtime':0,
            'token':token,
            'uid':uid,
            'platform':platform
        }

        rds = self.application.rds
        rds.srem('push:invaildtokens', token)
        r = rds.hmset(token_key,data)

        rds.lpush('queue_device',token)
        self.finish(chunk=r)

handlers = [(r"/device/register", DeviceRegisterHandler)]