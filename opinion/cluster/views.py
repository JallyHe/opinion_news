#-*- coding:utf-8 -*-

import json
from bson.objectid import ObjectId
from flask import Blueprint, render_template, request
from opinion.global_utils import ts2datetime, ts2date
from opinion.Database import Event, EventComments, EventManager, Feature, DbManager, News
from opinion.global_config import default_topic_name, default_topic_id, default_news_id, emotions_vk, default_subevent_id

mod = Blueprint('cluster', __name__, url_prefix='/cluster')

em = EventManager()

@mod.route('/')
def index():
    """返回页面
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topicid = em.getEventIDByName(topic_name)
    subevent_id = request.args.get('subevent_id', 'global')
    '''
    eventcomment = EventComments(topicid)

    news = News(news_id, topicid)
    news_subeventid = news.get_news_subeventid()
    news_url = news.get_news_url()
    '''

    return render_template('index/topic_comment.html', topic=topic_name, topic_id=topicid, subevent_id=subevent_id)

@mod.route('/topics/')
def topics():
    """获取新闻话题信息
    """
    results = []
    events = em.getEvents()

    for event in events:
        results.append({'_id': str(event['_id']), 'topic': event['topic']})

    return json.dumps(results)


@mod.route('/subevents/')
def subevents():
    """获取子事件信息
    """
    subevents = []
    events = em.getEvents()
    for event in events:
        e = Event(event['_id'])
        subevents.extend(e.getSubEvents())

    results_dict = dict()
    for s in subevents:
        feature = Feature(s['_id'])
        fwords = feature.get_newest()
        words = sorted(fwords.iteritems(), key=lambda(k, v): v, reverse=True)[:5]
        name = ','.join([k for k, v in words])
        subevent = {'_id': s['_id'], 'eventid': str(s['eventid']), 'name': name}
        try:
            results_dict[str(s['eventid'])].append(subevent)
        except KeyError:
            results_dict[str(s['eventid'])] = [subevent]

    return json.dumps(results_dict)


@mod.route('/comments_list/')
def comments_list():
    import os
    import sys
    AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../public/')
    sys.path.append(AB_PATH)
    from comment_module import comments_calculation

    topicid = request.args.get('topicid')
    subeventid = request.args.get('subeventid', 'global')

    ec = EventComments(topicid)
    if subeventid == 'global':
        comments = ec.getAllNewsComments()
    else:
        comments = ec.getCommentsBySubeventid(subeventid)

    results = comments_calculation(comments)

    return json.dumps(results)


@mod.route('/ratio/')
def ratio():
    """子观点占比
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    subevent_id = request.args.get('subevent_id', 'global')
    topicid = em.getEventIDByName(topic_name)

    '''
    eventcomment = EventComments(topicid)
    comments = eventcomment.getNewsComments(news_id)

    cluster_ratio = dict()
    for comment in comments:
        if 'clusterid' in comment:
            clusterid = comment['clusterid']

            try:
                cluster_ratio[clusterid] += 1
            except KeyError:
                cluster_ratio[clusterid] = 1

    results = dict()
    total_count = sum(cluster_ratio.values())
    for clusterid, ratio in cluster_ratio.iteritems():
        feature = eventcomment.get_feature_words(clusterid)
        if feature and len(feature):
            results[','.join(feature[:3])] = float(ratio) / float(total_count)

    return json.dumps(results)
    '''
    return json.dumps({})

@mod.route('/sentiratio/')
def sentiratio():
    """
    情绪占比
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    subevent_id = request.args.get('subevent_id', 'global')
    topicid = em.getEventIDByName(topic_name)
    '''
    eventcomment = EventComments(topicid)
    comments = eventcomment.getNewsComments(news_id)

    senti_dict = {
            0:'中性',
            1:'积极',
            2:'愤怒',
            3:'悲伤'
        }
    senti_ratio = dict()
    for comment in comments:
        if 'sentiment' in comment:
            sentiment = comment['sentiment']

            try:
                senti_ratio[sentiment] += 1
            except KeyError:
                senti_ratio[sentiment] = 1

    results = dict()
    total_count = sum(senti_ratio.values())
    for sentiment, ratio in senti_ratio.iteritems():
        label = senti_dict[sentiment]
        if label and len(label):
            results[label] = float(ratio) / float(total_count)

    return json.dumps(results)
    '''
    return json.dumps({})

@mod.route('/sentiment/')
def sentiment():
    """评论情绪
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    subevent_id = request.args.get('subevent_id', 'global')
    topicid = em.getEventIDByName(topic_name)
    '''
    eventcomment = EventComments(topicid)
    comments = eventcomment.getNewsComments(news_id)

    sentiment_comments = dict()
    for comment in comments:
        if 'sentiment' in comment:
            sentiment = comment['sentiment']
            try:
                sentiment_comments[sentiment].append(comment)
            except KeyError:
                sentiment_comments[sentiment] = [comment]

    return json.dumps(sentiment_comments)
    '''
    return json.dumps({})

@mod.route('/cluster/')
def cluster():
    """展现聚类结果
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    subevent_id = request.args.get('subevent_id', 'global')
    topicid = em.getEventIDByName(topic_name)
    '''
    eventcomment = EventComments(topicid)
    comments = eventcomment.getNewsComments(news_id)
    cluster_results = dict()
    for comment in comments:
        if 'clusterid' in comment:
            clusterid = comment['clusterid']
            try:
                cluster_results[clusterid].append(comment)
            except KeyError:
                cluster_results[clusterid] = [comment]

    sentiment_dict = dict()
    for clusterid, comments in cluster_results.iteritems():
        positive = 0
        negative = 0
        for c in comments:
            if c['sentiment'] == 1:
                positive += 1
            if c['sentiment'] in [2, 3]:
                negative += 1

        sentiment_dict[clusterid] = u'(积极：' + str(positive) + ',' + u'消极：' + str(negative) + ')'

    results = dict()
    for clusterid, comments in cluster_results.iteritems():
        feature = eventcomment.get_feature_words(clusterid)
        if feature and len(feature):
            results[clusterid] = [','.join(feature[:5]),sorted(comments, key=lambda c: c['weight'], reverse=True)]

    return json.dumps(results)
    '''
    return json.dumps({})
