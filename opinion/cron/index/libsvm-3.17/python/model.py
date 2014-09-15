# -*- coding: utf-8 -*-

from config import db

__all__ = ['OpinionTestRatio','OpinionTestTime',\
           'OpinionTestKeywords', 'OpinionTestWeibos', 'IndexTopic']

class IndexTopic(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    topic = db.Column(db.Text)
    count = db.Column(db.Integer) # 微博数
    user_count = db.Column(db.Integer) # 用户数
    begin = db.Column(db.BigInteger(10,unsigned = True)) # 起始时间
    end = db.Column(db.BigInteger(10,unsigned = True)) # 终止时间
    area = db.Column(db.Text) # 地理区域
    key_words = db.Column(db.Text) # 关键词
    opinion = db.Column(db.Text) # 代表文本
    media_opinion = db.Column(db.Text) # 媒体观点

    def __init__(self, topic, count, user_count, begin, end, area, key_words, opinion, media_opinion):
        self.topic = topic
        self.count = count
        self.user_count = user_count
        self.begin = begin
        self.end = end
        self.area = area
        self.key_words = key_words
        self.opinion = opinion
        self.media_opinion = media_opinion
        
# opinion module used in test
class OpinionTestTime(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.Text)
    start_ts = db.Column(db.BigInteger(20, unsigned=True))
    end_ts = db.Column(db.BigInteger(20, unsigned=True))

    def __init__(self, topic, child_topic, start_ts, end_ts):
        self.topic = topic
        self.child_topic = child_topic
        self.start_ts = start_ts
        self.end_ts = end_ts

class OpinionTestRatio(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.Text)
    ratio = db.Column(db.Float)

    def __init__(self, topic, child_topic, ratio):
        self.topc = topic
        self.child_topic = child_topic
        self.ratio = ratio

class OpinionTestKeywords(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.Text)
    keywords = db.Column(db.Text)

    def __init__(self, topic, child_topic, keywords):
        self.topic = topic
        self.child_topic = child_topic
        self.keywords = keywords

class OpinionTestWeibos(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic = db.Column(db.String(20))
    child_topic = db.Column(db.Text)
    weight = db.Column(db.Float)
    mid = db.Column(db.String(20))
    title = db.Column(db.Text)
    content = db.Column(db.Text)
    user = db.Column(db.String(20))
    time = db.Column(db.String(20))    
    source = db.Column(db.String(20))
    c_source = db.Column(db.String(20))
    repeat = db.Column(db.Integer)

    def __init__(self, topic, child_topic, weight, mid, title, content, user, time, source, c_source, repeat):
        self.topic = topic
        self.child_topic = child_topic
        self.weight = weight
        self.mid = mid
        self.title = title
        self.content = content
        self.user = user
        self.time = time        
        self.source = source
        self.c_source = c_source
        self.repeat = repeat





