# -*- coding:utf-8 -*-
import hashlib
import time
import exception

from handler import APIHandler
from model.model_device import DeviceModel

class MessagePushHandler(APIHandler):
    def get(self):
        self.finish(chunk='')
            
    def post(self):
        title = self.get_argument("title", "").strip()
        message = self.get_argument("message", "").strip()
        expire = self.get_argument("expire", '0')
        url = self.get_argument("url", '')
        platform = self.get_argument("platform",'')
        tokens = self.get_argument("tokens", '')
        
        if not title or not message:
            raise exception.HTTPAPIError(status_code=400)

        if platform and (platform not in ['android','iphone']):
            raise exception.HTTPAPIError(status_code=400,error_detail="params platform Invalid")

        
        tokenlist = []
        if tokens:
            tokenlist = tokens.split(",")

        rds = self.application.rds
        device = DeviceModel()

        md5str = '%s%s' % (title,message)
        md5str = md5str.encode('utf-8')
        letter_key = hashlib.md5(md5str).hexdigest()

        push_msg = {
            'title': title,
            'message' : message,
            'expire' : expire,
            'url' : url
        }
        #sign validata ctime+privatekey
        post_md5_sign    = self.get_argument("sign", '')
        post_ctime        = self.get_argument("ctime", '')
        md5_sign          = self.token_validate(post_ctime)
        if post_md5_sign != md5_sign:
            raise exception.HTTPAPIError(status_code=403,error_detail='sign is error')
        
        

        if rds.hmset('message:info:%s' % letter_key ,push_msg):
            score = int(time.time())
            rds.zadd('message:list',letter_key,score)            

        where = {'enable':1}
        if len(tokenlist) > 0:
            where['token'] = tokenlist

        if platform:
            where['platform'] = platform

        rows = device.get_devices(where,1)
        for row in rows:
            token = row.get('token')
            if row.get('platform') == 'iphone':
                rds.lpush('push:queue:ios:%s' % letter_key ,token)
            elif row.get('platform') == 'android':
                rds.lpush('push:queue:droid:%s' % letter_key ,token)

        self.finish('ok')

handlers = [(r"/message/push", MessagePushHandler)]