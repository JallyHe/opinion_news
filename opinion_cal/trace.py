# -*- coding: utf-8 -*-
# User: linhaobuaa
# Date: 2014-12-21 22:00:00
# Version: 0.1.0

import re
import os
import csv
import math
import time


def subevent_classifier(text, labels, feature_words):
    """input
           text: 单条文本
           labels: 子事件标签，list
           feature_words: 各子事件的特征词，与上述标签对应，list
       output
           
    """
    max_count = 0
    max_lable = -1
    sum_count = 0
    for k,v in word_dict.iteritems():
        count = 0
        sum_count = 0
        for i in range(0,len(v)):
            sum_count = sum_count + v[i][0]
            if v[i][1] in text:
                count = count + v[i][0]
        s_weight = float(sum_count)*0.05
        if count > s_weight:
            if count > max_count:
                max_lable = k
                max_count = count
        else:
            continue

    return max_lable


def text_classify(input_data, r_words):
    '''
    话题跟踪主函数
    输入数据：话题名、新闻数据、每一类的关键词
    输入数据格式：
    新闻数据：字典的序列，如：[{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳}]
    每一类的关键词：字典，如：{'类别标号1':[[32,'我们'],[43,'他们']....]}

    输出数据：有演化的类标签、演化的新闻、其他类新闻
    输出数据格式：
    有演化的类标签：序列，如['类别标号1','类别标号2','类别标号3'...]
    演化的新闻：字典，如{'mid':[新闻来源，标题，内容，时间戳，类标签]}
    其他类新闻：字典，如{'mid':[新闻来源，标题，内容，时间戳，类标签]}
    '''

    data_lable = dict()
    data_other = dict()
    ex_lable = []
    for item in input_data:
        p_time = item['timestamp']
        mid = item['_id']
        place = item['source_from_name']
        t = item['title']
        c = item['content']
        text = t + '__' + c
        l = find_cluster(text,r_words)
        if l not in ex_lable:
            ex_lable.append(l)
        if l == -1:
            data_other[str(mid)] = [place,str(t),str(c),p_time,l]
        else:
            data_lable[str(mid)] = [place,str(t),str(c),p_time,l]

    return ex_lable,data_lable,data_other
