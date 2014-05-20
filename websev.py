#!/usr/bin/env python
# -*- coding:utf-8 -*-
try:
    import json
except ImportError:
    import simplejson as json

import time

import os.path 
import tornado.httpserver  
from tornado import web 
from tornado.ioloop import IOLoop
from tornado.options import options 

from libs import importlib

def handler_patterns(root_module, handler_names, prefix=""):
    handlers = []

    for name in handler_names:

        module = importlib.import_module(".%s" % name, root_module)
        module_hanlders = getattr(module, "handlers", None)

        if module_hanlders:
            _handlers = []
            for handler in module_hanlders:
                try:
                    patten = r"%s%s" % (prefix, handler[0])
                    if len(handler) == 2:
                        _handlers.append((patten,
                                          handler[1]))
                    elif len(handler) == 3:
                        _handlers.append(web.url(patten,
                                             handler[1],
                                             name=handler[2])
                                         )
                    else:
                        pass
                except IndexError:
                    pass

            handlers.extend(_handlers)
    return handlers

class Application(web.Application):  
    def __init__(self,serv):

        settings = dict(  
            template_path = os.path.join(os.path.dirname(__file__), "templates"),   
            static_path = os.path.join(os.path.dirname(__file__), "static"),   
            debug = True  
        )        

        handler_names = ["device","message","ad","static"]
        handlers = handler_patterns("handlers", handler_names,"/api")

        self.serv = serv
        self.conf = serv.conf
        self.rds = serv.rds

        super(Application, self).__init__(handlers, **settings)

def start_httpserver(serv):
    port = serv.conf.get('http_port',8888)

    print 'pushserver running on port %d ...' % port
 
    app = tornado.httpserver.HTTPServer(Application(serv),xheaders=True)  
    app.listen(int(port))

    IOLoop.instance().start()
#    autoload the py change
#    loop = tornado.ioloop.IOLoop.instance()
#    tornado.autoreload.start(loop)
#    loop.start()
def run_server(port = 8888):
    print 'pushserver running on port %d ...' % port
    
    app = tornado.httpserver.HTTPServer(Application(),xheaders=True)  
    app.listen(int(port))

    IOLoop.instance().start()

if __name__ == '__main__':
    run_server()