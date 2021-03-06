#-*- coding:utf-8 -*-

import json
from flask import Blueprint, render_template, request
from opinion.global_utils import ts2datetime, ts2date
from opinion.Database import EventComments, EventManager, Feature, DbManager, News, Event
from opinion.global_config import default_topic_name, default_news_id, emotions_vk, default_news_url

mod = Blueprint('comment', __name__, url_prefix='/comment')

em = EventManager()

@mod.route('/')
def index():
    """返回页面
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    topicid = em.getEventIDByName(topic_name)
    eventcomment = EventComments(topicid)

    news = News(news_id, topicid)
    news_subeventid = news.get_news_subeventid()
    news_url = news.get_news_url()

    comments = eventcomment.getNewsComments(news_id)
    if not comments:
        return 'no comments'

    return render_template('index/comment.html', topic=topic_name, topic_id=topicid, \
            news_id=news_id, news_subeventid=news_subeventid, news_url=news_url)


@mod.route('/ratio/')
def ratio():
    """子观点占比
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    topicid = em.getEventIDByName(topic_name)

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

@mod.route('/sentiratio/')
def sentiratio():
    """
    情绪占比
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    topicid = em.getEventIDByName(topic_name)

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

@mod.route('/sentiment/')
def sentiment():
    """评论情绪
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    sort_by = request.args.get('sort', 'weight')
    topicid = em.getEventIDByName(topic_name)

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
    for sentiment in sentiment_comments:
        sentiment_comments[sentiment].sort(key=lambda c:c[sort_by], reverse=True)

    return json.dumps(sentiment_comments)

@mod.route('/keywords/')
def keywords():
    """关键词
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    topicid = em.getEventIDByName(topic_name)

    eventcomment = EventComments(topicid)
    clusterids = eventcomment.get_cluster_ids(news_id)

    results = dict()
    for clusterid in clusterids:
        fwords = eventcomment.get_feature_words(clusterid)
        results[clusterid] = [fwords[:5], fwords]

    return json.dumps(results)

@mod.route('/cluster/')
def cluster():
    """展现聚类结果
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    sort_by = request.args.get('sort', 'weight')
    topicid = em.getEventIDByName(topic_name)

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

    '''
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
    '''

    results = dict()
    for clusterid in cluster_results:
        feature = eventcomment.get_feature_words(clusterid)
        if feature and len(feature):
            cluster_results[clusterid].sort(key=lambda c: c[sort_by], reverse=True)
            results[clusterid] = [','.join(feature[:5]), cluster_results[clusterid]]

    return json.dumps(results)

@mod.route('/urlsearch/')
def urlsearch():
    """返回页面
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topicid = em.getEventIDByName(topic_name)

    news_url = request.args.get('url', default_news_url) # news url
    news_url = 'http://news.sina.com.cn/c/2014-10-09/145630963839.shtml'

    event = Event(topicid)
    news_id = event.get_news_id_by_url(news_url)
    if not news_id:
        return json.dumps({"news_id":None})

    eventcomment = EventComments(topicid)
    comments = eventcomment.getNewsComments(news_id)
    if not comments:
        return json.dumps({"news_id":None})

    return json.dumps({"news_id":news_id})
