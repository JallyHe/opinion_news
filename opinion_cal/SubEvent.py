#-*-coding=utf-8-*-


from utils import _default_mongo
from config import MONGO_DB_NAME

class SubEvent(object):
    def __init__(self, id):
        self.id = id
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)
