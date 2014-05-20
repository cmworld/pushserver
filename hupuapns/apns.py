# -*- coding:utf-8 -*-
import httplib
import sys
from libs.logger import log

try:
    import json
except ImportError:
    import simplejson as json

class HTTPConnection(object):
    def __init__(self):
        super(HTTPConnection, self).__init__()
        self._conn = None
        self._timeout = 5

    def _connect(self):
        try:
            conn = httplib.HTTPConnection(self.server,self.port,False,timeout=self._timeout)
            conn.connect()
        except:
            e = sys.exc_info()
            log.error('connect server %s:%s faild: %s' % (self.server,self.port,e[1]))
            sys.exit()

        self._conn = conn

    def _connection(self):
        if not self._conn:
            self._connect()
        return self._conn

    def send(self,method, uri,params=None):
       
        conn = self._connection()
        #conn.set_debuglevel(1)
        headers = {
            "Content-Type":'application/json; charset=utf-8'
        }

        method = method.upper()
        if method == 'POST':
            params = json.dumps(params)

        try:
            conn.request(method, uri,params,headers)
            rsp = conn.getresponse()

            if rsp.status != 200:
                raise ValueError, 'status:%d' % rsp.status

            return rsp.read()

        except Exception:
            e = sys.exc_info()
            log.error("Apns send faild: %s \n %s,%s,%s,%s" % (e[1],method, uri, params,headers))
        finally:
            conn.close()

        return None


class ApnsClient(HTTPConnection):
    def __init__(self, **kwargs):
        super(ApnsClient, self).__init__(**kwargs)
#        self.server = '61.174.9.138'
        self.server = '192.168.1.84'
        self.port = 12320

    def send_notification(self,uri,payload):
        return self.send('POST',uri,payload)

    def get_feedback(self,uri):
        res = self.send('GET',uri)
        return json.loads(res)