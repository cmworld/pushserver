# -*- coding:utf-8 -*-
import sys
import time
import traceback
import _mysql_exceptions
from libs.logger import log
from model.model_device import DeviceModel

class DeviceCache(object):

    def __init__(self,serv):
        self.rds = serv.rds
        self.conf = serv.conf

    def run(self):
    	self.loop_cache2db()

    def _db_connect(self):
        from model import Model
        try:
            setting = self.conf.get('database', {})
            Model.setup_dbs(setting)
        except:
            e = sys.exc_info()
            log.error("Cannot connect to MySQL: %s" % e[1])
            sys.exit(2)

    def loop_cache2db(self):
        log.debug('device queue init')
        device = DeviceModel()

        while(1):
            token = self.rds.rpop('queue_device')
            if not token:
                time.sleep(1)
                continue
            
            try:
                cache = self.rds.hgetall('tokens:info:%s' % token)

                row = device.get_deviceByToken(token)
                if not row:
                    createtime = int(time.time())
                    device.add_device(cache['platform'],token,cache['uid'],cache['pushset'],1,createtime)
                else:
                    update = {
                        'enable':1,
                        'uid':cache['uid'],
                        'pushset':cache['pushset']
                    }

                    device.update_device(update,{'pid':row['pid']})
            except _mysql_exceptions.OperationalError:
            	log.error('mysql reconnect ...')
                self._db_connect()
                self.loop_cache2db()
            except:
                excinfo = traceback.format_exc()
                log.error('update device %s faild: %s' % (token,excinfo))               

            time.sleep(1)

    def loop_db2cache(self):
        device = DeviceModel()
        rows = device.get_devices()
        for row in rows:
            token = row.get('token')
            self.rds.hmset('tokens:info:%s' % token ,row)
