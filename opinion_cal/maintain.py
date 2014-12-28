#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

"""维护文件
"""

from Features import Feature
from utils import datetime2ts
from Event import Event, EventManager

def initialize_topics():
    """重新初始化topic
       1. 把话题status变为initializing
       2. 设置话题起始时间
       3. 清除新闻表中每条新闻的subeventid字段
       4. 清除子事件表中话题的相关数据
       5. 清除子事件特征词表中话题的相关数据
    """
    topic_start = []
    em = EventManager()

    topicname = u'APEC2014'
    start_datetime = "2014-11-04 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'手术台自拍'
    start_datetime = "2014-12-14 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'呼格案'
    start_datetime = "2014-12-01 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'复旦投毒案'
    start_datetime = "2014-12-01 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'非法占中'
    start_datetime = "2014-12-01 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'马航失联'
    start_datetime = "2014-03-10 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'博鳌论坛'
    start_datetime = "2014-04-10 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'昆明火车站暴恐案'
    start_datetime = "2014-03-03 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'全军政治工作会议'
    start_datetime = "2014-11-04 00:00:00"
    topic_start.append((topicname, start_datetime))

    for topicname, start_datetime in topic_start:
        topicid = em.getEventIDByName(topicname)
        event = Event(topicid)
        event.initializing()
        start_ts = datetime2ts(start_datetime)
        event.setStartts(start_ts)
        event.clear_news_label()
        subevents = event.getSubEvents()
        event.clear_subevents()
        for subevent in subevents:
            feature = Feature(subevent["_id"])
            feature.clear_all_features()


if __name__ == '__main__':
    initialize_topics()

