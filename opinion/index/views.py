#-*- coding:utf-8 -*-


import json
import time
import datetime
from opinion.model import *
from opinion.extensions import db
import search as searchModule
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response
from get_result import get_opinion_time, get_opinion_ratio, get_opinion_keywords, get_opinion_weibos
import heapq

mod = Blueprint('opinion_news', __name__, url_prefix='/index')

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]


@mod.route('/')
def meaning():
    
    topic = u'两会'
    results = get_opinion_ratio(topic)
    n = len(results)

    content = u'在代表委员讨论里，在会内会外交流中，在达成的共识和成果里，改革，成为最强音，汇聚成澎湃激越的主旋律。从新的历史起点出发，全面深化改革的强劲引擎，将推动“中国号”巨轮，向着中国梦的美好目标奋勇前行.'

    return render_template('index/semantic.html',topic = topic,n = n,content = content)

@mod.route('/time/')
def opinion_time():
    topic = request.args.get('topic', '')
    results = get_opinion_time(topic) # results=[[c_topic,start,end],....]

    if not results:
        return 'no data in mysql'
    
    time_list = []
    for i in range(0,len(results)):
        k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        time_list.append([k,results[i][1],results[i][2]])
    return json.dumps(time_list)

@mod.route('/ratio/')
def opinion_ratio():
    topic = request.args.get('topic', '')
    results = get_opinion_ratio(topic) # results=[[childtopic,ratio],....]

    if not results:
        return 'no data in mysql'
    
    ratio = dict()
    for i in range(0,len(results)):
        k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        ratio[k] = results[i][1]
    return json.dumps(ratio)

@mod.route('/keywords/')
def opinion_keywords():
    topic = request.args.get('topic', '')
    results = get_opinion_keywords(topic) # results=[{childtopic:[(keywords,weight)]},.....]

    if not results:
        return 'no data in mysql'

    ratio = dict()
    for i in range(0,len(results)):
        k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        ratio[k] = results[i][1]
    return json.dumps(ratio)

@mod.route('/weibos/')
def opinion_weibos():
    topic = request.args.get('topic', '')
    results = get_opinion_weibos(topic) # results=[{childtopic:[{weibos,weight}]},.....]

    if not results:
        return 'no data in mysql'

    f_news = TopkHeap(20)
    for i in range(0,len(results)):
        k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
        row = {'c_topic':k,'weight':results[i][1],'_id':results[i][2],'title':results[i][3],'content':results[i][4],'user':results[i][5],'time':results[i][6],'source':results[i][7],'c_source':results[i][8],'repeat':results[i][9]}
        f_news.Push((results[i][1],row))

    data = f_news.TopK()
    return json.dumps(data)

@mod.route('/rank/')
def opinion_rank():#自定义排序
    topic = request.args.get('topic', '')
    c_topic = request.args.get('c_topic', '')
    r_type = request.args.get('r_type', '')

    if not r_type:#异常返回
        return 'ranking type is wrong'

    results = get_opinion_weibos_rank(topic,c_topic)

    if not results:
        return 'no data in mysql'

    if r_type == 'weight':#按代表性排序
        f_news = TopkHeap(20)
        for i in range(0,len(results)):
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
            row = {'c_topic':k,'weight':results[i][1],'_id':results[i][2],'title':results[i][3],'content':results[i][4],'user':results[i][5],'time':results[i][6],'source':results[i][7],'c_source':results[i][8],'repeat':results[i][9]}
            f_news.Push((results[i][1],row))
    else:#按时间排序
        f_news = TopkHeap(20)
        for i in range(0,len(results)):
            k = results[i][0][0].encode('utf-8')+'-'+results[i][0][1].encode('utf-8')+'-'+results[i][0][2].encode('utf-8')
            row = {'c_topic':k,'weight':results[i][1],'_id':results[i][2],'title':results[i][3],'content':results[i][4],'user':results[i][5],'time':results[i][6],'source':results[i][7],'c_source':results[i][8],'repeat':results[i][9]}
            f_news.Push((results[i][5],row))

    data = f_news.TopK()
    return json.dumps(data)
    
    

    
