#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

import time
from utils import _default_mongo
from config import MONGO_DB_NAME, SUB_EVENTS_COLLECTION, \
        EVENTS_NEWS_COLLECTION_PREFIX, EVENTS_COLLECTION


class EventManager(object):
    """话题管理类
    """
    def __init__(self):
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def getActiveEvents(self):
        return self.mongo[EVENTS_COLLECTION].find({"status": "active"})

    def terminateEvent(self, eventid, endts=int(time.time())):
        event = Event(eventid)
        event.terminate()
        event.setEndts(endts)

    def getEventByName(self, name):
        return self.mongo[EVENTS_COLLECTION].find_one({"name": name})

    def upsertEvent(self, name, startts=int(time.time()), status="active"):
        pass


class Event(object):
    """话题类
    """
    def __init__(self, id):
        """初始化话题实例，输入为话题ID，字符串类型
        """
        self.id = id
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def getSubEvents(self):
        """获取子事件，非其他类
        """
        other_subevent_id = self.getOtherSubEventID()
        print other_subevent_id
        results = self.mongo[SUB_EVENTS_COLLECTION].find({"eventid": self.id, "_id": {"$ne": other_subevent_id}})

        return results

    def getInfos(self, start_ts, end_ts):
        """获取话题最新的文本
           input
               start_ts: 起始时间戳
               end_ts:   终止时间戳
        """
        results = self.mongo[EVENTS_NEWS_COLLECTION_PREFIX + self.id].find({"timestamp": {"$gte": start_ts, "$lt": end_ts}})
        return results

    def getOtherSubEventID(self):
        """获取其他类ID，该ID是预留的
           规则为eventid + '_other'
        """
        return self.id + '_other'

    def terminate(self):
        """终止话题
        """
        self.mongo[EVENTS_COLLECTION].upsert({"_id": self.id}, {"$set": {"status": "terminate"}})

    def activate(self):
        """激活话题
        """
        self.mongo[EVENTS_COLLECTION].upsert({"_id": self.id}, {"$set": {"status": "active"}})

    def setStartts(self, startts):
        """更新话题起始时间
        """
        self.mongo[EVENTS_COLLECTION].upsert({"_id": self.id}, {"$set": {"startts": startts}})

    def setEndts(self, endts):
        """更新话题终止时间
        """
        self.mongo[EVENTS_COLLECTION].upsert({"_id": self.id}, {"$set": {"endts": endts}})

