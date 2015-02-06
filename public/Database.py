#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2015-01-11 11:00:00
# Version: 0.1.0
"""数据库操作的封装
"""

from utils import _default_mongo
from load_settings import load_settings

settings = load_settings()

MONGOD_HOST = settings.get('MONGOD_HOST')
MONGOD_PORT = settings.get('MONGOD_PORT')

MONGO_DB_NAME = settings.get('MONGO_DB_NAME')
SUB_EVENTS_COLLECTION = settings.get('SUB_EVENTS_COLLECTION')
EVENTS_COMMENTS_COLLECTION_PREFIX = settings.get('EVENTS_COMMENTS_COLLECTION_PREFIX')
EVENTS_COLLECTION = settings.get('EVENTS_COLLECTION')
SUB_EVENTS_FEATURE_COLLECTION = settings.get('SUB_EVENTS_FEATURE_COLLECTION')
COMMENTS_CLUSTER_COLLECTION = settings.get('COMMENTS_CLUSTER_COLLECTION')
EVENTS_NEWS_COLLECTION_PREFIX = settings.get('EVENTS_NEWS_COLLECTION_PREFIX')


class EventManager(object):
    """话题管理类
    """
    def __init__(self):
        self.mongo = _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGO_DB_NAME)
        self.events_collection = EVENTS_COLLECTION

    def getEventIDByName(self,name):
        result = self.mongo[self.events_collection].find_one({"topic": name})
        if result:
            return result['_id']
        else:
            return None


class CommentsManager(object):
    """评论管理
    """
    def __init__(self):
        self.mongo = _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGO_DB_NAME)

    def get_comments_collection_name(self):
        results = self.mongo.collection_names()
        return [r for r in results if r.startswith('comment_') and r != 'comment_cluster']


class EventComments(object):
    """评论数据管理
    """
    def __init__(self, topicid):
        self.id = topicid
        self.comments_cluster_collection = COMMENTS_CLUSTER_COLLECTION
        self.comments_collection = EVENTS_COMMENTS_COLLECTION_PREFIX + str(self.id)
        self.news_collection = EVENTS_NEWS_COLLECTION_PREFIX + str(self.id)
        self.mongo = _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGO_DB_NAME)

    def saveItem(self,item):
        """保存单条item
        """
        self.mongo[self.comments_collection].save(item)

    def getAllComments(self):
        """获取话题下所有的评论
        """
        results = self.mongo[self.comments_collection].find()
        return [r for r in results]

    def getSubeventComments(self, subeventid):
        """获取某个子事件（新闻）的评论
        """
        comments = []
        news_list = self.mongo[self.news_collection].find({"subeventid": subeventid})
        for news in news_list:
            news_id = news['_id']
            comments.extend(getNewsComments(news_id))

        return comments

    def getNewsIds(self):
        """获取评论表中不同的NewsId
        """
        return self.mongo[self.comments_collection].distinct("news_id")

    def getNewsComments(self, news_id):
        results = self.mongo[self.comments_collection].find({"news_id": news_id})
        return [r for r in results]

    def clear_cluster(self, news_id):
        self.mongo[self.comments_cluster_collection].remove({"eventid": self.id, \
                "news_id": news_id})

    def save_cluster(self, id, news_id, timestamp):
        self.mongo[self.comments_cluster_collection].save({"_id": id, "eventid": self.id, \
                "news_id": news_id, "timestamp": timestamp})

    def update_feature_words(self, id, feature_words):
        self.mongo[self.comments_cluster_collection].update({"_id": id}, {"$set": {"feature": feature_words}})


class News(object):
    """新闻类
    """
    def __init__(self, id):
        self.id = id
        self.otherClusterId = self.getOtherClusterId()
        self.mongo = _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGO_DB_NAME)

    def getOtherClusterId(self):
        """获取评论的其他簇id
        """
        return str(self.id) + '_other'


class Comment(object):
    """评论类
    """
    def __init__(self, id, topicid):
        self.id = id
        self.comments_collection = EVENTS_COMMENTS_COLLECTION_PREFIX + str(topicid)
        self.mongo = _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb=MONGO_DB_NAME)

    def update_comment_label(self, label):
        return self.mongo[self.comments_collection].update({"_id": self.id}, {"$set": {"clusterid": label}})

    def update_comment_weight(self, weight):
        return self.mongo[self.comments_collection].update({"_id": self.id}, {"$set": {"weight": weight}})

    def update_comment_sentiment(self, sentiment):
        return self.mongo[self.comments_collection].update({"_id": self.id}, {"$set": {"sentiment": sentiment}})

    def update_comment_global_weight(self, weight):
        return self.mongo[self.comments_collection].update({"_id": self.id}, {"$set": {"gweight": weight}})
