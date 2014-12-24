#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

from utils import _default_mongo
from config import MONGO_DB_NAME

class SubEvent(object):
    def __init__(self, id):
        self.id = id
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)
