#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

from utils import _default_mongo
from config import MONGO_DB_NAME, SUB_EVENTS_COLLECTION

class Event(object):
    """话题类
    """
    def __init__(self, id):
        """初始化话题实例，输入为话题ID，字符串类型
        """
        self.id = id
        self.name = None
        self.status = None
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def getSubEvents(self):
        """获取子事件，非其他类
        """
        other_subevent_id = self.getOtherSubEventID()
        results = self.mongo[SUB_EVENTS_COLLECTION].find({"eventid": self.id, "$not": {"_id": other_subevent_id}})

        return results

    def getOtherSubEventID(self):
        """获取其他类ID，该ID是预留的
           规则为eventid + '_other'
        """
        return self.id + '_other'
