#-*- coding:utf-8 -*-

import json
from flask import Blueprint, render_template, request
from opinion.global_utils import ts2datetime, ts2date
from opinion.Database import Event, EventComments, EventManager, Feature, DbManager, News
from opinion.global_config import default_topic_name, default_news_id, emotions_vk

mod = Blueprint('cluster', __name__, url_prefix='/cluster')

em = EventManager()

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
    eventid = request.args.get('eventid', 'global')

    subevents = []
    if eventid == 'global':
        events = em.getEvents()
        for event in events:
            e = Event(event['_id'])
            subevents.extend(e.getSubEvents())

    else:
        eventid = ObjectId(eventid)
        e = Event(eventid)
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
    topicid = request.args.get('topicid')
    subeventid = request.args.get('subeventid', 'global')

