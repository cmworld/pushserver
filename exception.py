# -*- coding: utf-8 -*-

#from tornado import escape
from tornado.web import HTTPError

_error_types = {400: "param_error",
                401: "invalid_auth",
                403: "not_authorized",
                404: "endpoint_error",
                405: "method_not_allowed",
                500: "server_error"}


class HTTPAPIError(HTTPError):

    def __init__(self, status_code=400, error_detail="", error_type="",
                 notification="", response="", log_message=None, *args):

        super(HTTPAPIError, self).__init__(int(status_code), log_message, *args)

        self.error_type = error_type if error_type else \
            _error_types.get(self.status_code, "unknow_error")
        self.error_detail = error_detail
        self.response = {
            "errorType": self.error_type,
            "errorDetail" : self.error_detail
        }