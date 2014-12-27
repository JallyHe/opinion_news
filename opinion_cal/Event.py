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

    def getActiveEventIDs(self, timestamp):
        """获取活跃话题的ID
           input:
               timestamp: 检测的时间点, 话题的创建时间要小于检测的时间点
           output:
               活跃的话题ID
        """
        results = self.mongo[EVENTS_COLLECTION].find({"status": "active", "startts": {"$lte": timestamp}})
        return [r['_id'] for r in results]

    def terminateEvent(self, eventid, endts=int(time.time())):
        """终止事件
           input:
               eventid: 事件ID
               endts: 终止时间
        """
        event = Event(eventid)
        event.terminate()
        event.setEndts(endts)

    def getEventIDByName(self, name):
        result = self.mongo[EVENTS_COLLECTION].find_one({"topic": name})
        if result:
            return result['_id']
        else:
            return None

    def checkActive(self, timestamp):
        """根据话题新文本数检查话题的活跃性
           input:
               timestamp: 检测的时间点
           output:
               活跃的话题ID
        """
        active_ids = []
        ids = self.getActiveEventIDs(timestamp)
        for id in ids:
            event = Event(id)
            if event.check_ifactive():
                active_ids.append(id)
            else:
                event.terminate()
                event.setEndts(timestamp)

        return active_ids

    def getInitializingEventIDs(self, timestamp):
        """获取正在初始化的话题ID
           input:
               timestamp: 检测的时间点
           output:
               正在初始化的话题ID
        """
        print EVENTS_COLLECTION
        results = self.mongo[EVENTS_COLLECTION].find({"status": "initializing", "startts": {"$lte": timestamp}})
        return [r['_id'] for r in results]


class Event(object):
    """话题类
    """
    def __init__(self, id):
        """初始化话题实例，输入为话题ID，ObjectID
        """
        self.id = id
        self.other_subeventid = self.getOtherSubEventID()
        self.news_collection = EVENTS_NEWS_COLLECTION_PREFIX + str(id)
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
        return str(self.id) + '_other'

    def initializing(self):
        """初始化话题, 该状态下做初始聚类
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"status": "initializing"}})

    def activate(self):
        """激活话题
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"status": "active"}})

    def terminate(self):
        """终止话题
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"status": "terminate"}})

    def setStartts(self, startts):
        """更新话题起始时间
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"startts": startts}})

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

    def getInitialInfos(self):
        """获取初始聚类文本，默认取话题开始时间之前的文本
        """
        event = self.mongo[self.events_collection].find_one({"_id": self.id})
        start_ts = event["startts"]
        results = self.mongo[self.news_collection].find({"timestamp": {"$lt": start_ts}})
        return [r for r in results]

    def check_ifactive(self, timestamp, during=3600 * 24 * 3):
        """根据话题信息数在给定时间判断是否活跃
           input:
               timestamp: 截止时间戳
               during: 在during时间内没有新文本，则判定为不活跃
           output:
               True or False
        """
        if self.mongo[self.news_collection].find({"timestamp": {"$gte": timestamp - during, "$lt": timestamp}}).count():
            return True
        else:
            return False

    def check_ifsplit(self, timestamp):
        """给定时间判断其他类是否需要分裂子事件, 每小时执行一次
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

