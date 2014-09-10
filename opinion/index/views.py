#-*- coding:utf-8 -*-


import json
import time
import datetime
from opinion.model import *
from opinion.extensions import db
import search as searchModule
from flask import Blueprint, url_for, render_template, request, abort, flash, session, redirect, make_response
from get_result import get_opinion_time, get_opinion_ratio, get_opinion_keywords, get_opinion_weibos


mod = Blueprint('opinion_news', __name__, url_prefix='/index')

#tag = ['九一八','钓鱼岛','历史',]
comment = ['历史是不能改变的',]

def get_default_timerange():
    return u'20130901-20130901'

def get_default_topic():
    return u'中国'

def get_default_pointInterval():
    return {'zh': u'1小时', 'en': 3600}

def get_pointIntervals():
    return [{'zh': u'15分钟', 'en': 900}, {'zh': u'1小时', 'en': 3600}, {'zh': u'1天', 'en': 3600 * 24}]

def get_gaishu_yaosus():
    return {'zhibiao': u'指标分析', 'gaishu': u'概述分析'}

def get_deep_yaosus():
    return {'time': u'时间分析' , 'area': u'地域分析', 'moodlens': u'情绪分析', 'network': u'网络分析', 'semantic': u'语义分析'}

default_timerange = get_default_timerange()
default_topic = get_default_topic()
default_pointInterval = get_default_pointInterval()
pointIntervals = get_pointIntervals()
gaishu_yaosus = get_gaishu_yaosus()
deep_yaosus = get_deep_yaosus()

@mod.route('/')
def meaning():
        # 要素
    yaosu = 'semantic'

    # 话题关键词
    topic = request.args.get('query', default_topic)

    # 时间范围: 20130901-20130901
    time_range = request.args.get('time_range', default_timerange)

    # 时间粒度: 3600
    point_interval = request.args.get('point_interval', None)
    if not point_interval:
        point_interval = default_pointInterval
    else:
        for pi in pointIntervals:
            if pi['en'] == int(point_interval):
                point_interval = pi
                break

    return render_template('index/semantic.html', yaosu=yaosu, time_range=time_range, \
            topic=topic, pointInterval=point_interval, pointIntervals=pointIntervals, \
            gaishu_yaosus=gaishu_yaosus, deep_yaosus=deep_yaosus)

@mod.route('/time/')
def opinion_time():
    topic = request.args.get('topic', '')
    results = get_opinion_time(topic) # results=[{childtopic:[start_ts, end_ts]},....]
    return json.dumps(results)

@mod.route('/ratio/')
def opinion_ratio():
    topic = request.args.get('topic', '')
    results = get_opinion_ratio(topic) # results=[{childtopic:ratio},....]
    return json.dumps(results)

@mod.route('/keywords/')
def opinion_keywords():
    topic = request.args.get('topic', '')
    results = get_opinion_keywords(topic) # results=[{childtopic:[(keywords,weight)]},.....]
    return json.dumps(results)

@mod.route('/weibos/')
def opinion_weibos():
    topic = request.args.get('topic', '')
    results = get_opinion_weibos(topic) # results=[{childtopic:[{weibos,weight}]},.....]
    return json.dumps(results)
