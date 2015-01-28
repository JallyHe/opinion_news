#-*- coding:utf-8 -*-

import json
from flask import Blueprint, render_template, request
from opinion.global_utils import ts2datetime, ts2date
from opinion.Database import EventComments, EventManager, Feature, DbManager, News
from opinion.global_config import default_topic_name, default_news_id, emotions_vk

mod = Blueprint('comment', __name__, url_prefix='/comment')

em = EventManager()

@mod.route('/')
def index():
    """返回页面
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
    topicid = em.getEventIDByName(topic_name)
    news = News(news_id, topicid)
    news_subeventid = news.get_news_subeventid()
    eventcomment = EventComments(topicid)

    return render_template('index/comment.html', topic=topic_name, topic_id=topicid, \
            news_id=news_id, news_subeventid=news_subeventid)


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
            results[','.join(feature[:5])] = float(ratio) / float(total_count)

    return json.dumps(results)


@mod.route('/sentiment/')
def sentiment():
    """评论情绪
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    news_id = request.args.get('news_id', default_news_id)
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
            results[clusterid] = [','.join(feature[:5]) + sentiment_dict[clusterid], \
                sorted(comments, key=lambda c: c['weight'], reverse=True)]

    return json.dumps(results)

