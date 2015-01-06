#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-28 14:00:00
# Version: 0.3.0
"""数据库操作的封装
"""

import time
from utils import _default_mongo
from config import MONGO_DB_NAME, SUB_EVENTS_COLLECTION, \
        EVENTS_NEWS_COLLECTION_PREFIX, EVENTS_COLLECTION, \
        SUB_EVENTS_FEATURE_COLLECTION


class EventManager(object):
    """话题管理类
    """
    def __init__(self):
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def getFalseEventIDs(self):
        """获取最近更新不成功的eventid
        """
        results = self.mongo[EVENTS_COLLECTION].find({"status": "active", "modify_success": False})
        return [r['_id'] for r in results]

    def getAllEventIDs(self):
        """
        """
        results = self.mongo[EVENTS_COLLECTION].find()
        return [r['_id'] for r in results]

    def getActiveEventIDs(self):
        """获取活跃话题的ID
           input:
           output:
               活跃的话题ID
        """
        results = self.mongo[EVENTS_COLLECTION].find({"status": "active"})
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

    def checkActive(self):
        """根据话题新文本数检查话题的活跃性, 更新不再活跃的话题的status
           input:
           output:
               活跃的话题ID
        """
        active_ids = []
        ids = self.getActiveEventIDs()
        for id in ids:
            event = Event(id)
            last_modify = event.getLastmodify()
            timestamp = last_modify + 3600
            if event.check_ifactive():
                active_ids.append(id)
            else:
                event.terminate()
                event.setEndts(timestamp)

        return active_ids

    def getInitializingEventIDs(self):
        """获取正在初始化的话题ID
           input:
           output:
               正在初始化的话题ID
        """
        results = self.mongo[EVENTS_COLLECTION].find({"status": "initializing"})
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
        return [r for r in results]

    def getSubeventInfos(self, subeventid):
        """获取一个子事件的相关信息
        """
        results = self.mongo[self.news_collection].find({"subeventid": subeventid})
        return [r for r in results]

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

    def initialize(self, start_ts):
        """一键初始化, 对event表的操作
           input:
               start_ts: 事件开始的时间戳
        """
        self.initstatus()
        self.setStartts(start_ts)
        self.setLastmodify(start_ts - 3600)
        self.setModifysuccess(True)
        self.clear_news_label()

        subevents = self.getSubEvents()
        for subevent in subevents:
            feature = Feature(subevent["_id"])
            feature.clear_all_features()

        self.clear_subevents()

    def initstatus(self):
        """设置状态为initializing, 该状态下即将做初始聚类
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"status": "initializing"}})

    def activate(self):
        """激活话题, 让话题进入演化状态
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
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"endts": endts}})

    def setModifysuccess(self, modify_success):
        """更新事件的modify_success, 表示是否修改成功
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"modify_success": modify_success}})

    def setLastmodify(self, timestamp):
        """更新事件的最后修改时间戳，整点, last_modify
        """
        self.mongo[self.events_collection].update({"_id": self.id}, {"$set": {"last_modify": timestamp}})

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

    def getInitialInfos(self, during=3600 * 24 * 30):
        """获取初始聚类文本，默认取话题开始时间之前往前推一个月的文本
        """
        event = self.mongo[self.events_collection].find_one({"_id": self.id})
        start_ts = event["startts"]
        results = self.mongo[self.news_collection].find({"timestamp": {"$gte": start_ts - during, "$lt": start_ts}})
        return [r for r in results]

    def getOtherSubEventInfos(self, initializing=False):
        """
           初始化：其他类文本取往前推30天的
           24h: 前两天其他类文本 + 当天其他类文本（已做扔回处理)
           1h: 当天凌晨到该小时内其他类文本
           output:
               cluster_num: 聚类数量
               results: 新闻字典list
               reserve_num: 评价时取的tfidf最大的类个数
        """
        import math
        MAX_CLUSTER_NUM = 10
        MIN_CLUSTER_NUM = 5

        last_modify = self.getLastmodify()
        timestamp = last_modify + 3600
        now_hour = int(time.strftime('%H', time.localtime(timestamp)))

        if initializing:
            results = self.mongo[self.news_collection].find({"subeventid": self.other_subeventid, "timestamp": {"$lt": timestamp}})

        elif now_hour == 0:
            results = self.mongo[self.news_collection].find({"timestamp": {"$gte": timestamp - 24 * 3600 * 3, "$lt": timestamp}, "subeventid": self.other_subeventid})

        else:
            zero_timestamp = timestamp - now_hour * 3600 # 当天0时
            results = self.mongo[self.news_collection].find({"timestamp": {"$gte": zero_timestamp, "$lt": timestamp}, "subeventid": self.other_subeventid})

        results = [r for r in results]
        items_length = len(results)

        cluster_num = int(math.ceil(float(items_length) / 20.0))

        if cluster_num < MIN_CLUSTER_NUM:
            cluster_num = MIN_CLUSTER_NUM

        if cluster_num > MAX_CLUSTER_NUM:
            cluster_num = MAX_CLUSTER_NUM

        reserve_num = int(math.ceil(float(cluster_num) / 2.0))

        return results, cluster_num, reserve_num

    def getLastmodify(self):
        """事件的最后修改时间戳, last_modify
        """
        result = self.mongo[self.events_collection].find_one({"_id": self.id})
        return result['last_modify']

    def check_ifactive(self, during=3600 * 24 * 3):
        """根据话题信息数在给定时间判断是否活跃
           input:
               during: 在last_modify + 3600 往前推during时间内没有新文本，则判定为不活跃
           output:
               True or False
        """
        last_modify = self.getLastmodify()
        if self.mongo[self.news_collection].find({"timestamp": {"$gte": last_modify + 3600 - during, "$lt": last_modify + 3600}}).count():
            return True
        else:
            return False

    def remove_subevents(self, ids):
        """移除subevents
        """
        self.mongo[self.sub_events_collection].remove({"_id": {"$in": ids}})
        self.mongo[SUB_EVENTS_FEATURE_COLLECTION].remove({"subeventid": {"$in": ids}})

    def getTodayCreatSubeventIds(self):
        """当天（大于0时小于timestamp时）产生的簇（非其他簇）
        """
        import time
        last_modify = self.getLastmodify()
        timestamp = last_modify + 3600
        now_hour = int(time.strftime('%H', time.localtime(timestamp)))
        if now_hour == 0:
            zero_timestamp = timestamp - 24 * 3600
        else:
            zero_timestamp = timestamp - now_hour * 3600 # 当天0时

        results = self.mongo[self.sub_events_collection].find({"eventid": self.id, "timestamp": {"$gt": zero_timestamp, "$lte": timestamp}})

        return [r["_id"] for r in results]

    def getTodayCreatSubeventInfos(self):
        """当天（大于0小于timestamp时）产生的簇（非其他簇）下的文本
        """
        subeventids = self.getTodayCreatSubeventIds()
        results = self.mongo[self.news_collection].find({"subeventid": {"$in": subeventids}})

        return [r for r in results]

    def check_ifsplit(self, initializing=False):
        """给定时间判断其他类是否需要分裂子事件, 每小时执行一次
           input:
               timestamp: 截止时间戳, 整点
               initializing: 是否在初始化
           output:
               True or False
        """
        import time
        if initializing:
            return True

        last_modify = self.getLastmodify()
        timestamp = last_modify + 3600
        now_hour = int(time.strftime('%H', time.localtime(timestamp)))

        if now_hour == 0:
            # 24时检测前两天其他类文本+当天没有被分到当天0时之前产生的簇的文本>30
            count = self.mongo[self.news_collection].find({"timestamp": {"$gte": timestamp - 24 * 3600 * 3, "$lt": timestamp}, "subeventid": self.other_subeventid}).count()
            print timestamp, now_hour, count
            if count > 30:
                return True

        else:
            # 每小时判断0时至当前点其他类文本数是否大于10, 大于10则分裂
            zero_timestamp = timestamp - now_hour * 3600 # 当天0时
            count = self.mongo[self.news_collection].find({"subeventid": self.other_subeventid, "timestamp": {"$gte": zero_timestamp, "$lt": timestamp}}).count()
            print timestamp, now_hour, count
            if count > 10:
                return True

        return False

    def checkLastModify(self):
        """检测最后一次修改时间是否在检测的时间点之前，最后一次修改是否成功
           input:
               timestamp: 检测的时间戳，整点
           output:
               True or False
        """
        last_modify = self.getLastmodify()
        timestamp = last_modify + 3600
        result = self.mongo[self.events_collection].find_one({"_id": self.id})
        if 'last_modify' not in result and result['startts'] < timestamp:
            # 可能是initializing的状态
            return True
        elif 'last_modify' in result and result['last_modify'] < timestamp \
                and 'modify_success' in result and result['modify_success']:
            return True
        else:
            return False

    def save_subevent(self, _id, timestamp):
        """保存子事件
           input:
                _id: 子事件ID
                timestamp: 子事件创建时间戳
        """
        subevent = {"_id": _id, "eventid": self.id, "timestamp": timestamp}
        return self.mongo[self.sub_events_collection].save(subevent)

    def clear_subevents(self):
        """清除子事件表中话题的相关子事件信息
        """
        self.mongo[self.sub_events_collection].remove({"eventid": self.id})

    def clear_news_label(self):
        """清除话题的所有新闻的clear_labels字段
        """
        clear_labels = ['subeventid', 'weight', 'duplicate', 'same_from']
        results = self.mongo[self.news_collection].find()
        for r in results:
            for key in clear_labels:
                if key in r:
                    del r[key]
            self.mongo[self.news_collection].update({"_id": r["_id"]}, r)

    def update_subevent_size(self, subeventid, size):
        """更新子事件的大小
        """
        self.mongo[SUB_EVENTS_COLLECTION].update({"_id": subeventid}, {"$set": {"size": size}})

    def get_subevent_size(self, subeventid):
        """获取子事件的大小
        """
        result = self.mongo[SUB_EVENTS_COLLECTION].find_one({"_id": subeventid})
        if result:
            if "size" in result:
                return result["size"]

        return 0

    def update_subevent_addsize(self, subeventid, addsize):
        """更新子事件的增幅
        """
        self.mongo[SUB_EVENTS_COLLECTION].update({"_id": subeventid}, {"$set": {"addsize": addsize}})

    def update_subevent_tfidf(self, subeventid, tfidf):
        """更新子事件的tfidf
        """
        self.mongo[SUB_EVENTS_COLLECTION].update({"_id": subeventid}, {"$set": {"tfidf": tfidf}})

    def get_min_tfidf(self):
        """获取最小的tfidf
        """
        result = self.mongo[SUB_EVENTS_COLLECTION].find({"eventid": self.id}).sort("tfidf", 1).limit(1)
        for r in result:
            if 'tfidf' in r:
                return r['tfidf']

        return 0


class News(object):
    """新闻类
    """
    def __init__(self, id, topicid):
        self.id = id
        self.topicid = topicid
        self.news_collection = EVENTS_NEWS_COLLECTION_PREFIX + str(topicid)
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def update_news_subeventid(self, label):
        """更新单条信息的簇标签, subeventid
        """
        self.mongo[self.news_collection].update({"_id": self.id}, {"$set": {"subeventid": label}})

    def update_news_weight(self, weight):
        """更新单条信息的权重, weight
        """
        self.mongo[self.news_collection].update({"_id": self.id}, {"$set": {"weight": weight}})

    def update_news_duplicate(self, duplicate, same_from):
        """更新条信息的duplicate、same_from字段
        """
        self.mongo[self.news_collection].update({"_id": self.id}, {"$set": {"duplicate": duplicate, "same_from": same_from}})


class Feature(object):
    """特征词类, 按子事件组织
    """
    def __init__(self, subeventid):
        """初始化特征词类
           input
               subeventid: 子事件ID
        """
        self.subeventid = subeventid
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def upsert_newest(self, words):
        """存储子事件最新存量的特征词，pattern为"newest", top100, 为新文本分类服务, upsert模式
        """
        self.mongo[SUB_EVENTS_FEATURE_COLLECTION].update({"subeventid": self.subeventid, "pattern": "newest"}, \
                {"subeventid": self.subeventid, "pattern": "newest", "feature": words}, upsert=True)

    def get_newest(self):
        """获取子事件最新存量的特征词, pattern为"newest", top100, 为新文本分类服务
        """
        result = self.mongo[SUB_EVENTS_FEATURE_COLLECTION].find_one({"subeventid": self.subeventid, "pattern": "newest"})
        if result:
            return result["feature"]
        else:
            return {}

    def set_range(self, words, start_ts, end_ts):
        """计算子事件某时间范围的特征词并存储
        """
        pass

    def get_range(self):
        """获取子事件某时间范围的特征词
        """
        pass

    def clear_all_features(self):
        """清除pattern为regular和newest的特征词
        """
        self.mongo[SUB_EVENTS_FEATURE_COLLECTION].remove({"subeventid": self.subeventid})



if __name__ == "__main__":
    topicid = "54916b0d955230e752f2a94e"
    event = Event(topicid)

    now_ts = int(time.time())
    timestamp = now_ts - now_ts % 3600
    print event.getAvgSubEventSize(timestamp)
    print event.check_ifsplit(timestamp)

