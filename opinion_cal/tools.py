#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

from utils import datetime2ts
from Event import Event, EventManager

if __name__ == '__main__':
    em = EventManager()

    topicname = u'APEC2014'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-11-04 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)

    topicname = u'手术台自拍'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-12-14 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)

    topicname = u'呼格案'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-12-01 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)

    topicname = u'复旦投毒案'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-12-01 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)

    topicname = u'非法占中'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-12-01 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)

    topicname = u'马航失联'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-03-10 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)

    topicname = u'博鳌论坛'
    topicid = em.getEventIDByName(topicname)
    event = Event(topicid)
    event.initializing()
    start_datetime = "2014-04-10 00:00:00"
    start_ts = datetime2ts(start_datetime)
    event.setStartts(start_ts)
