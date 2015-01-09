# -*- coding: utf-8 -*-

import os
import csv
import time
from bson.objectid import ObjectId
from ad_filter import ad_filter

import sys
AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../test/')
sys.path.append(AB_PATH)

from feature import extract_feature
from sort import text_weight_cal
from duplicate import duplicate
from clustering import kmeans, cluster_evaluation
from Database import CommentsManager, EventComments

def one_topic_calculation_comments(topicid):
    """
    """
    eventcomment = EventComments(topicid)
    results = eventcomment.getComments()

    inputs = []
    for r in results:
        r['title'] = ''
        r['content'] = r['content168'].encode('utf-8')
        item = ad_filter(r)
        if item['ad_label'] == 0:
            inputs.append(item)

    # kmeans 聚类及评价
    kmeans_results = kmeans(inputs, k=10)
    reserve_num = 5
    final_cluster_results, tfidf_dict = cluster_evaluation(kmeans_results, top_num=reserve_num, topk_freq=TOPK_FREQ_WORD, least_size=LEAST_SIZE, min_tfidf=None)
    inputs = []
    fw = open('items.txt', 'w')
    for label, items in final_cluster_results.iteritems():
        if label != 'other':
            fw.write('%s\n' % label)
            inputs.extend(items)

            for item in items:
                fw.write('%s\n' % item['content168'].encode('utf-8'))
    fw.close()

    #计算各簇特征词
    fw = open('feature.txt', 'w')
    cluster_feature = extract_feature(inputs)
    for label, fwords in cluster_feature.iteritems():
        fw.write('%s\n' % label)
        for k,v in fwords.iteritems():
            fw.write('%s\t%s\n' % (k, v))
    fw.close()

    #计算文本权重
    for input in inputs:
        weight = text_weight_cal(input, cluster_feature[input['label']])
        input["weight"] = weight


if __name__=="__main__":
    # 聚类评价时选取TOPK_FREQ_WORD的高频词
    TOPK_FREQ_WORD = 50

    # 聚类评价时最小簇的大小
    LEAST_SIZE = 8

    cm = CommentsManager()
    com_col_names = cm.get_comments_collection_name()
    for name in com_col_names:
        topicid = ObjectId(name.lstrip('comment_'))
        one_topic_calculation_comments(topicid)

