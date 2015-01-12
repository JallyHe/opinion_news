#-*-coding=utf-8-*-

from utils import datetime2ts


MONGO_DB_NAME = "news"
EVENTS_COLLECTION = "news_topic"
SUB_EVENTS_COLLECTION = "news_subevent"
SUB_EVENTS_FEATURE_COLLECTION = "news_subevent_feature"
EVENTS_NEWS_COLLECTION_PREFIX = "post_"
EVENTS_COMMENTS_COLLECTION_PREFIX = "comment_"
COMMENTS_CLUSTER_COLLECTION = 'comment_cluster'

START_DATETIME = "2014-01-01 00:00:00"
END_DATETIME = "2014-11-04 00:00:00"

START_TS = datetime2ts(START_DATETIME)
END_TS = datetime2ts(END_DATETIME)

emotions_vk = {0: '无倾向', 1: '高兴', 2: '愤怒', 3: '悲伤', 4: '新闻'}
emotions_kv = {'happy': 1, 'angry': 2, 'sad': 3, 'news': 4}
emotions_zh_kv = {'happy': '高兴', 'angry': '愤怒', 'sad': '悲伤', 'news': '新闻'}
