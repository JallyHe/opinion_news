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

def write_rate(topic,count):

    max_e = -1
    min_e = 99999999
    for k,v in count.iteritems():
        if v > max_e:
            max_e = v
        if v < min_e:
            min_e = v

    r_rate = dict()
    for k,v in count.iteritems():
        s = float(v - min_e)/float(max_e - min_e)
        r_rate[k] = s

    return  r_rate

def write_z_count(topic,total):

    sum_count = 0
    for k,v in total.iteritems():
        sum_count = sum_count + int(v)

    z_count = dict()
    for k,v in total.iteritems():
        z_count[k] = float(v)/float(sum_count)

    return z_count

def get_other_group(r_rate,z_count):

    n = len(r_rate)
    if n <= 6:
        return []
    rate_data = TopkHeap(n)
    for k,v in r_rate.iteritems():
        rate_data.Push((v,k))#排序

    data = rate_data.TopK()

    cuont_data = TopkHeap(n)
    for k,v in z_count.iteritems():
        count_data.Push((v,k))#排序

    c_data = count_data.TopK()
    
    data_list = []
    if n == 7:
        data_list.append(data[0][1])
    elif n == 8:
        data_list.append(data[0][1])
        data_list.append(c_data[n-1][1])
    elif n == 9:
        data_list.append(data[0][1])
        data_list.append(data[1][1])
        data_list.append(c_data[n-1][1])
    elif n == 10:
        data_list.append(data[0][1])
        data_list.append(data[1][1])
        data_list.append(c_data[n-1][1])
        data_list.append(c_data[n-2][1])
    else:
        return []

    return data_list

def eval_main(topic,count_title,total_text):#聚类评价主函数
    '''
    聚类评价主函数
    输入数据：话题名、每一类标题数、每一类的文本数
    每一类标题数格式：字典，如{'类别标号1':34,'类别标号2':24}
    每一类文本数格式：字典，如{'类别标号1':34,'类别标号2':24}

    输出数据：不做演化的类标签列表
    输出数据格式：序列，如[类别标号1,类别标号2,类别标号3]
    '''

    r_rate = write_rate(topic,count_title)#计算每一类的混杂度

    z_count = write_z_count(topic,total_text)#计算每一类的比例

    other_list = get_other_group(r_rate,z_count)#选取分类精度不高的类



