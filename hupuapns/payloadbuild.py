# -*- coding:utf-8 -*-

try:
    import json
except ImportError:
    import simplejson as json

"""
payload_json = {
    'tokens' : tokens,
    'expiry' : int(time.time()) + 3600,
    'payload' : {
		'aps': {
			'alert': {
				'body': "alert message",
				'action-loc-key': "",
				'loc-key': "",
				'loc-args': "",
				'launch-image': "",
			},
			'badge': 3,
			'sound': "",
		},
		'url': "",
		'args': "",
    }
}
"""

class Alert(object):
    def __init__(self, body, title=None, action_loc_key=None, loc_key=None,loc_args=None, launch_image=None):
        super(Alert, self).__init__()
        self.body = body
        self.title = title
        self.action_loc_key = action_loc_key
        self.loc_key = loc_key
        self.loc_args = loc_args
        self.launch_image = launch_image

    def dict(self):
        d = {'body': self.body}
        if self.title:
            d['title'] = self.title
        if self.action_loc_key:
            d['action-loc-key'] = self.action_loc_key
        if self.loc_key:
            d['loc-key'] = self.loc_key
        if self.loc_args:
            d['loc-args'] = self.loc_args
        if self.launch_image:
            d['launch-image'] = self.launch_image
        return d

class Payload(object):

    def __init__(self, alert=None, badge=None, sound=None, custom={}):
        super(Payload, self).__init__()
        self.alert = alert
        self.badge = badge
        self.sound = sound
        self.custom = custom

    def dict(self):
    	d = {}
        if self.alert:
            if isinstance(self.alert, Alert):
                d['alert'] = self.alert.dict()
            else:
                d['alert'] = self.alert
        if self.sound:
            d['sound'] = self.sound
        if self.badge:
            d['badge'] = int(self.badge)

        d = {'aps': d}
        d.update(self.custom)
        return d

    def json(self):
        return json.dumps(self.dict(), separators=(',', ':'))

    def __repr__(self):
        attrs = ("alert", "badge", "sound", "custom")
        args = ", ".join(["%s=%r" % (n, getattr(self, n)) for n in attrs])
        return "%s(%s)" % (self.__class__.__name__, args)