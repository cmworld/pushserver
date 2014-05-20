# -*- coding: utf-8 -*-
import string
from libs.torndb import Connection

class Model(object):
    _dbs = None

    @classmethod
    def setup_dbs(cls, setting):
        cls._dbs = Connection(**setting)

    @property
    def db(self):
        return self._dbs

    def parse_dict(self,data,spilt=","):
        w = []
        for i in range(len(data)):
            key = data.keys()[i]
            val = data[key]
            if isinstance(val, list):
                s = "%s in ('%s')" % (str(key),"','".join(map(str,val)))
                w.append(s)
            else:
                w.append(str(key)+"='"+str(val)+"'")
        
        return string.join(w,spilt)