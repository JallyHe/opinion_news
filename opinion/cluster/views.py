#-*- coding:utf-8 -*-

import os
import sys
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
    AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../public/')
    sys.path.append(AB_PATH)
    from comment_module import comments_calculation_v2

    topicid = request.args.get('topicid', default_topic_id)
    subeventid = request.args.get('subeventid', 'global')

    ec = EventComments(topicid)
    if subeventid == 'global':
        comments = ec.getAllNewsComments()
    else:
        comments = ec.getCommentsBySubeventid(subeventid)

    if not comments:
        return json.dumps({"status":"fail"})

    cal_results = comments_calculation_v2(comments)
    features = cal_results['cluster_infos']['features']
    item_infos = cal_results['item_infos']

    senti_dict = {
            0:'中性',
            1:'积极',
            2:'愤怒',
            3:'悲伤'
        }

    cluster_ratio = dict()
    senti_ratio = dict()
    sentiment_comments = dict()
    cluster_results = dict()
    for comment in item_infos:
        if ('clusterid' in comment) and (comment['clusterid'] != 'nonsense') :
            clusterid = comment['clusterid']

            try:
                cluster_ratio[clusterid] += 1
            except KeyError:
                cluster_ratio[clusterid] = 1
            try:
                cluster_results[clusterid].append(comment)
            except KeyError:
                cluster_results[clusterid] = [comment]

        if 'sentiment' in comment:
            sentiment = comment['sentiment']

            try:
                senti_ratio[sentiment] += 1
            except KeyError:
                senti_ratio[sentiment] = 1
            try:
                sentiment_comments[sentiment].append(comment)
            except KeyError:
                sentiment_comments[sentiment] = [comment]

    ratio_results = dict()
    ratio_total_count = sum(cluster_ratio.values())
    for clusterid, ratio in cluster_ratio.iteritems():
        if clusterid in features:
            feature = features[clusterid]
            if feature and len(feature):
                ratio_results[','.join(feature[:3])] = float(ratio) / float(ratio_total_count)

    sentiratio_results = dict()
    sentiratio_total_count = sum(senti_ratio.values())
    for sentiment, ratio in senti_ratio.iteritems():
        if sentiment in senti_dict:
            label = senti_dict[sentiment]
            if label and len(label):
                sentiratio_results[label] = float(ratio) / float(sentiratio_total_count)

    for sentiment in sentiment_comments:
        sentiment_comments[sentiment].sort(key=lambda c:c['weight'], reverse=True)

    cluster_comments = dict()
    for clusterid, contents in cluster_results.iteritems():
        if clusterid in features:
            feature = features[clusterid]
            if feature and len(feature):
                cluster_comments[clusterid] = [','.join(feature[:5]),sorted(contents, key=lambda c: c['weight'], reverse=True)]

    return json.dumps({"ratio":ratio_results, "sentiratio":sentiratio_results,\
            "sentiment_comments":sentiment_comments, "cluster_comments":cluster_comments})

