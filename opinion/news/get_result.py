# -*- coding: utf-8 -*-

import json
import opinion.model
from opinion.model import OpinionTestTime, OpinionTestRatio, OpinionTestKeywords, OpinionTestWeibos
from opinion.extensions import db

def get_opinion_time(topic):
    items = db.session.query(OpinionTestTime).filter(OpinionTestTime.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        topic_term = json.loads(item.child_topic)
        start_ts = item.start_ts
        end_ts = item.end_ts
        results.append([topic_term,start_ts,end_ts])
    
    return results

def get_opinion_ratio(topic):
    items = db.session.query(OpinionTestRatio).filter((OpinionTestRatio.id>=103)&(OpinionTestRatio.id<=128)).all()#ratio表有问题，话题存不进去
    if not items:
        return None
##    items = db.session.query(OpinionTestRatio).filter(OpinionTestRatio.topic==topic).all()
##    if not items:
##        return None

    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        ratio = item.ratio
        results.append([child_topic,ratio])
    print len(results)
    return results

def get_opinion_keywords(topic):
    items = db.session.query(OpinionTestKeywords).filter(OpinionTestKeywords.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        keywords_weight = json.loads(item.keywords)
        results.append([child_topic,keywords_weight])
    
    return results

def get_opinion_weibos(topic):
    items = db.session.query(OpinionTestWeibos).filter(OpinionTestWeibos.topic==topic).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        weight = item.weight
        mid = item.mid
        title = item.title
        content = item.content
        user = item.user
        time = item.time
        source = item.source
        c_source = item.c_source
        repeat = item.repeat
        results.append([child_topic,weight,mid,title,content,user,time,source,c_source,repeat])
    return results

def get_opinion_weibos_rank(topic,c_topic):

    title = c_topic.split('-')
    row = []
    for i in range(0,len(title)):
        row.append(title[i])

    row = json.dumps(row)
    items = db.session.query(OpinionTestWeibos).filter((OpinionTestWeibos.topic==topic)&(OpinionTestWeibos.child_topic==row)).all()
    if not items:
        return None
    results = []
    for item in items:
        child_topic = json.loads(item.child_topic)
        weight = item.weight
        mid = item.mid
        title = item.title
        content = item.content
        user = item.user
        time = item.time
        source = item.source
        c_source = item.c_source
        repeat = item.repeat
        results.append([child_topic,weight,mid,title,content,user,time,source,c_source,repeat])
    return results

        
