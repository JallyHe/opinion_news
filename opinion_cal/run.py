#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-28 12:00:00
# Version: 0.3.0
"""子事件演化聚类主文件
"""

import time
from multiprocessing import Pool
from utils import datetime2ts, ts2datetime
from clustering import kmeans, cluster_evaluation
from classify import subevent_classifier
from feature import extract_feature
from sort import text_weight_cal
from duplicate import duplicate
from Database import News, Event, EventManager, Feature


def one_topic_calculation(eventid_initializing_ts):
    """多步计算
       input:
           eventid_initializing_ts: (eventid, initializing, timestamp)
               eventid: 话题ID
               initializing： 是否做初始聚类
               timestamp: 当前的时间戳，int
    """
    eventid, initializing, timestamp = eventid_initializing_ts

    def step1_cal():
        """第一步计算，获取子事件特征词，新文本与特征词匹配分类
        """
        print '[%s] ' % ts2datetime(int(time.time())), 'event ', eventid, ' %s start step1' % ts2datetime(timestamp)

        # 根据话题ID初始化话题实例
        event = Event(eventid)

        # 获取子事件
        subevents = event.getSubEvents()
        labels_list = []
        feature_words_list = []
        for subevent in subevents:
            subeventid = subevent["_id"]
            feature = Feature(subeventid)

            # 获取每个子事件最新的特征词
            fwords = feature.get_newest()
            feature_words_list.append(fwords)
            labels_list.append(subeventid)

        if initializing:
            # 若话题需要做初始聚类，获取话题开始时间之前的文本
            results = event.getInitialInfos()
        else:
            # 若话题已做完初始聚类，获取话题最新一小时的文本
            results = event.getInfos(timestamp - 3600, timestamp)

        for r in results:
            text = (r['title'] + r['content168']).encode('utf-8')
            # 单条文本与各子事件的特征词进行匹配，得到每条文本的簇标签
            label = subevent_classifier(text, labels_list, feature_words_list)

            if label == "other":
                label = event.getOtherSubEventID()

            news = News(r["_id"], event.id)
            news.update_news_subeventid(label)

        print '[%s] ' % ts2datetime(int(time.time())), 'event ', eventid, ' %s end step1' % ts2datetime(timestamp)

    def step2_cal():
        """第二步计算，判断其他类是否需要分裂，若需要，则对其他类进行文本聚类，并做聚类评价
        """
        # 根据话题ID初始化话题实例
        event = Event(eventid)

        # 判断其他类是否需要分裂
        ifsplit = event.check_ifsplit(timestamp)
        print '[%s] ' % ts2datetime(int(time.time())), 'event ', eventid, ' split ', ifsplit, ' %s start step2' % ts2datetime(timestamp)
        if ifsplit:
            inputs = event.getOtherSubEventInfos()
            items = []
            for r in inputs:
                r["title"] = r["title"].encode("utf-8")
                r["content"] = r["content168"].encode("utf-8")
                items.append(r)

            # kmeans聚类
            kmeans_results = kmeans(items)

            # 聚类评价
            final_cluster_results = cluster_evaluation(kmeans_results)

            # 更新新闻簇标签，更新子事件表
            for label, items in final_cluster_results.iteritems():
                if label == "other":
                    label = event.getOtherSubEventID()

                event.save_subevent(label, timestamp)

                for r in items:
                    news = News(r["_id"], event.id)
                    news.update_news_subeventid(label)


        print '[%s] ' % ts2datetime(int(time.time())), 'event ', eventid, ' %s end step2' % ts2datetime(timestamp)

    def step3_cal():
        """计算各簇的特征词、代表文本、去重
        """
        print '[%s] ' % ts2datetime(int(time.time())), 'event ', eventid, ' %s start step3' % ts2datetime(timestamp)

        # 根据话题ID初始化话题实例
        event = Event(eventid)

        inputs = []
        subevents = event.getSubEvents()
        for subevent in subevents:
            subeventid = subevent["_id"]
            inputs.extend(event.getSubeventInfos(subeventid))

        for r in inputs:
            r["title"] = r["title"].encode("utf-8")
            r["content"] = r["content168"].encode("utf-8")
            r["label"] = r["subeventid"]

        # 计算各簇的存量特征词
        cluster_feature = extract_feature(inputs)
        for label, fwords in cluster_feature.iteritems():
            feature = Feature(label)
            feature.upsert_newest(fwords)

        # 计算文本权重
        for r in inputs:
            weight = text_weight_cal(r, cluster_feature[r['label']])
            news = News(r["_id"], event.id)
            news.update_news_weight(weight)

        # 文本去重
        items_dict = {}
        for r in inputs:
            try:
                items_dict[r["label"]].append(r)
            except KeyError:
                items_dict[r["label"]] = [r]

        for label, items in items_dict.iteritems():
            results = duplicate(items)
            for r in results:
                news = News(r["_id"], event.id)
                news.update_news_duplicate(r["duplicate"], r["same_from"])

        if initializing:
            # 更新事件状态由initializing变为active
            event.activate()

        print '[%s] ' % ts2datetime(int(time.time())), 'event ', eventid, ' %s end step3' % ts2datetime(timestamp)

    event = Event(eventid)

    # 首先检测该事件最近一次修改是否成功
    success = event.checkLastModify(timestamp)
    print success
    if success:
        try:
            # 进行多步计算
            step1_cal()
            step2_cal()
            step3_cal()
            event.setLastmodify(timestamp) # 更新事件的last_modify
            event.setModifysuccess(True) # 更新事件的modify_success为True
        except Exception, e:
            # 如果做计算时出错，更新last_modify, 并将modify_success设置为False
            print e
            event.setLastmodify(timestamp)
            event.setModifysuccess(False)


if __name__ == '__main__':
    em = EventManager()
    event_ids_list = []

    # 检测的时间戳
    timestamp = datetime2ts("2014-12-10 00:00:00")

    # 获取做初始聚类的话题
    initial_event_ids = em.getInitializingEventIDs(timestamp)
    event_ids_list.extend([(id, True, timestamp) for id in initial_event_ids])

    # 获取已做完初始聚类的活跃话题
    active_event_ids = em.checkActive(timestamp)
    event_ids_list.extend([(id, False, timestamp) for id in active_event_ids])

    # map并行计算
    pool = Pool()
    pool.map(one_topic_calculation, event_ids_list)
    pool.close()
    pool.join()

