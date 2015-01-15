# -*- coding: utf-8 -*-

import os
import csv
import time
import math
from bson.objectid import ObjectId
from ad_filter import ad_filter
from triple_sentiment_classifier import triple_classifier

import sys
AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../test/')
sys.path.append(AB_PATH)

from feature import extract_feature
from sort import text_weight_cal
from duplicate import duplicate
from Database import CommentsManager, EventComments, Comment, News
from config import emotions_vk
from comment_clustering_tfidf_v2 import kmeans, tfidf_v2, text_classify, cluster_evaluation, global_text_weight


def text_kmeans_clustering():
    # 聚类评价时选取TOPK_FREQ_WORD的高频词
    TOPK_FREQ_WORD = 50

    # 聚类评价时最小簇的大小
    LEAST_SIZE = 8

    eventcomment = EventComments(topicid)
    newsIds = eventcomment.getNewsIds()

    for news_id in newsIds:
        results = eventcomment.getNewsComments(news_id)

        inputs = []
        for r in results:
            r['title'] = ''
            r['content'] = r['content168'].encode('utf-8')
            r['text'] = r['content168']
            item = ad_filter(r)
            if item['ad_label'] == 0:
                inputs.append(item)

        # 情绪计算
        for r in inputs:
            sentiment = triple_classifier(r)
            comment = Comment(r['_id'])
            comment.update_comment_sentiment(sentiment)

        # kmeans 聚类及评价
        kmeans_results = kmeans(inputs, k=10)
        reserve_num = 5
        final_cluster_results, tfidf_dict = cluster_evaluation(kmeans_results, \
                top_num=reserve_num, topk_freq=TOPK_FREQ_WORD, least_size=LEAST_SIZE, min_tfidf=None)

        inputs = []
        for label, items in final_cluster_results.iteritems():
            if label != 'other':
                inputs.extend(items)

            for item in items:
                news = News(item['news_id'])

                if label == 'other':
                    label = news.otherClusterId

                comment = Comment(item['_id'])
                comment.update_comment_label(label)

            eventcomment.save_cluster(label, news_id, int(time.time()))

        #计算各簇特征词
        cluster_feature = extract_feature(inputs)
        for label, fwords in cluster_feature.iteritems():
            eventcomment.update_feature_words(label, fwords)

        #计算文本权重
        for input in inputs:
            weight = text_weight_cal(input, cluster_feature[input['label']])
            comment = Comment(input['_id'])
            comment.update_comment_weight(weight)


def one_topic_calculation_comments(topicid):
    """对评论进行聚类
    """
    eventcomment = EventComments(topicid)
    newsIds = eventcomment.getNewsIds()

    for news_id in newsIds:
        eventcomment.clear_cluster(news_id)
        results = eventcomment.getNewsComments(news_id)
        news = News(news_id)

        inputs = []
        for r in results:
            r['title'] = ''
            r['content'] = r['content168'].encode('utf-8')
            r['text'] = r['content168']
            item = ad_filter(r)
            if item['ad_label'] == 0:
                inputs.append(item)

        # 情绪计算
        for r in inputs:
            sentiment = triple_classifier(r)
            comment = Comment(r['_id'], topicid)
            comment.update_comment_sentiment(sentiment)

        tfidf_word = tfidf_v2(inputs)

        #聚类个数=过滤后文本数/2向上取整，大于10的取10
        kmeans_cluster_number = int(math.ceil(float(len(inputs)) / 5.0))
        if kmeans_cluster_number > 10:
            kmeans_cluster_number = 10
        if kmeans_cluster_number < 5:
            kmeans_cluster_number = 5

        # 评论词聚类
        word_label = kmeans(tfidf_word, inputs, k=kmeans_cluster_number)

        # 计算全局文本权重
        for r in inputs:
            gweight = global_text_weight(r['content'], tfidf_word)
            comment = Comment(r['_id'], topicid)
            comment.update_comment_global_weight(gweight)

        # 评论文本分类
        results = text_classify(inputs, word_label, tfidf_word)

        #簇评价
        reserved_num = int(math.ceil(float(kmeans_cluster_number) / 2.0))
        LEAST_CLUSET_SIZE = 3 # 最小的簇大小
        TOPK_FREQ = 10
        TOPK_WEIGHT = 5
        final_cluster_results = cluster_evaluation(results, top_num=reserved_num, topk_freq=TOPK_FREQ, \
                least_freq=LEAST_FREQ, least_size=LEAST_CLUSTER_SIZE, topk_weight=TOPK_WEIGHT)
        for label, items in final_cluster_results.iteritems():
            if label == 'other':
                label = news.otherClusterId

            if len(items):
                eventcomment.save_cluster(label, news_id, int(time.time()))

            if label != news.otherClusterId:
                fwords = word_label[label]
                eventcomment.update_feature_words(label, fwords)

            for item in items:
                comment = Comment(item['_id'], topicid)
                comment.update_comment_label(label)
                comment.update_comment_weight(item['weight'])


if __name__=="__main__":
    cm = CommentsManager()
    com_col_names = cm.get_comments_collection_name()
    for name in com_col_names:
        topicid = ObjectId(name.lstrip('comment_'))
        one_topic_calculation_comments(topicid)

