#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2015-01-25 19:00:00
# Version: 0.1.0
"""加载客观微博数据，当作新闻进行处理
"""

import re
import json
from Database import EventManager, Event
from utils import ts2datetime, ts2date, datetime2ts


WEIBO_FIELDS = [u'reposts_count', u'_id', u'name', u'website_type', \
        u'text', u'createdate', u'bmiddle_pic', u'retweeted_mid', \
        u'weibourl', u'source', u'attitudes_count', u'secondprovinceid', \
        u'comments_count', u'user', u'timestamp', u'provinceid', \
        u'retweeted_uid', u'geo', u'topics', u'message_type']

NEWS_FIELDS = ['_id', 'classid', 'more_same_link', 'datetime', \
        'last_modify', 'replies', 'source_website', 'id', 'category', \
        'news_author', 'user_id', 'title', 'relative_news', 'source_from_name', \
        'showurl', 'user_name', 'user_image_url', 'same_news_num', 'user_url', \
        'first_in', 'timestamp', 'isV', 'title1', 'tplid', 'key', 'transmit_name', \
        'date', 'pagesize', 'url', 'content168', 'summary', 'thumbnail_url']

NULL_FIELDS = ['classid', 'more_same_link', 'last_modify', 'source_website', 'category', \
        'relative_news', 'source_from_name', 'user_image_url', 'user_url', 'first_in', \
        'isV', 'title1', 'tplid', 'key', 'transmit_name', 'pagesize', 'summray', 'thumbnail_url']


def subob_classifier(item):
    subject = True # 是否主观
    if '【' in item['text'] and '】' in item['text']:
        subject = False

    item['subject'] = subject
    return item

def subject_weibo2news(item):
    news = dict()
    for field in NULL_FIELDS:
        news[field] = None

    for k, v in item.iteritems():
        if k == 'timestamp':
            news['timestamp'] = v
            news['date'] = ts2date(v)
            news['datetime'] = ts2datetime(v)
        if k == '_id':
            news['_id'] = v
            news['id'] = v
        if k == 'reposts_count':
            news['replies'] = v
        if k == 'comments_count':
            news['same_news_num'] = v
        if k == 'name':
            news['news_author'] = v
            news['user_name'] = v
        if k == 'user':
            news['user_id'] = v
        if k == 'text':
            text = v
            news['title'] = '【' + re.search(r'【(.*?)】', str(text)).group(1) + '】'
            news['content168'] = text.replace(news['title'], '')
        if k == 'weibourl':
            news['showurl'] = v

    return news


def load_subject_weibo_data():
    """加载客观微博数据
    """
    topicname = u'外滩踩踏-微博'

    em = EventManager()
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)

    f = open('caitai.jl')
    for line in f:
        item = json.loads(line.strip())
        item['text'] = item['text'].encode('utf-8')
        item = subob_classifier(item)
        if not item['subject']:
            news = subject_weibo2news(item)
            event.saveItem(news)

    f.close()


def initializeWeiboTopic():
    """初始化weibo话题
    """
    em = EventManager()

    topicname = u'外滩踩踏-微博'
    start_datetime = "2015-01-02 00:00:00"
    topicid = em.getEventIDByName(topicname)
    start_ts = datetime2ts(start_datetime)

    event = Event(topicid)
    event.initialize(start_ts)


if __name__ == '__main__':
    # initializeWeiboTopic()
    load_subject_weibo_data()

