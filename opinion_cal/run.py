#-*-coding=utf-8-*-


import time
from utils import _default_mongo
from config import MONGO_DB_NAME, EVENTS_NEWS_COLLECTION_PREFIX, \
        START_TS, END_TS
from Info import News
from Event import Event
from Features import Feature
from classify import subevent_classifier
from duplicate import max_same_rate, max_same_rate_shingle


if __name__ == '__main__':
    topic = "APEC2014"
    topicid = "54916b0d955230e752f2a94e"
    mongo = _default_mongo(usedb=MONGO_DB_NAME)

    event = Event(topicid)

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

    # 获取话题最新的文本
    results = event.getInfos(START_TS, END_TS)
    items = []
    for r in results:
        text = r['title'].encode('utf-8') + r['content168'].encode('utf-8')
        """
        idx, rate, reserve = max_same_rate_shingle(items, r)
        if reserve:
            items.append(r)
        else:
            print idx, rate, reserve, items[idx]['title'], r['title'], items[idx]['content168'], r['content168']
        """

        news = News(r["_id"], event.id)
        # 单条文本与各子事件的特征词进行匹配，得到每条文本的簇标签
        label = subevent_classifier(text, labels_list, feature_words_list)
        print label

        if label == "other":
            label = event.getOtherSubEventID()

        # news.update_news_subeventid(label)

