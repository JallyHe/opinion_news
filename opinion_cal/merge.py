#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2015-01-08 13:00:00
# Version: 0.1.0
"""子事件merge
"""

import time
from multiprocessing import Pool
from Database import Event, EventManager, Feature

def merge_subevents(subevent_feature_words, sorted_subeventids, top_tfidf_para=10, top_percent=0.3):
    """返回
       merge_subeventids: [['保留ID', '合并ID']]
    """
    inputs_features = dict()
    for label, fwords in subevent_feature_words.iteritems():
        sorted_results = sorted(fwords.iteritems(), key=lambda (k, v): v, reverse=False)
        top_words_set = set([k for k, v in sorted_results[-top_tfidf_para:]])
        inputs_features[label] = top_words_set

    candidate_subeventids = []
    merge_subeventids = []
    for idx, testsid in enumerate(sorted_subeventids):
        max_intersection = 0
        max_idx = idx
        if len(candidate_subeventids):
            for idy, subid in enumerate(candidate_subeventids):
                if testsid != subid:
                    intersection = len(inputs_features[subid] & inputs_features[testsid])
                    if intersection > max_intersection:
                        max_intersection = intersection
                        max_idx = idy

        if max_idx != idx and max_intersection >= top_tfidf_para * top_percent:
            # print idx, max_idx, max_intersection
            merge_subeventids.append([candidate_subeventids[max_idx], testsid])
        else:
            candidate_subeventids.append(testsid)

    return candidate_subeventids, merge_subeventids


def one_topic_merge(eventid_initializing):
    """合并簇
       input:
           eventid_initializing: (eventid, initializing)
               eventid: 话题ID
               initializing： 是否做初始聚类
    """
    eventid, initializing = eventid_initializing

    # 根据话题ID初始化话题实例
    event = Event(eventid)

    timestamp = event.getLastmodify() + 3600 # 当前的时间戳，int, 默认为最后修改日期+3600
    now_hour = int(time.strftime('%H', time.localtime(timestamp)))

    subevents = event.getSubEvents()
    subevent_fwords = dict()
    for subevent in subevents:
        subeventid = subevent["_id"]
        feature = Feature(subeventid)

        # 获取每个子事件最新的特征词
        fwords = feature.get_newest()
        subevent_fwords[subeventid] = fwords

    subeventids_sort_timestamp = event.get_sorted_subeventids()

    cids, mids = merge_subevents(subevent_fwords, subeventids_sort_timestamp, top_tfidf_para=10, top_percent=0.3)

    for res_id, mer_id in mids:
        # 将mer_id下的文本扔入res_id下的簇，remove mer_id的簇，同时重新计算各簇的特征词, 并计算文本权重, 并去重
        temp_infos = event.get_subevent_infos(mer_id)

        for r in temp_infos:
            news = News(r["_id"], event.id)
            news.update_news_subeventid(res_id)

        event.remove_subevents([mer_id])


if __name__ == '__main__':
    em = EventManager()
    event_ids_list = []

    # 获取做初始聚类的话题
    initial_event_ids = em.getInitializingEventIDs()
    event_ids_list.extend([(id, True) for id in initial_event_ids])

    # 获取已做完初始聚类的活跃话题
    active_event_ids = em.checkActive()
    event_ids_list.extend([(id, False) for id in active_event_ids])

    # map并行计算
    pool = Pool()
    pool.map(one_topic_merge, event_ids_list)
    pool.close()
    pool.join()
