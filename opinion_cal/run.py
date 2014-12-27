#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-26 23:00:00
# Version: 0.2.0

import time
from utils import datetime2ts
from Info import News
from Event import Event, EventManager
from Features import Feature
from clustering import kmeans, cluster_evaluation
from classify import subevent_classifier
from feature import extract_feature
from sort import text_weight_cal
from duplicate import duplicate


def steps_calculation(eventids, initializing=True):
    """多步计算
       input:
           eventids: 话题ID列表
           initializing： 是否做初始聚类
    """
    def step1_cal(eventid):
        """第一步计算，获取子事件特征词，新文本与特征词匹配分类
        """
        print 'event ', eventid, ' start step1'

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

        print 'event ', eventid, ' end step1'

    def step2_cal(eventid):
        """第二步计算，判断其他类是否需要分裂，若需要，则对其他类进行文本聚类，并做聚类评价
        """
        # 根据话题ID初始化话题实例
        event = Event(eventid)

        # 判断其他类是否需要分裂
        ifsplit = event.check_ifsplit(timestamp)
        print 'event ', eventid, ' split ', ifsplit, ' start step2'
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

            if initializing:
                # 更新事件状态由initializing变为active
                event.activate()

        print 'event ', eventid, ' end step2'

    def step3_cal(eventid):
        """计算各簇的特征词、代表文本、去重
        """
        print 'event ', eventid, ' start step3'

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
            print label
            for k, v in fwords.iteritems():
                print k, v

        # 计算文本权重
        for r in inputs:
            weight = text_weight_cal(r, cluster_feature[r['label']])

        # 文本去重
        items_dict = {}
        for r in inputs:
            try:
                items_dict[r["label"]].append(r)
            except KeyError:
                items_dict[r["label"]] = [r]

        results = duplicate(inputs)

        print 'event ', eventid, ' end step3'

    # 遍历每个话题，进行多步计算
    for eventid in eventids:
        step1_cal(eventid)
        step2_cal(eventid)
        step3_cal(eventid)


if __name__ == '__main__':
    # 时间戳
    timestamp = datetime2ts("2014-12-10 00:00:00")

    em = EventManager()

    """
    from bson import ObjectId
    steps_calculation([ObjectId('549d1de52253274b61368312')])
    """
    # 获取初始化的话题，做初始聚类
    initial_event_ids = em.getInitializingEventIDs(timestamp)
    steps_calculation(initial_event_ids, initializing=True)

    # 检测话题活跃性, 获取活跃的话题
    active_event_ids = em.checkActive(timestamp)
    steps_calculation(initial_event_ids, initializing=False)

