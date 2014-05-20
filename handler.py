# -*- coding: utf-8 -*-

import traceback
import logging

from tornado import escape
from tornado.options import options
from tornado.web import RequestHandler as BaseRequestHandler, HTTPError

import exception
import md5
import sys

from ConfigParser import ConfigParser

class BaseHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        # enable GET request when enable delegate get to post
        if options.app_get_to_post:
            self.post(*args, **kwargs)
        else:
            raise exception.HTTPAPIError(405)

    def prepare(self):
        self.traffic_control()
        pass

    def traffic_control(self):
        # traffic control hooks for api call etc
        self.log_apicall()
        pass

    def log_apicall(self):
        pass


class RequestHandler(BaseHandler):
    pass


class APIHandler(BaseHandler):
    def get_current_user(self):
        pass

    def finish(self, chunk=None, code=200):
        if chunk is None:
            chunk = {}

        chunk = {"code": code, "response": chunk}

        self.set_header("Content-Type", "application/json; charset=UTF-8")
        super(APIHandler, self).finish(chunk)

    def write_error(self, status_code, **kwargs):
        """Override to implement custom error pages."""
        debug = self.settings.get("debug", False)
        try:
            exc_info = kwargs.pop('exc_info')
            e = exc_info[1]

            if isinstance(e, exception.HTTPAPIError):
                pass
            elif isinstance(e, HTTPError):
                e = exception.HTTPAPIError(e.status_code)
            else:
                e = exception.HTTPAPIError(500)

            exception_str = "".join([ln for ln in traceback.format_exception(*exc_info)])

            if status_code == 500 and not debug:
                logging.error("Internal Server Error: %s" % exception_str)

            if debug:
                e.response["exception"] = exception_str

            self.clear()
            self.set_status(200)  # always return 200 OK for API errors
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.finish(e.response,e.status_code)
        except Exception:
            logging.error(traceback.format_exc())
            return super(APIHandler, self).write_error(status_code, **kwargs)
    """
    @note validate the token time+privatekey
    @param post param
    @type
    @return 
    """
    def token_validate(self,ctime=''):
        config = ConfigParser()
        config.read('config.ini')
        privatekey = config.get('security', 'privatekey')
        md5_str = "%s%s" % (ctime,privatekey)
        md5_str_sign = self.hash_md5(strings = md5_str)
        return md5_str_sign
    #md5 the string
    def hash_md5(self, strings=''):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        strings.encode('utf-8')
        md5Obj =md5.new()
        md5Obj.update(strings)
        md5_str = md5Obj.hexdigest()
        return md5_str
        

class ErrorHandler(RequestHandler):
    #Default 404: Not Found handler.
    def prepare(self):
        super(ErrorHandler, self).prepare()
        raise HTTPError(404)


class APIErrorHandler(APIHandler):
    #Default API 404: Not Found handler.
    def prepare(self):
        super(APIErrorHandler, self).prepare()
        raise exception.HTTPAPIError(404)