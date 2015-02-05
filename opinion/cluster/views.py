#-*- coding:utf-8 -*-

import os
import sys
import json
from flask import Blueprint, render_template, request
from opinion.global_utils import ts2datetime, ts2date
from opinion.Database import Event, EventComments, EventManager, Feature
from opinion.global_config import default_topic_name, default_topic_id, default_subevent_id,\
        default_kmeans_number, default_reserve_number

mod = Blueprint('cluster', __name__, url_prefix='/cluster')

em = EventManager()
temp_file = 'cluster_dump_dict.txt'

@mod.route('/')
def index():
    """返回页面
    """
    topic_name = request.args.get('query', default_topic_name) # 话题名
    topicid = em.getEventIDByName(topic_name)
    subevent_id = request.args.get('subevent_id', 'global')
    kmeans = request.args.get('kmeans', default_kmeans_number)
    reserve = request.args.get('reserve', default_reserve_number)

    return render_template('index/topic_comment.html', topic=topic_name, topic_id=topicid, subevent_id=subevent_id,\
            kmeans=kmeans, reserve=reserve)

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

    if os.path.exists(temp_file):
        os.remove(temp_file)
    AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../public/')
    sys.path.append(AB_PATH)
    from comment_module import comments_calculation_v2

    topicid = request.args.get('topicid', default_topic_id)
    subeventid = request.args.get('subeventid', 'global')
    kmeans = request.args.get('kmeans', default_kmeans_number) # KMEANS聚类数
    reserve = request.args.get('reserve', default_reserve_number) # 保留聚簇数
    print kmeans, reserve

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
    sentiment_results = dict()
    cluster_results = dict()
    for comment in item_infos:
        if ('clusterid' in comment) and (comment['clusterid'][:8] != 'nonsense') : 
            clusterid = comment['clusterid']

            try:
                cluster_ratio[clusterid] += 1
            except KeyError:
                cluster_ratio[clusterid] = 1
            try:
                cluster_results[clusterid].append(comment)
            except KeyError:
                cluster_results[clusterid] = [comment]

        if ('sentiment' in comment) and (comment['sentiment'] in senti_dict) and ('clusterid' in comment) \
                and (comment['clusterid'][:8] != 'nonsense'):
            sentiment = comment['sentiment']

            try:
                senti_ratio[sentiment] += 1
            except KeyError:
                senti_ratio[sentiment] = 1
            try:
                sentiment_results[sentiment].append(comment)
            except KeyError:
                sentiment_results[sentiment] = [comment]

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

    # 情感分类去重
    sentiment_dump_dict = dict()
    for sentiment, contents in sentiment_results.iteritems():
        dump_dict = dict()
        for comment in contents:
            same_from_sentiment = comment["same_from_sentiment"]
            try:
                dump_dict[same_from_sentiment].append(comment)
            except KeyError:
                dump_dict[same_from_sentiment] = [comment]
        sentiment_dump_dict[sentiment] = dump_dict


    # 子观点分类去重
    cluster_dump_dict = dict()
    for clusterid, contents in cluster_results.iteritems():
        if clusterid in features:
            feature = features[clusterid]
            if feature and len(feature):
                dump_dict = dict()
                for comment in contents:
                    same_from_cluster = comment["same_from"]
                    try:
                        dump_dict[same_from_cluster].append(comment)
                    except KeyError:
                        dump_dict[same_from_cluster] = [comment]
                    cluster_dump_dict[clusterid] = dump_dict

    dump_file = open(temp_file, 'w')
    dump_file.write(json.dumps({"features":features, "senti_dump_dict":sentiment_dump_dict,\
            "cluster_dump_dict":cluster_dump_dict}));
    dump_file.close();

    return json.dumps({"ratio":ratio_results, "sentiratio":sentiratio_results,})

@mod.route('/sentiment_comments/')
def sentiment_comments():

    sort_by = request.args.get('sort', 'weight')
    dump_file = open(temp_file,'r')
    dump_dict = json.loads(dump_file.read())
    sentiment_dump_dict = dump_dict["senti_dump_dict"]
    dump_file.close()
    sentiment_comments = dict()
    for sentiment, dump_dict in sentiment_dump_dict.iteritems():
        for same_from in dump_dict:
            dump_dict[same_from].sort(key=lambda c:c[sort_by], reverse=True)
            try:
                sentiment_comments[sentiment].append(dump_dict[same_from][0])
            except KeyError:
                sentiment_comments[sentiment] = [dump_dict[same_from][0]]
        sentiment_comments[sentiment].sort(key=lambda c:c[sort_by], reverse=True)
    return json.dumps(sentiment_comments)

@mod.route('/cluster_comments/')
def cluster_comments():

    sort_by = request.args.get('sort', 'weight')
    dump_file = open(temp_file,'r')
    dump_dict = json.loads(dump_file.read())
    cluster_dump_dict = dump_dict["cluster_dump_dict"]
    features = dump_dict["features"]
    dump_file.close()

    cluster_comments = dict()
    for clusterid, dump_dict in cluster_dump_dict.iteritems():
        if clusterid in features:
            feature = features[clusterid]
            if feature and len(feature):
                cluster_comments[clusterid] = []
                cluster_comments[clusterid].append(','.join(feature[:5]))
                dump_list = []
                for same_from in dump_dict:
                    dump_dict[same_from].sort(key=lambda c:c[sort_by], reverse=True)
                    dump_list.append(dump_dict[same_from][0])
                dump_list.sort(key=lambda c:c[sort_by], reverse=True)
                cluster_comments[clusterid].append(dump_list)

    return json.dumps(cluster_comments)
