#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2015-01-05 20:00:00
# Version: 0.4.0
"""子事件演化聚类测试
"""

from Database import Event, News, Feature
from classify import subevent_classifier


def test_subevent_classifier():
    labels_list = []
    feature_words_inputs = []
    subevents = event.getSubEvents()
    for subevent in subevents:
        subeventid = subevent["_id"]
        if subeventid != "575612b6-a26f-4df9-a2de-01c85cae56a2":
            labels_list.append(subeventid)
            feature = Feature(subeventid)
            feature_words = feature.get_newest()
            new_feature_words = dict()
            for k, v in feature_words.iteritems():
                new_feature_words[k.encode('utf-8')] = v
            feature_words_inputs.append(new_feature_words)

    news_id = "http://news.xinhuanet.com/comments/2014-11/03/c_1113084515.htm"
    news = News(news_id, event.id)
    ns = news.get_news_info()
    text = ns['title'].encode('utf-8') + ns['content168'].encode('utf-8')
    label = subevent_classifier(text, labels_list, feature_words_inputs)

    print label

if __name__ == '__main__':
    from bson.objectid import ObjectId
    eventid = ObjectId("54916b0d955230e752f2a94e")
    event = Event(eventid)

    test_subevent_classifier()

