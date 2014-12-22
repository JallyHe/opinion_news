# -*- coding: utf-8 -*-

import os
import scws
import csv
import math
import time
import re
import datetime
from datetime import datetime
from datetime import date

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

cx_dict = ['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@','j']#关键词词性词典

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

def load_data(topic,input_data):#提取关键词主函数
'''
    提取关键词主函数
    输入数据：话题名、前两天分类的新闻数据
    输入数据格式：字典的序列
    输入数据示例：
    [{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳,'lable':类别标签}]

    输出数据：每类的关键词及权重
    输出数据格式：字典
    {'类别标号1':[[32,'我们'],[43,'他们']....]}
'''

    data = dict()
    for i in range(0,len(input_data)):
        mid = input_data[i]['_id']
        place = input_data[i]['source_from_name']
        t = input_data[i]['title']
        c = input_data[i]['content']
        p_time = input_data[i]['timestamp']
        lable = input_data[i]['lable']
        if data.has_key(str(lable)):
            item = data[str(lable)]
            item.append([mid,place,t,c,p_time])
            data[str(lable)] = item
        else:
            item = []
            item.append([mid,place,t,c,p_time])
            data[str(lable)] = item
        
    black = load_black_words()
    sw = load_scws()
    f_dict = dict()
    for k,v in data.iteritems():
        c_row = dict()
        total_count = 0
        for i in range(0,len(v)):
            text = v[i][2]
            words = sw.participle(text)           
            for c_word in words:
                if (c_word[1] in cx_dict) and (3 < len(c_word[0]) < 30 or c_word[0] in single_word_whitelist) and (c_word[0] not in black):#选择分词结果的名词、动词、形容词，并去掉单个词
                    if c_row.has_key(str(c_word[0])):
                        c_row[str(c_word[0])] = c_row[str(c_word[0])] + 5
                    else:
                        c_row[str(c_word[0])] = 5
                    total_count = total_count + 5
            text = v[i][3]
            words = sw.participle(text)         
            for c_word in words:
                if (c_word[1] in cx_dict) and (3 < len(c_word[0]) < 30 or c_word[0] in single_word_whitelist) and (c_word[0] not in black):#选择分词结果的名词、动词、形容词，并去掉单个词
                    if c_row.has_key(str(c_word[0])):
                        c_row[str(c_word[0])] = c_row[str(c_word[0])] + 1
                    else:
                        c_row[str(c_word[0])] = 1
                    total_count = total_count + 1
        c_data = dict()
        for key,value in c_row.iteritems():
            if (float(value)/float(total_count) >= 0.8) or (value <= 3):
                continue
            c_data[key] = float(value)/float(total_count)
        f_dict[str(k)] = c_data

    word_dict = dict()
    for k,v in f_dict.iteritems():
        n = len(v)
        row = TopkHeap(n*0.5)
        for k1,v1 in v.iteritems():
            idf = find_idf(k1,k,f_dict)#统计词语在其他类别中出现的次数
            row.Push((idf*v1,k1))
        word_dict[k] = row.TopK()

    return word_dict



