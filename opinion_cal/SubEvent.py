#-*-coding=utf-8-*-

from utils import _default_mongo

class SubEvent(object):
    def __init__(self):
        self.id = None
        self.mongo = _default_mongo()

