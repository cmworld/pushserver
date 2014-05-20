# -*- coding:utf-8 -*-
import sys
import time

try:
    import json
except ImportError:
    import simplejson as json

import redis
import _mysql_exceptions

from hupuapns import apns
from hupuapns import payloadbuild
from libs.logger import log

from model.model_device import DeviceModel

class Notifier(object):
    def __init__(self, conf=None,channel=None,platform=None,pkn=None):

        self.conf = conf
        self.channel = channel
        self.platform = platform
        self.pkn = pkn

        self.alive = True
        self.retry_time_max = 5
        self.retry_time = 0
        self.max_push = 2000

        self.apns = apns.ApnsClient()

    def _rds_connect(self):
        rds = None
        try:
            setting = self.conf.get('redis', {})
            rds = redis.Redis(host=setting['host'],port=int(setting['port']),db=setting['db'])
            if rds.ping() == False:
                raise
        except:
            log.error('Failed: Redis Connection refused.')
            self.alive = False
        return rds

    def run(self):
        log.debug('thread %s running' % self.channel)

        self.rds = self._rds_connect()
        self.push_loop()

    def flash_letter(self):
        letter_list = self.rds.zrange('message:list',0,0)

        if not letter_list:
            log.debug('thread %s flash_letter get none...' % self.channel)
            return None,None

        letter_key = letter_list[0]
        letter_info = self.rds.hgetall('message:info:%s' % letter_key)
        if not letter_info:
            return None,None

        log.debug('thread %s flash_letter get %s ' % (self.channel,letter_key))
        
        tokens = []
        while(1):
            token = self.rds.rpop('push:queue:%s:%s' % (self.platform,letter_key))
            if not token:
                break

            if self.rds.sismember('push:invaildtokens',token):
                continue
            
            tokens.append(token)
            if len(tokens) < self.max_push:
                continue

            break

        if not len(tokens):
            log.debug('thread %s no tokens, clean message' % self.channel)
            self.rds.delete('push:queue:%s:%s' % (self.platform,letter_key))
            self.rds.delete('message:info:%s' % letter_key)
            self.rds.zrem('message:list', letter_key)
            return None,None

        
        return letter_info,tokens
        

    def push_loop(self):
        log.debug('thread %s init loop' % self.channel)

        while(self.alive):
            try:             
                letter_info,tokens = self.flash_letter()
                if not letter_info or not tokens or not len(tokens):
                    time.sleep(2)
                    continue

                self.push_message(tokens,letter_info)
            except Exception:
                e = sys.exc_info()
                log.error("push message faild: %s" % e[1])
                
                if self.retry_time <= self.retry_time_max:
                    time.sleep(10)
                    self.retry_time = self.retry_time + 1
                    log.debug('thread %s retry %d' % (self.channel,self.retry_time))
                    self.push_loop()
                else:
                    break
                    
            time.sleep(2)

        log.error('thread %s leaving...' % self.channel)


    def push_message(self,tokens,data):

        log.debug('thread %s pushing message' % self.channel)

        try:
            title = data.get('title','')
            message = data.get('message','')
            expiry = data.get('expiry',3600)

            params ={}

            if self.platform == 'ios':
                message = '%s , %s' % (title,message)
                alert = payloadbuild.Alert(message,**params)
            else:
                alert = payloadbuild.Alert(message,title,**params)
            
            payload_params = {
                'alert' : alert,
                'badge' : '',
                'sound' : 0
            }

            if data.get('url',None):
                payload_params['custom'] = {'url':data['url']}

            payload = payloadbuild.Payload(**payload_params)

            p = {
                'expiry' : int(time.time()) + int(expiry),
                'payload' : payload.dict()
            }

            if self.platform == 'ios':
                p.update({'tokens' : tokens})
            else:
                p.update({'clients' : tokens})

            uri = '/%s/notific/%s' % (self.platform,self.pkn)
            r = self.apns.send_notification(uri,p)
            print r

        except Exception:
            e = sys.exc_info()
            log.error("push message faild: %s" % e[1])


class FeedbackRater(object):
    def __init__(self, conf=None,channel=None,platform=None,pkn=None):
        self.TOKEN_MAX_FAIL_TIME = 10
        self.channel = channel
        self.platform = platform
        self.pkn = pkn

        self.alive = True
        self.conf = conf
        self.apns = apns.ApnsClient()

    def _rds_connect(self):
        rds = None
        try:
            setting = self.conf.get('redis', {})
            rds = redis.Redis(host=setting['host'],port=int(setting['port']),db=setting['db'])
            if rds.ping() == False:
                raise
        except:
            log.error('Failed: Redis Connection refused.')
            self.alive = False
        return rds

    def _db_connect(self):
        from model import Model
        try:
            setting = self.conf.get('database', {})
            Model.setup_dbs(setting)
        except:
            e = sys.exc_info()
            log.error("Cannot connect to MySQL: %s" % e[1])
            sys.exit(2)       

    def run(self):
        log.debug('thread %s running' % self.channel)

        self.rds = self._rds_connect()

        uri = '/%s/feedback/%s' % (self.platform,self.pkn)

        while(self.alive):
            try:
                tokens = self.apns.get_feedback(uri)
                if tokens != None:
                    log.debug('thread %s get feedback tokens' % self.channel)
                    for token in tokens:
                        count = self.rds.hincrby('tokens:info:%s' % token[1] , 'fail_count')
                        count = self.rds.hincrby('tokens:info:%s' % token[1] , 'last_failtime',token[0])
                        
                        if int(count) >= self.TOKEN_MAX_FAIL_TIME:
                            self.handle_bad_token(token[1])
            except:
                e = sys.exc_info()
                log.error('get feedback fail: %s' % e[1])
            time.sleep(60*60)

        log.debug('i am leaving feedback')

    def handle_bad_token(self,token):
        log.debug('thread %s handle bad_token %s' % (self.channel,token))
        device = DeviceModel()
        try:
            device.update_device({'enable':0},{'token':token})
            self.rds.sadd('push:invaildtokens', token)
        except _mysql_exceptions.OperationalError:
            self._db_connect()
            self.handle_bad_token(token)
        except:
            e = sys.exc_info()
            log.error("Handle Bad Token Failed: %s" % e[0])



