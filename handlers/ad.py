# -*- coding:utf-8 -*-
import re
import time
import hashlib
import exception


from handler import APIHandler
#from model.model_ad import AdModel

class AdPushHandler(APIHandler):
    def get(self):
        self.finish(chunk='')

    def post(self):
        title = self.get_argument("title", "").strip()
        picurl = self.get_argument("picurl", "").strip()
        linkurl = self.get_argument("linkurl", '')
        adtype = self.get_argument("adtype", '')
        adslug = self.get_argument("adslug", '')
        sort_order = self.get_argument("sort_order", 0)
        inspire = self.get_argument("inspire", 0)
        expire = self.get_argument("expire", 0)
        sign   = self.get_argument("sign",'');
        #enable = self.get_argument("enable", 0)
        if not adtype or not title:
            raise exception.HTTPAPIError(status_code=400,error_detail='params title,adtype should not be empty')

        if adtype not in ['cpa','cpm']:
            raise exception.HTTPAPIError(status_code=400,error_detail='params adtype Invalid')

        if not linkurl or not picurl:
            raise exception.HTTPAPIError(status_code=400,error_detail='params picurl,linkurl should not be empty')

        regex = re.compile(r'^(?:http)s?://')
        if not regex.match(picurl):
            raise exception.HTTPAPIError(status_code=400,error_detail='params picurl Invalid')

        if not regex.match(linkurl):
            raise exception.HTTPAPIError(status_code=400,error_detail='params linkurl Invalid')

        if isinstance(inspire,str) or isinstance(expire,str):
            raise exception.HTTPAPIError(status_code=400,error_detail='params inspire or expire Invalid')

        timenow = int(time.time())
        if inspire == 0:
            inspire = timenow

        if expire == 0:
            expire = timenow + 3600 * 24
        
        if inspire >= expire:
            raise exception.HTTPAPIError(status_code=400,error_detail='params inspire or expire Invalid')
       
        if not adslug:
            md5str = '%s%s%d' % (title,picurl,timenow)
            md5str = md5str.encode('utf-8')
            adhash = hashlib.md5(md5str).hexdigest()
            adslug = '%s_%s' % (adtype,adhash[0:8])       

        rds = self.application.rds
        
        key = 'push:ad:info:%s' % adslug
        if rds.exists(key):
            raise exception.HTTPAPIError(status_code=500,error_detail='the adslug %s has exists' % adslug)

        ad_data = {
            'title': title,
            'picurl' : picurl,
            'linkurl' : linkurl,
            'adslug' : adslug,
            'adtype' : adtype,
            'inspire' : inspire,
            'expire' : expire,
            'sign': sign,
            'sort_order' : sort_order,
            'enable' : 0,
            'isclosed' : 0,
            'createtime' : timenow,
        }
#        sign validate
        post_md5_sign    = ad_data.get('sign')
        post_ctime        = self.get_argument("ctime", '')
        md5_sign = self.token_validate(post_ctime)
        if post_md5_sign != md5_sign:
            raise exception.HTTPAPIError(status_code=403,error_detail='sign is error')
        #ad = AdModel()
        #ad_id = ad.add_ad(**ad_data)

        #delete other
        adrows = rds.zrange('push:ad:list',0,-1)
        for adkey in adrows:
            rds.delete(adkey) 
        rds.delete('push:ad:list')

        rds.hmset(key,ad_data)
        rds.zadd('push:ad:list',key,sort_order)

        self.finish(chunk='ok')

class AdPopHandler(APIHandler):
    def get(self):
        rds = self.application.rds
        #ad = AdModel()

        adcount = rds.zcard('push:ad:list')

        ad = {}
        if adcount > 0:
            timenow = int(time.time())
            adrows = rds.zrange('push:ad:list',0,-1)
            for adkey in adrows:
                ad = rds.hgetall(adkey)

                if int(ad.get('isclosed')) == 1:
                    ad = {}
                    continue;

                if int(ad['expire']) > timenow:
                    rds.hset(adkey,'enable','1')
                    ad['enable'] = 1
                    break;
                else:
                    rds.hset(adkey,'isclosed','1')
                    ad = {}

        res = {}
        if ad:
            res = {
                'enable' : ad['enable'],
                'title' : ad['title'],
                'sort_order' : ad['sort_order'],
                'adtype': ad['adtype'],
                'picurl':  ad['picurl'],
                'linkurl': ad['linkurl']
            }
        self.finish(chunk=res)

class AdListHandler(APIHandler):
    def get(self):

        rds = self.application.rds
        adcount = rds.zcard('push:ad:list')

        ads = []
        if adcount > 0:
            adrows = rds.zrange('push:ad:list',0,-1)

            for adkey in adrows:
                adrow = rds.hgetall(adkey) 
                ads.append(adrow)

        self.finish(chunk=ads)


handlers = [(r"/ad/push", AdPushHandler),
            (r"/ad/pop", AdPopHandler),
            (r"/ad/list", AdListHandler)
            ]