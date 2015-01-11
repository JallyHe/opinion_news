#-*-coding=utf-8-*-

from utils import datetime2ts, _default_mongo_db

def get_db_names():
    results = _default_mongo_db().database_names()
    return [r for r in results if r.startswith('news')]

db_names = get_db_names()
MONGO_DB_NAME = db_names[4]
EVENTS_COLLECTION = "news_topic"
SUB_EVENTS_COLLECTION = "news_subevent"
SUB_EVENTS_FEATURE_COLLECTION = "news_subevent_feature"
EVENTS_NEWS_COLLECTION_PREFIX = "post_"

START_DATETIME = "2014-01-01 00:00:00"
END_DATETIME = "2014-11-04 00:00:00"

START_TS = datetime2ts(START_DATETIME)
END_TS = datetime2ts(END_DATETIME)

