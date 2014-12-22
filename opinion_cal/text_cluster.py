# -*- coding: utf-8 -*-

import os
import scws
import csv
import time
import re
import datetime
from datetime import datetime
from datetime import date
import heapq
import math
import Levenshtein
import milk
import numpy as np
import json
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

SCWS_ENCODING = 'utf-8'
SCWS_RULES = '/usr/local/scws/etc/rules.utf8.ini'
CHS_DICT_PATH = '/usr/local/scws/etc/dict.utf8.xdb'
CHT_DICT_PATH = '/usr/local/scws/etc/dict_cht.utf8.xdb'
IGNORE_PUNCTUATION = 1

ABSOLUTE_DICT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), './dict'))
CUSTOM_DICT_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'userdic.txt')
EXTRA_STOPWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'stopword.txt')
EXTRA_EMOTIONWORD_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'emotionlist.txt')
EXTRA_ONE_WORD_WHITE_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'one_word_white_list.txt')
EXTRA_BLACK_LIST_PATH = os.path.join(ABSOLUTE_DICT_PATH, 'black.txt')

cx_dict = ['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@']#关键词词性词典

class TopkHeap(object):
    def __init__(self, k):
        self.k = k
        self.data = []
 
    def Push(self, elem):
        if len(self.data) < self.k:
            heapq.heappush(self.data, elem)
        else:
            topk_small = self.data[0][0]
            if elem[0] > topk_small:
                heapq.heapreplace(self.data, elem)
 
    def TopK(self):
        return [x for x in reversed([heapq.heappop(self.data) for x in xrange(len(self.data))])]

def load_one_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_ONE_WORD_WHITE_LIST_PATH)]
    return one_words

def load_black_words():
    one_words = [line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)]
    return one_words

single_word_whitelist = set(load_one_words())
single_word_whitelist |= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789')

def load_scws():
    s = scws.Scws()
    s.set_charset(SCWS_ENCODING)

    s.set_dict(CHS_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CHT_DICT_PATH, scws.XDICT_MEM)
    s.add_dict(CUSTOM_DICT_PATH, scws.XDICT_TXT)

    # 把停用词全部拆成单字，再过滤掉单字，以达到去除停用词的目的
    s.add_dict(EXTRA_STOPWORD_PATH, scws.XDICT_TXT)
    # 即基于表情表对表情进行分词，必要的时候在返回结果处或后剔除
    s.add_dict(EXTRA_EMOTIONWORD_PATH, scws.XDICT_TXT)

    s.set_rules(SCWS_RULES)
    s.set_ignore(IGNORE_PUNCTUATION)
    return s

def cut_word(re_data,flag,cluster):#标题分类
   
    title = dict()
    title_count = dict()
    weibo_word = []
    black = load_black_words()
    sw = load_scws()
    word_count = []
    for i in range(0,len(re_data)):
        mid = re_data[i]['_id']
        place = re_data[i]['source_from_name']
        t = re_data[i]['title']
        c = re_data[i]['content']
        p_time = re_data[i]['timestamp']
        if title_count.has_key(str(t)):
            item = title_count[str(t)]
            item.append(mid)
            title_count[str(t)] = item
        else:
            item = []
            item.append(mid)
            title_count[str(t)] = item
        string = t + '_' + c
        words = sw.participle(string)
        for word in words:
            if (word[1] in cx_dict) and (3 < len(word[0]) < 30 or word[0] in single_word_whitelist) and (word[0] not in black):
                if word[0] not in weibo_word:
                    weibo_word.append(word[0])
                    word_count.append(0)
        title[str(mid)] = [str(t),str(c),p_time,place]
    
    #统计每个属性的值    
    for k,v in title.iteritems():
        string = v[0] + '_' + v[1]
        for i in range(0,len(weibo_word)):
            if weibo_word[i] in string:
                word_count[i] = word_count[i] + 1

    new_weibo = []
    for i in range(0,len(word_count)):
        if word_count[i] >= 5:
            new_weibo.append(weibo_word[i])

    notin = []
    data = dict()
    for k,v in title.iteritems():
        f = 0
        row = []
        string = v[0] + '_' + v[1]
        for i in new_weibo:
            if i in string:
                n = string.count(i)
                row.append(n)
                f = 1
            else:
                row.append(0)
        if f == 1:
            data[k] = row
        else:
            notin.append(k)

    #聚类
    feature = []
    word = []
    for k,v in data.iteritems():
        word.append([k,title[k][0],title[k][1],title[k][2],title[k][3]])
        feature.append((v))
    features = np.array(feature)
    cluster_ids = milk.kmeans(features, cluster)

    return word, cluster_ids#新闻、聚类标签

def start_cluster(inputs,topic,cluster):#文本聚类主函数
    '''
    文本聚类主函数
    输入参数：新闻数据、话题名、聚类个数
    新闻数据格式：字典的序列
    新闻数据示例:
    [{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳}]

    输出参数：类别标签
    类别标签格式：字典的序列
    类别标签示例：
    [{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳,'lable':类别标签}]
    '''

    news, cluster_ids = cut_word(inputs,topic,cluster)#进行新闻的分类与聚类

    lable_data = []
    for i in range(0,len(news)):
        lable_data.append({'_id':news[i][0],'source_from_name':news[i][3],'title':news[i][1],'content':news[i][2],'timestamp':news[i][4],'lable':cluster_ids[0][i]})          

    return lable_data

