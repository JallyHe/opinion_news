# -*- coding: utf-8 -*-

import os
import sys
from global_utils import datetime2ts, _default_mongo_db
AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../public/')
sys.path.append(AB_PATH)
from comment_module import MIN_CLUSTER_NUM, MAX_CLUSTER_NUM, CLUSTER_EVA_MIN_SIZE, \
        COMMENT_CLUSTERING_PROCESS_FOR_CLUTO_VERSION

IS_PROD = 0

if IS_PROD == 1:
    pass
else:
    # 219.224.135.47
    default_topic_name = u'APEC2014'
    default_weibo_topic_name = u'APEC2014-微博'
    default_topic_id = '54916b0d955230e752f2a94e'
    default_news_id = '1-1-30963839'
    default_weibo_news_id = 'weibo'
    default_news_url = 'http://news.sina.com.cn/c/2014-10-09/145630963839.shtml'
    default_subevent_id = '7325a077-76b8-4b03-bbed-d8f0faaf28fd'
    # ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    ALLOWED_EXTENSIONS = set(['jl'])
    UPLOAD_FOLDER = '/tmp/upload/'
    default_task_id = default_topic_id
    default_min_cluster_num = MIN_CLUSTER_NUM
    default_max_cluster_num = MAX_CLUSTER_NUM
    default_cluster_eva_min_size = CLUSTER_EVA_MIN_SIZE
    default_vsm = COMMENT_CLUSTERING_PROCESS_FOR_CLUTO_VERSION

def get_db_names():
    results = _default_mongo_db().database_names()
    return [r for r in results if r.startswith('news')]

db_names = get_db_names()
MONGO_DB_NAME = db_names[0]
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
