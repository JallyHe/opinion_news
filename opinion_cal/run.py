#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-26 23:00:00
# Version: 0.2.0

from utils import datetime2ts
from Info import News
from Event import Event, EventManager
from Features import Feature
from classify import subevent_classifier
from duplicate import max_same_rate, max_same_rate_shingle


def two_step_calculation(eventids, initializing=True):
    """两步计算
       input:
           eventids: 话题ID列表
           initializing： 是否做初始聚类
    """
    # 遍历每个话题，进行两步计算
    for eventid in eventids:
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

            news = News(r["_id"], event.id)
            # 单条文本与各子事件的特征词进行匹配，得到每条文本的簇标签
            label = subevent_classifier(text, labels_list, feature_words_list)
            print label

            if label == "other":
                label = event.getOtherSubEventID()

            # news.update_news_subeventid(label)


if __name__ == '__main__':
    # 时间戳
    timestamp = datetime2ts("2014-12-10 00:00:00")

    em = EventManager()

    # 获取初始化的话题，做初始聚类
    initial_event_ids = em.getInitializingEventIDs(timestamp)
    two_step_calculation(initial_event_ids, initializing=True)

    # 检测话题活跃性, 获取活跃的话题
    active_event_ids = em.checkActive(timestamp)
    two_step_calculation(initial_event_ids, initializing=False)

