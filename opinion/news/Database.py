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
        """根据话题新文本数检查话题的活跃性, 更新不再活跃的话题的status
           input:
               timestamp: 检测的时间点
           output:
               活跃的话题ID
        """
        active_ids = []
        ids = self.getActiveEventIDs(timestamp)
        for id in ids:
            event = Event(id)
            if event.check_ifactive(timestamp):
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
        return [r for r in results]

    def getSubEventsLength(self):
        """获取子事件的个数
        """
        return self.mongo[self.sub_events_collection].find({"eventid": self.id, "_id": {"$ne": self.other_subeventid}}).count()

    def getEventRiverData(self, topk_keywords=5):
        """获取echarts event river的数据
           input:
               topk_keywords: 取每个子事件的topk keywords
        """
        results = self.mongo[self.news_collection].find({"$and": \
                [{"subeventid": {"$ne": self.other_subeventid}}, \
                {"subeventid": {"$exists": True}}]})
        cluster_date = dict()
        for r in results:
            label = r['subeventid']
            date = time.strftime('%Y-%m-%d', time.localtime(r['timestamp']))
            try:
                cluster_date[label].append(date)
            except KeyError:
                cluster_date[label] = [date]

        from collections import Counter
        results = []
        for label, dates in cluster_date.iteritems():
            feature = Feature(label)
            fwords = feature.get_newest()
            counter = Counter(fwords)
            top_words_count = counter.most_common(topk_keywords)
            cluster_keywords = ','.join([word for word, count in top_words_count])

            counter = Counter(dates)
            date_count_dict = dict(counter.most_common())
            sorted_date_count = sorted(date_count_dict.iteritems(), key=lambda(k, v): k, reverse=False)
            evolution_list = [{"time": date, "value": count, "detail": {"text": str(count), "link": "#"}} for date, count in sorted_date_count]
            cluster_result = {"name": cluster_keywords, "weight": len(dates), "evolution": evolution_list}
            results.append(cluster_result)

        return results

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
        self.setLastmodify(start_ts - 1)
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

    def getSubEventSize(self, timestamp):
        """获取子事件的大小
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
        count_dict = {r["subeventid"]: r['count'] for r in results}

        return count_dict

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

    def getSortedInfos(self, subeventid=None, key="weight", removeDuplicate=True, limit=10):
        """获取各簇排序后的信息
           input:
               subeventid: 子事件的ID，默认不指定，则计算所有子事件
               key: 排序的标准, 默认是按照文本相关度，weight
               removeDuplicate: True or False，是否移除重复的文本
               limit: 默认返回前10
           output:
               排完序的items
        """
        # items: 一个簇下的items，每个item需要包含same_from一个字段
        def handle_subevent(subeventid):
            results = self.mongo[self.news_collection].find({"subeventid": subeventid}).sort(key, -1).limit(limit)
            unique_ids = set()
            unique_items = {}
            for r in results:
                if r['same_from'] in unique_ids:
                    try:
                        unique_items[r['same_from']]['same_list'].append(r)
                    except KeyError:
                        unique_items[r['same_from']]['same_list'] = [r]

                else:
                    unique_items[r['same_from']] = r
                    unique_ids.add(r['same_from'])

            sorted_results = sorted(unique_items.iteritems(), key=lambda(k, v): v[key], reverse=True)
            sorted_results = [[news['weight'], news]  for id, news in sorted_results]
            return sorted_results

        if subeventid:
            return handle_subevent(subeventid)
        else:
            s_dict = dict()
            subevents = self.getSubEvents()
            for subevent in subevents:
                subeventid = subevent["_id"]
                s_dict[subeventid] = handle_subevent(subeventid)

            return s_dict

    def getInitialInfos(self):
        """获取初始聚类文本，默认取话题开始时间之前的文本
        """
        event = self.mongo[self.events_collection].find_one({"_id": self.id})
        start_ts = event["startts"]
        results = self.mongo[self.news_collection].find({"timestamp": {"$lt": start_ts}})
        return [r for r in results]

    def getOtherSubEventInfos(self):
        results = self.mongo[self.news_collection].find({"subeventid": self.other_subeventid})
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
        SIX_HOUR_SECONDS = 3600
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

    def checkLastModify(self, timestamp):
        """检测最后一次修改时间是否在检测的时间点之前，最后一次修改是否成功
           input:
               timestamp: 检测的时间戳，整点
           output:
               True or False
        """
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

