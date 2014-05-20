#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
import os

_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(_root)

import threading
import redis

from ConfigParser import ConfigParser
from libs.notifiertion import Notifier,FeedbackRater
from libs.logger import log,create_log,console_log
from model import Model
from websev import start_httpserver

from device import DeviceCache

class CacheGuard(object):
    def __init__(self,conf):
        self.conf = conf
        self.notifiers = {}

        try:
            setting = conf.get('database', {})
            Model.setup_dbs(setting)
        except:
            e = sys.exc_info()
            log.error("Cannot connect to MySQL: %s" % e[1])
            sys.exit(2)

        try:
            setting = conf.get('redis', {})
            self.rds = redis.Redis(host=setting['host'],port=int(setting['port']),db=setting['db'],socket_timeout=3)
            if self.rds.ping() == False:
                raise
        except:
            e = sys.exc_info()
            log.error("'Redis Connection refused: %s" % e[1])
            sys.exit(2)
       

    def run(self):
        log.debug("building cache...")
        Dcache = DeviceCache(self)
        try:
            Dcache.loop_db2cache()
        except:
            e = sys.exc_info()
            log.error('buiding cache fail: %s' % e[1])
            sys.exit()

        self.deviceloop()
        self.start_worker()
        start_httpserver(self)

    def start_worker(self):
        kwargs = {
            'conf':self.conf
        }

        apps = conf.get('apps', {})

        workers = []
        for platform,pkn in apps.items():
            params = kwargs.copy()
            params.update({'platform': platform})
            params.update({'pkn': pkn})

            push_worker = threading.Thread(target=self.push, kwargs=params)
            workers.append(push_worker)

            feedback_worker = threading.Thread(target=self.feedback, kwargs=params)
            workers.append(feedback_worker)

        for w in workers:
            w.setDaemon(True)
            w.start()

    def stop_worker(self):
        for i in self.notifiers:
            self.notifiers[i].alive = False
            del self.notifiers[i]

    def push(self,conf,platform,pkn):
        channel = "push:%s:%s" % (platform,pkn)
        notifier = Notifier(conf,channel,platform,pkn)
        self.notifiers[channel] = notifier
        notifier.run()

    def feedback(self,conf,platform,pkn):
        channel = "feedback:%s:%s" % (platform,pkn)
        notifier = FeedbackRater(conf,channel,platform,pkn)
        self.notifiers[channel] = notifier
        notifier.run()

    def deviceloop(self):
        dl = threading.Thread(target=self.devicecache)
        dl.setDaemon(True)
        dl.start()

    def devicecache(self):
        dc = DeviceCache(self)
        dc.run()

if __name__ == '__main__':

    args = sys.argv
    if len(args) < 2:
        print 'Failed: Configuration file is not specified'
        sys.exit(2)

    conf_file = args[1] #os.getcwd() + '/config.ini'
    if not os.path.isfile(conf_file):
        print 'Failed: Cann\'t found file "%s".' % conf_file
        sys.exit(2)

    config = ConfigParser()
    config.read(conf_file)

    log_level = int(config.get('setting', 'log_level'))
    log_file = config.get('setting', 'log_file')
    if log_file:
        create_log(log_file,log_level)
    else:
        console_log(log_level)

    conf = {}

    for section in config.sections():
        sec = {}
        items = config.items(section)  
        for item in items:
            sec.update({item[0]:item[1]})
        conf.update({section:sec})


    guard = CacheGuard(conf)
    guard.run()   