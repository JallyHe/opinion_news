#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

"""维护文件
"""

from utils import datetime2ts
from multiprocessing import Pool
from Database import Event, EventManager, Feature

def initialize_topics():
    """重新初始化topic
       1. 把话题status变为initializing
       2. 设置话题起始时间
       3. 清除新闻表中每条新闻的subeventid字段、weight字段、duplicate字段、same_from字段
       4. 清除子事件表中话题的相关数据
       5. 清除子事件特征词表中话题的相关数据
    """
    topic_start = []

    """
    topicname = u'APEC2014'
    start_datetime = "2014-11-04 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'手术台自拍'
    start_datetime = "2014-12-23 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'呼格案'
    start_datetime = "2014-12-14 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'复旦投毒案'
    start_datetime = "2014-02-18 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'非法占中'
    start_datetime = "2014-09-30 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'马航失联'
    start_datetime = "2014-03-10 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'博鳌论坛'
    start_datetime = "2014-04-03 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'昆明火车站暴恐案'
    start_datetime = "2014-03-03 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'乌鲁木齐火车站暴恐'
    start_datetime = "2014-05-01 00:00:00"
    topic_start.append((topicname, start_datetime))

    topicname = u'全军政治工作会议'
    start_datetime = "2014-11-04 00:00:00"
    topic_start.append((topicname, start_datetime))
    """

    topicname = u'高校思想宣传工作'
    start_datetime = "2015-01-31 00:00:00"

    """
    topicname = u'张灵甫遗骨被埋羊圈'
    start_datetime = "2015-01-31 00:00:00"
    """

    topic_start.append((topicname, start_datetime))

    pool = Pool()
    pool.map(one_topic_clear, topic_start)
    pool.close()
    pool.join()

def one_topic_clear(topicname_start):
    topicname, start_datetime = topicname_start
    em = EventManager()
    topicid = em.getEventIDByName(topicname)
    start_ts = datetime2ts(start_datetime)

    event = Event(topicid)
    event.initialize(start_ts)

if __name__ == '__main__':
    initialize_topics()

