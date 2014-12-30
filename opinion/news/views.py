#-*- coding:utf-8 -*-


import json
import time
import datetime
from collections import Counter
from utils import ts2datetime
from flask import Blueprint, url_for, render_template, request
from Database import Event, EventManager, Feature
from opinion.global_config import default_topic_name

mod = Blueprint('news', __name__, url_prefix='/news')

em = EventManager()

@mod.route('/')
def index():
    """返回页面
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    n = event.getSubEventsLength() # 子事件的个数

    # 话题简介
    # content = u'在代表委员讨论里，在会内会外交流中，在达成的共识和成果里，改革，成为最强音，汇聚成澎湃激越的主旋律。从新的历史起点出发，全面深化改革的强劲引擎，将推动“中国号”巨轮，向着中国梦的美好目标奋勇前行.'
    content = ""

    return render_template('index/semantic.html',topic=topic_name, n=n, content=content)

@mod.route('/mange/')
def mange():
    """返回页面
    """
    content = u'在代表委员讨论里，在会内会外交流中，在达成的共识和成果里，改革，成为最强音，汇聚成澎湃激越的主旋律。从新的历史起点出发，全面深化改革的强劲引擎，将推动“中国号”巨轮，向着中国梦的美好目标奋勇前行.'
    return render_template('index/opinion.html',content=content )

@mod.route('/topics/')
def topics():
    """返回话题数据
    """
    em = EventManager()
    results = em.getEvents()
    final = []
    for r in results:
        topic = dict()
        try:
            topic['_id'] = str(r['_id'])
            topic['name'] = r['topic']
            topic['start_datetime'] = ts2datetime(r['startts'])
            if 'endts' in r:
                topic['end_datetime'] = ts2datetime(r['endts'])

            topic['status'] = r['status']
            topic['last_modify'] = ts2datetime(r['last_modify'])
            topic['modify_success'] = r['modify_success']
            final.append(topic)
        except KeyError:
            pass

    return json.dumps(final)

@mod.route('/eventriver/')
def eventriver():
    """event river数据
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    subeventlist = event.getEventRiverData()

    return json.dumps({"name": topic_name, "type": "eventRiver", "eventList": subeventlist})

@mod.route('/keywords/')
def opinion_keywords():
    """关键词云数据
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topk_keywords = request.args.get('topk', 50) # topk keywords

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    subevents = event.getSubEvents()

    subevent_keywords = dict()
    for subevent in subevents:
        feature = Feature(subevent["_id"])
        counter = Counter()
        counter.update(feature.get_newest())
        top_keywords_count = counter.most_common(topk_keywords)
        top5_keywords_count = counter.most_common(3)

        subevent_top5_keywords = ','.join([k for k, c in top5_keywords_count])
        subevent_top5_count = sum([c for k, c in top5_keywords_count])
        subevent_keywords[subevent["_id"]] = [(subevent_top5_keywords, subevent_top5_count), dict(top_keywords_count)]

    return json.dumps(subevent_keywords)

@mod.route('/ratio/')
def opinion_ratio():
    """子事件占比饼图数据
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topk_keywords = request.args.get('topk', 3)

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    subevents = event.getSubEvents()

    subevent_keywords = dict()
    for subevent in subevents:
        feature = Feature(subevent["_id"])
        counter = Counter()
        counter.update(feature.get_newest())
        top5_keywords_count = counter.most_common(topk_keywords)
        subevent_top5_keywords = ','.join([k for k, c in top5_keywords_count])
        subevent_keywords[subevent["_id"]] = subevent_top5_keywords

    results = dict()
    size_results = event.getSubEventSize(int(time.time()))
    total_size = sum(size_results.values())
    for label, size in size_results.iteritems():
        keywords = subevent_keywords[label]
        results[keywords] = float(size) / float(total_size)

    return json.dumps(results)

@mod.route('/weibos/')
def opinion_weibos():
    """重要信息排序
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    subevents = event.getSubEvents()

    results = dict()
    for subevent in subevents:
        subeventid = subevent["_id"]
        results[subeventid] = event.getSortedInfos(subeventid=subeventid)

    return json.dumps(results)

"""
@mod.route('/rank/')
def opinion_rank():#自定义排序
    topic = request.args.get('topic', '')
    c_topic = request.args.get('c_topic', '')
    r_type = request.args.get('r_type', '')

    r_type = r_type.strip('\r\t')
    if r_type == u'时间':
        r_type = 'time'
    else:
        r_type = 'weight'
        
    if not r_type:#异常返回
        return 'ranking type is wrong'

    f_news = TopkHeap(10)
    item = c_topic.split(',')
    for i in range(0,len(item)):
        sub = item[i].strip('\r\t')
        results = get_opinion_weibos_rank(topic,sub)
 
        if not results:
            continue

        if r_type == 'weight':#按代表性排序
            for i in range(0,len(results)):
                k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
                row = {'c_topic':k,'weight':results[i][1],'_id':results[i][2],'title':results[i][3],'content':results[i][4],'user':results[i][5],'time':results[i][6],'source':results[i][7],'c_source':results[i][8],'repeat':results[i][9]}
                f_news.Push((results[i][1],row))
        else:#按时间排序
            for i in range(0,len(results)):
                k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
                row = {'c_topic':k,'weight':results[i][1],'_id':results[i][2],'title':results[i][3],'content':results[i][4],'user':results[i][5],'time':results[i][6],'source':results[i][7],'c_source':results[i][8],'repeat':results[i][9]}
                f_news.Push((results[i][5],row))

    data = f_news.TopK()
    return json.dumps(data)
    
@mod.route('/load_more/')
def opinion_load_more():

    topic = request.args.get('topic', '')

    return render_template('index/load_more.html',topic=topic)    
"""
    
