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
        self.other_subeventid = self.getOtherSubEventID()
        self.news_collection = EVENTS_NEWS_COLLECTION_PREFIX + self.id
        self.sub_events_collection = SUB_EVENTS_COLLECTION
        self.events_collection = EVENTS_COLLECTION
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def getSubEvents(self):
        """获取子事件，非其他类
        """
        results = self.mongo[self.sub_events_collection].find({"eventid": self.id, "_id": {"$ne": self.other_subeventid}})

        return results

    def getInfos(self, start_ts, end_ts):
        """获取话题最新的文本
           input
               start_ts: 起始时间戳
               end_ts:   终止时间戳
        """
        results = self.mongo[self.news_collection].find({"timestamp": {"$gte": start_ts, "$lt": end_ts}})
        return results

    def getOtherSubEventID(self):
        """获取其他类ID，该ID是预留的
           规则为eventid + '_other'
        """
        return self.id + '_other'

    def terminate(self):
        """终止话题
        """
        self.mongo[self.events_collection].upsert({"_id": self.id}, {"$set": {"status": "terminate"}})

    def activate(self):
        """激活话题
        """
        self.mongo[self.events_collection].upsert({"_id": self.id}, {"$set": {"status": "active"}})

    def setStartts(self, startts):
        """更新话题起始时间
        """
        self.mongo[self.events_collection].upsert({"_id": self.id}, {"$set": {"startts": startts}})

    def setEndts(self, endts):
        """更新话题终止时间
        """
        self.mongo[self.events_collection].upsert({"_id": self.id}, {"$set": {"endts": endts}})

    def getAvgSubEventSize(self, timestamp):
        """获取子事件的平均大小
           input:
               timestamp: 截止的时间戳
        """
        func='''
                function(obj,prev)
                {
                    prev.count++;
                }
        '''
        results = self.mongo[self.news_collection].group({"subeventid": 1}, {"$and": [{"subeventid": {"$ne": None}}, {"subeventid": {"$ne": self.other_subeventid}}], 'timestamp': {'$lt': timestamp}}, {"count": 0}, func)
        count_list = [r['count'] for r in results]

        if len(count_list):
            avg = float(sum(count_list)) / float(len(count_list))
        else:
            avg = 0

        return avg

    def check_ifsplit(self, timestamp):
        """给定时间判断是否需要分裂子事件, 每小时执行一次
           input:
               timestamp: 截止时间戳, 整点
           output:
               True or False
        """
        avg_subevent_size = self.getAvgSubEventSize(timestamp)

        # 每天0、6、12、18时检测, 其他类存量文本数 > avg, 则分裂
        SIX_HOUR_SECONDS = 6 * 3600
        six_hour_threshold = avg_subevent_size
        if timestamp % SIX_HOUR_SECONDS == 0:
            other_subevent_news_count = self.mongo[self.news_collection].find({"timestamp": {"$lt": timestamp}, "subeventid": self.other_subeventid}).count()
            if other_subevent_news_count > six_hour_threshold:
                return True

        # 每小时检测，该小时内其他类文本数 > avg * 5 或 该小时内其他类文本数-上个小时内其他类文本数 > avg * 2, 则分裂
        one_hour_threshold = avg_subevent_size * 5
        one_hour_added_threshold = avg_subevent_size * 2
        count_in_hour = self.mongo[self.news_collection].find({"timestamp": {"$gte": timestamp - 3600, "$lt": timestamp}, "subeventid": self.other_subeventid}).count()
        count_before_hour = self.mongo[self.news_collection].find({"timestamp": {"$gte": timestamp - 7200, "$lt": timestamp - 3600}, "subeventid": self.other_subeventid}).count()
        added_count = count_in_hour - count_before_hour

        if count_in_hour > one_hour_threshold or added_count > one_hour_added_threshold:
            return True

        return False


if __name__ == "__main__":
    topicid = "54916b0d955230e752f2a94e"
    event = Event(topicid)

    now_ts = int(time.time())
    timestamp = now_ts - now_ts % 3600
    print event.getAvgSubEventSize(timestamp)
    print event.check_ifsplit(timestamp)

