#-*- coding:utf-8 -*-


import json
import time
import datetime
from collections import Counter
from utils import ts2datetime, ts2date
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

    start_ts = event.getStartts()
    default_startts = start_ts - 3600 * 24 * 30
    last_modify = event.getLastmodify()
    status = event.getStatus()
    end_ts = event.getEndts()
    if end_ts:
        end_date = ts2date(end_ts)
    else:
        end_date = u'无'
    modify_success = event.getModifysuccess()

    time_range = request.args.get('time_range', ts2date(default_startts) + '-' + ts2date(last_modify))

    return render_template('index/semantic.html', topic=topic_name, time_range=time_range, status=status, \
            start_date=ts2datetime(start_ts), end_date=end_date, last_modify=ts2datetime(last_modify), modify_success=modify_success)

@mod.route('/manage/')
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
    end_ts = request.args.get('ts', None)
    during = request.args.get('during', None)

    if end_ts:
        end_ts = int(end_ts)

    if during:
        during = int(during)
        start_ts = end_ts - during

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)
    subeventlist = event.getEventRiverData(start_ts, end_ts)

    return json.dumps({"name": topic_name, "type": "eventRiver", "eventList": subeventlist})

@mod.route('/keywords/')
def opinion_keywords():
    """关键词云数据
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    end_ts = request.args.get('ts', None)
    during = request.args.get('during', None)

    subevent_status = request.args.get('subevent', 'global')
    topk_keywords = request.args.get('topk', 50) # topk keywords

    if subevent_status != 'global':
        subeventid = subevent_status
        feature = Feature(subeventid)
        counter = Counter()
        counter.update(feature.get_newest())
        top_keywords_count = counter.most_common(topk_keywords)

        subevent_keywords = dict(top_keywords_count)

        return json.dumps(subevent_keywords)
    else:
        topicid = em.getEventIDByName(topic_name)
        event = Event(topicid)
        if end_ts:
            end_ts = int(end_ts)

        if during:
            during = int(during)

        counter = Counter()
        subevents = event.getSubEvents()
        for subevent in subevents:
            feature = Feature(subevent["_id"])
            counter.update(feature.get_newest())

        top_keywords_count = counter.most_common(topk_keywords)

        return json.dumps(dict(top_keywords_count))


@mod.route('/ratio/')
def opinion_ratio():
    """饼图数据
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topk = request.args.get('topk', 10)
    end_ts = request.args.get('ts', None)
    during = request.args.get('during', None)
    subevent_status = request.args.get('subevent', 'global')

    if end_ts:
        end_ts = int(end_ts)

    if during:
        during = int(during)
        start_ts = end_ts - during

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)

    if subevent_status != 'global':
        subeventid = subevent_status
        results = event.getMediaCount(start_ts, end_ts, subeventid)
    else:
        results = event.getMediaCount(start_ts, end_ts)

    from collections import Counter
    results = Counter(results)
    results = dict(results.most_common(topk))

    total_weight = sum(results.values())
    results = {k: float(v) / float(total_weight) for k, v in results.iteritems()}

    return json.dumps(results)


@mod.route('/weibos/')
def opinion_weibos():
    """重要信息排序
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    end_ts = request.args.get('ts', None)
    during = request.args.get('during', None)
    topk = int(request.args.get('topk', 10))
    subevent_status = request.args.get('subevent', 'global')

    if end_ts:
        end_ts = int(end_ts)

    if during:
        during = int(during)
        start_ts = end_ts - during

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)

    results = dict()
    if subevent_status != 'global':
        subeventid = subevent_status
        results = event.getSortedInfos(start_ts, end_ts, subeventid=subeventid, limit=10)

        return json.dumps(results)
    else:
        results = event.getSortedInfos(start_ts, end_ts, subeventid=None, limit=10)

        return json.dumps(results)


@mod.route('/timeline/')
def timeline():
    topic_name = request.args.get('query', default_topic_name) # 话题名
    timestamp = int(request.args.get('ts'))
    subevent_status = request.args.get('subevent', 'global')
    during = int(request.args.get('during', 3600 * 24))

    topicid = em.getEventIDByName(topic_name)
    event = Event(topicid)

    results = dict()
    if subevent_status == 'global':
        count = event.getInfoCount(timestamp - during, timestamp)
        results["global"] = [timestamp, count]
    else:
        subeventid = subevent_status
        count = event.getInfoCount(timestamp - during, timestamp, subevent=subeventid)
        results[subeventid] = [timestamp, count]

    return json.dumps(results)

@mod.route('/peak/')
def getPeaks():
    '''获取拐点数据
    '''
    from peak_detection import detect_peaks
    limit = int(request.args.get('limit', 10))
    query = request.args.get('query', None)
    during = int(request.args.get('during', 24 * 3600))

    subevent_status = request.args.get('subevent', 'global')
    lis = request.args.get('lis', '')

    try:
        lis = [float(da) for da in lis.split(',')]
    except:
        lis = []

    ts_lis = request.args.get('ts', '')
    ts_lis = [float(da) for da in ts_lis.split(',')]

    new_zeros = detect_peaks(lis)

    time_lis = {}
    for idx, point_idx in enumerate(new_zeros):
        ts = ts_lis[point_idx]
        end_ts = ts

        time_lis[idx] = {
            'ts': end_ts * 1000,
            'title': str(idx)
        }

    return json.dumps(time_lis)

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
    
