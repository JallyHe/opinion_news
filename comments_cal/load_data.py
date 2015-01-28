#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2015-01-25 19:00:00
# Version: 0.1.0
"""加载主观微博数据，当作评论进行处理
"""

import os
import re
import sys
import json

AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../public/')
sys.path.append(AB_PATH)

from Database import EventManager, EventComments
from utils import ts2datetime, ts2date, datetime2ts


WEIBO_FIELDS = [u'reposts_count', u'_id', u'name', u'website_type', \
        u'text', u'createdate', u'bmiddle_pic', u'retweeted_mid', \
        u'weibourl', u'source', u'attitudes_count', u'secondprovinceid', \
        u'comments_count', u'user', u'timestamp', u'provinceid', \
        u'retweeted_uid', u'geo', u'topics', u'message_type']

COMMENTS_FIELDS = ['first_in', 'timestamp', 'datetime', 'last_modify', \
        'date', 'id', 'user_comment_url', 'content168', 'news_id', 'attitudes_count', \
        'comments_count', 'reposts_count','location', '_id', 'user_name', 'comment_source']

NULL_FIELDS = ['last_modify', 'first_in', 'news_id', 'location', 'user_comment_url']


def subob_classifier(item):
    subject = True # 是否主观
    if '【' in item['text'] and '】' in item['text']:
        subject = False

    item['subject'] = subject
    return item

def object_weibo2comment(item):
    comment = dict()
    for field in NULL_FIELDS:
        comment[field] = None
    comment['news_id'] = 'weibo'
    for k, v in item.iteritems():
        if k == 'timestamp':
            comment['timestamp'] = v
            comment['date'] = ts2date(v)
            comment['datetime'] = ts2datetime(v)
        if k == '_id':
            comment['_id'] = v
            comment['id'] = v
        if k == 'reposts_count':
            comment[k] = v
        if k == 'comments_count':
            comment[k] = v
        if k == 'attitudes_count':
            comment[k] = v
        if k == 'name':
            comment['user_name'] = v
        if k =='weibourl':
            comment['comment_source'] = v
        if k == 'text':
            text = v
            comment['content168'] = text

    return comment


def load_object_weibo_data():
    """加载主观微博数据
    """
    # topicname = u'外滩踩踏-微博'
    # topicname = u'呼格案-微博'
    # topicname = u'复旦投毒案-微博'
    topicname = u'APEC-微博'

    em = EventManager()
    topicid = em.getEventIDByName(topicname)
    eventcomment = EventComments(topicid)

    # f = open('caitai.jl')
    # f = open('huge.jl')
    # f = open('fudan.jl')
    f = open('apec.jl')
    for line in f:
        item = json.loads(line.strip())
        item['text'] = item['text'].encode('utf-8')
        item = subob_classifier(item)
        if item['subject']:
            weibo = object_weibo2comment(item)
            eventcomment.saveItem(weibo)

    f.close()


def initializeWeiboTopic():
    """初始化weibo话题
    """
    em = EventManager()

    # topicname = u'外滩踩踏-微博'
    # start_datetime = "2015-01-02 00:00:00"
    # topicname = u'呼格案-微博'
    # start_datetime = "2014-12-14 00:00:00"
    # topicname = u'复旦投毒案-微博'
    # start_datetime = "2014-12-15 00:00:00"
    topicname = u'APEC-微博'
    start_datetime = "2014-12-15 00:00:00"

    topicid = em.getEventIDByName(topicname)
    start_ts = datetime2ts(start_datetime)

    eventcomment = EventComments(topicid)
    eventcomment.initialize(start_ts)


def initializeNewsTopic():
    """初始化新闻话题
    """
    em = EventManager()

    topicname = u'外滩踩踏'
    start_datetime = "2015-01-02 00:00:00"
    topicid = em.getEventIDByName(topicname)
    start_ts = datetime2ts(start_datetime)

    event = Event(topicid)
    event.initialize(start_ts)


if __name__ == '__main__':
    # initializeNewsTopic()
    # initializeWeiboTopic()
    load_object_weibo_data()

