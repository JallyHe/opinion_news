# -*- coding: utf-8 -*-

import os
import time
import math
import uuid
import csv
import re
import heapq
import numpy as np
from gensim import corpora
from collections import Counter
from utils import cut_words, cut_words_noun, _default_mongo

AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), './')

def freq_word_comment(items):
    '''
    统计一条评论中的名词
    输入数据：
        items:新闻组成的列表:字典, 数据示例：[{'item的下标':评论id,'news_id':新闻id,'content':新闻内容}]
    输出数据：
        top_word:词和词频构成的列表，{词：词频率}
        word_comment:每条评论的名词，{"_id":[名词1，名词2，...]}
    '''
    words_list = []
    word_comment = {}#记录每条评论的名词
    for item in items:
        text = item['content']
        words = cut_words_noun(text)
        word_item = []
        for w in words:
            words_list.append(w)
            word_item.append(w)
        word_comment[items.index(item)]=word_item

    counter = Counter(words_list)
    total = sum(counter.values())#总词频数
    topk_words = counter.most_common()
    top_word = {k:float(v)/float(total) for k,v in topk_words}

    return top_word,word_comment

def freq_word_news(item):
    '''
    统计新闻的名词
    输入数据:新闻，字符串
    输出数据:新闻的词及词频率字典，{词：词频率}
    '''
    words_list = []
    words = cut_words_noun(item)
    word_item = []
    for w in words:
        words_list.append(w)

    counter = Counter(words_list)
    total = sum(counter.values())#总词频数
    topk_words = counter.most_common()
    top_word = {k:float(v)/float(total) for k,v in topk_words}

    return top_word

def word_list(comment_word,news_word):
    '''
    统计在评论和新闻中出现频率都高的词
    输入数据:
        comment_word:评论中的词及词频，字典格式
        news_word:新闻中的词及词频，字典格式
    输出数据:
        评论和新闻中出现频率排在前20%的词，[(词，词频)]
    '''
    word_all = {}
    for k,v in comment_word.iteritems():
        if news_word.has_key(k):
            word_all[k] = comment_word[k]+news_word[k]
        else:
            word_all[k] = comment_word[k]

    for k,v in news_word.iteritems():
        if word_all.has_key(k)==False:
            word_all[k] = news_word[k]

    sorted_word = sorted(word_all.iteritems(),key=lambda(k,v):v,reverse=True)
    result_word = [(k,v)for k,v in sorted_word]

    return result_word[:int(len(result_word)*0.2)]

def comment_word_in_news(word_comment,word_news,inputs):
    '''
    判断一条评论中的名词是否在新闻中出现过
    输入数据：
        word_comment:每条评论的名词，{"过滤后评论的下标":[名词1，名词2，...]}
        word_news:相应新闻的词及词频列表，[(词，词频)]
        inputs:过滤后的评论文本的集合,[{'_id':评论id,'news_id':新闻id,'content':新闻内容}]
    输出数据：
        input_reserved:评论中的名词在新闻中出现过,[{'_id':评论id,'news_id':新闻id,'content':新闻内容}]
        input_filtered:评论中的名词在新闻中没出现过，[{'_id':评论id,'news_id':新闻id,'content':新闻内容}]
    '''
    input_reserved = []
    input_filtered = []
    news_word = [item[0] for item in word_news]
    for k,v in word_comment.iteritems():
        count = 0#每条评论中包含的新闻词数
        for w in v:
            if w in news_word:
                count += 1
        if count >=2:
            inputs[int(k)]["count"] = count
            input_reserved.append(inputs[int(k)])
        else:
            inputs[int(k)]["count"] = count
            input_filtered.append(inputs[int(k)])
            
    return input_reserved,input_filtered  


def filter_comment(inputs,news,topicid):
    """
    过滤评论函数：将评论中@及后面用户名、表情符号去掉，只保留名词、动词、形容词次数大于3的评论;如果评论中的名词在高频（新闻+评论）词中出现过则保留该条评论，否则删除掉
    输入数据:
        inputs:评论数据，示例：[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
        news:新闻数据，"新闻"
        topicid:新闻id
    输出数据:
        过滤后的评论数据
    """

    item_reserved = []
    at_pattern = r'@(.+?)\s'
    emotion_pattern = r'\[(\S+?)\]'
    market_words = [u'兼职',u'包邮',u'大酬宾',u'网页链接',u'请关注',u'求互粉']
    
    for input in inputs:
        item = {}
        item['_id'] = input['_id']
        item['news_id'] = input['news_id']
        text = re.sub(at_pattern, '',input['content']+' ')#在每个input后加一个空格，以去掉@在末尾的情况
        text = text.strip(' ')
        text = re.sub(emotion_pattern,'',text)
        words = cut_words(text)
        if len(words) >= 3 and len(words)<=20:
            flag = 1#标记评论词汇中是否含有营销词汇
            for word in words:
                if word in market_words:
                    flag = 0
            if flag == 1:
                item['content'] = text
                item_reserved.append(item)

    #如果评论中的名词出现在过新闻中，则保留该评论
    comment_top, comment_noun = freq_word_comment(item_reserved)#评论中的词及词频
    news_word = freq_word_news(news)#新闻中的词及词频
    imp_word = word_list(comment_top,news_word)#评论和新闻中的词及词频结合
    reserved,filtered = comment_word_in_news(comment_noun,imp_word,item_reserved)

    return reserved

def comment_news(inputs):
    '''
    将新闻评论按新闻id归类
    输入数据：评论数组组成的列表，示例：[{"_id":评论编号，"news_id":新闻编号，"content":评论内容}]
    输出数据：按新闻id归类的新闻评论，示例：{新闻编号：[{"_id":评论编号，"news_id":新闻编号，"content":评论内容}]}
    '''
    comment_inputs={}
    for input in inputs:
        news_id = input["news_id"].encode("utf-8")
        if comment_inputs.has_key(news_id):
            item = comment_inputs[news_id]
            item.append(input)
        else:
            item = []
            item.append(input)
            comment_inputs[news_id] = item

    return comment_inputs

def freq_word(items):
    '''
    统计一条文本的词频
    输入数据：
        items: 新闻组成的列表:字典, 数据示例：{'_id':评论id,'news_id':新闻id,'content':新闻内容}
    输出数据：
        top_word: 词和词频构成的字典, 数据示例：{词：词频，词：词频，...}
    '''
    words_list = []
    text = items['content']
    words = cut_words_noun(text)
    for w in words:
        words_list.append(w)

    counter = Counter(words_list)
    total = sum(counter.values())#总词频数
    topk_words = counter.most_common()
    top_word = {k:(float(v)/float(total)) for k,v in topk_words}

    return top_word

def tfidf_v2(inputs):
    '''
    计算每条文本中每个词的tfidf，对每个词在各个文本中tfidf加和除以出现的文本次数作为该词的权值。
    输入数据：
        评论数据，示例：[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
    输出数据：
        result_tfidf[:topk]:前20%tfidf词及tfidf值的列表,示例：[(词,tfidf)]
        input_word_dict:每一条记录的词及tfidf,示例：{"_id":{词：tfidf,词：tfidf,...}}
    '''
    total_document_count = len(inputs)
    tfidf_dict = {}#词在各个文本中的tfidf之和
    count_dict = {}#词出现的文本数
    count = 0#记录每类下词频总数
    input_word_dict = {}#每条记录每个词的tfidf,{"_id":{词：tfidf，词：tfidf}}
    for input in inputs:
        word_count = freq_word(input)
        count += sum(word_count.values())
        word_tfidf_row = {}#每一行中词的tfidf
        for k,v in word_count.iteritems():
            tf = v
            document_count = sum([1 for input_item in inputs if k in input_item['content']])
            idf = math.log(float(total_document_count)/(float(document_count+1)))
            tfidf = tf*idf
            word_tfidf_row[k] = tfidf
            try:
                tfidf_dict[k] += tfidf
            except KeyError:
                tfidf_dict[k] = 1
        input_word_dict[input["_id"]] = word_tfidf_row

    for k,v in tfidf_dict.iteritems():
        tfidf_dict[k] =  float(tfidf_dict[k])/float(len(inputs))

    sorted_tfidf = sorted(tfidf_dict.iteritems(), key = lambda asd:asd[1],reverse = True)
    result_tfidf = [(k,v)for k,v in sorted_tfidf]

    topk = int(math.ceil(float(len(result_tfidf))*0.2))#取前20%的tfidf词
    return result_tfidf[:topk],input_word_dict

def process_for_cluto(word,inputs):
    '''
    处理成cluto的输入格式，词-文本聚类
    输入数据：
        word:特征词,[(词，tfidf)]
        input_dict:每条文本中包含的词及tfidf,{"_id":{词:tfidf,词：tfidf}}
        inputs:过滤后的评论数据
    输出数据：
        cluto输入文件的位置
    '''

    #生成cluto输入文件
    row = len(word)#词数
    column = len(inputs)#特征列数
    nonzero_count = 0#非0特征数

    cluto_input_folder = os.path.join(AB_PATH, "cluto")
    if not os.path.exists(cluto_input_folder):
        os.makedirs(cluto_input_folder)
    file_name = os.path.join(cluto_input_folder, '%s.txt' % os.getpid())

    with open(file_name, 'w') as fw:
        lines = []    
        #词频聚类
        for w in word:
            row_record = []#记录每行特征
            for i in range(len(inputs)):
                n = str(inputs[i]['content']).count(str(w[0]))
                if n!= 0:
                    nonzero_count += 1
                    row_record.append('%s %s'%(str(i+1),n))
            line = ' '.join(row_record) + '\r\n'
            lines.append(line)
        fw.write('%s %s %s\r\n'%(row, column, nonzero_count))
        fw.writelines(lines)
                    
    return file_name

def cluto_kmeans_vcluster(k=10, input_file=None, vcluster=None):
    '''
    cluto kmeans聚类
    输入数据：
        k: 聚簇数
        input_file: cluto输入文件路径，如果不指定，以cluto_input_folder + pid.txt方式命名
        vcluster: cluto vcluster可执行文件路径

    输出数据：
        cluto聚类结果, list
        聚类结果评价文件位置及名称
    '''
    # 聚类结果文件, result_file

    cluto_input_folder = os.path.join(AB_PATH, "cluto")

    if not input_file:
        input_file = os.path.join(cluto_input_folder, '%s.txt' % os.getpid())
        result_file = os.path.join(cluto_input_folder, '%s.txt.clustering.%s' % (os.getpid(), k))
        evaluation_file = os.path.join(cluto_input_folder,'%s_%s.txt'%(os.getpid(),k))
    else:
        result_file = os.path.join(cluto_input_folder,'%s.clustering.%s' % (input_file, k))
        evaluation_file = os.path.join(cluto_input_folder,'%s_%s.txt'%(os.getpid(),k))

    if not vcluster:
        vcluster = os.path.join(AB_PATH, './cluto-2.1.2/Linux_i686/vcluster')

    command = "%s -niter=20 %s %s > %s" % (vcluster, input_file, k, evaluation_file)
    os.popen(command)

    results = [line.strip() for line in open(result_file)]

    if os.path.isfile(result_file):
        os.remove(result_file)

    if os.path.isfile(input_file):
        os.remove(input_file)


    return results,evaluation_file

def label2uniqueid(labels):
    '''
        为聚类结果不为其他类的生成唯一的类标号
        input：
            labels: 一批类标号，可重复
        output：
            label2id: 各类标号到全局唯一ID的映射
    '''
    label2id = dict()
    for label in set(labels):
        label2id[label] = str(uuid.uuid4())

    return label2id
def kmeans(word, inputs, k):
    '''
    kmeans聚类函数
    输入数据：
        word:前20%tfidf词及tfidf值的列表,示例：[(词,tfidf)]
        input_dict:每条文本中包含的词及tfidf,{"_id":{词:tfidf,词：tfidf}}
        inputs:[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
        k:聚类个数
    输出数据：
        每类词构成的字典，{类标签：[词1，词2，...]}
        聚类效果评价文件路径
    '''
    if len(inputs) < 2:
        raise ValueError("length of input items must be larger than 2")
    
    input_file = process_for_cluto(word, inputs)
    label,evaluation_file = cluto_kmeans_vcluster(k=k, input_file = input_file)
    label2id = label2uniqueid(label)

    #将词对归类，{类标签：[词1，词2，...]}
    word_label = {}
    for i in range(len(word)):
        l = label2id[label[i]]
        if word_label.has_key(l):
            item = word_label[l]
            item.append(word[i][0])
        else:
            item = []
            item.append(word[i][0])
            word_label[l] = item

    return word_label,evaluation_file


def choose_cluster(tfidf_word,inputs,cluster_min,cluster_max):
    '''
    选取聚类个数2~15个中聚类效果最好的保留
    输入数据：
        tfidf_word:tfidf topk词及权值，[(词，权值)]
        inputs:过滤后的评论
        cluster_min:尝试的最小聚类个数
        cluster_max:尝试的最大聚类个数
    输出数据：
        聚类效果最好的聚类个数下的词聚类结果
    '''
    from comment_clustering_tfidf_v4 import kmeans

    evaluation_result = {}#每类的聚类评价效果
    cluster_result={}#记录每个聚类个数下，kmeans词聚类结果，{聚类个数：{类标签：[词1，词2，...]}}
    for i in range(cluster_min,cluster_max,1):
        results,evaluation = kmeans(tfidf_word,inputs,i)
        cluster_result[i]=results
        #提取每类聚类效果
        f = open(evaluation)
        s = f.read()
        pattern = re.compile(r'\[I2=(\S+?)\]')
        res = pattern.search(s).groups()
        evaluation_result[i]=res[0]
    sorted_evaluation = sorted(evaluation_result.iteritems(),key = lambda(k,v):k,reverse=False)

    #计算各个点的斜率
    slope = {}#每点斜率
    slope_average = 0#斜率的平均值
    for i in range(cluster_min,len(sorted_evaluation)):
        slope[i]=(float(sorted_evaluation[i][1])-float(sorted_evaluation[i-1][1]))/float(sorted_evaluation[i][1])
        slope_average += slope[i]
    slope_average = slope_average/float(len(sorted_evaluation)-1)

    #计算各个点与斜率均值的差值，找到差值最小点
    slope_difference = {}#斜率与均值的差值
    for k,v in slope.iteritems():
        slope_difference[k] = abs(float(slope[k])-slope_average)
    sorted_slope_difference = sorted(slope_difference.iteritems(),key=lambda(k,v):v, reverse=False)

    return cluster_result[sorted_slope_difference[0][0]]

def text_classify(inputs,word_label,tfidf_word):
    '''
    对每条评论分别计算属于每个类的权重，将其归入权重最大的类
    输入数据：
        inputs:评论字典的列表，[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
        word_cluster:词聚类结果,{'类标签'：[词1，词2，...]}
        tfidf_word:tfidf topk词及权值，[(词，权值)]

    输出数据：
        每条文本的归类，字典，{'_id':[类，属于该类的权重]}
    '''
    #将词及权值整理为字典格式
    word_weight = {}
    for idx,w in enumerate(tfidf_word):
        word_weight[w[0]] = w[1]

    #计算每条评论属于各个类的权值
    for input in inputs:
        text_weight = {}
        text = input['content']
        text_word = cut_words_noun(text)#每句话分词结果，用于text_weight中

        for l,w_list in word_label.iteritems():
            weight = 0
            for w in w_list:
                weight += text.count(w)*word_weight[w]
            text_weight[l] = float(weight)/(float(len(text_word)) + 1.0)
        sorted_weight = sorted(text_weight.iteritems(), key = lambda asd:asd[1], reverse = True)
        if sorted_weight[0][1]!=0:#只有一条文本属于任何一个类的权值都不为0时才归类
            clusterid, weight = sorted_weight[0]
        else:
            clusterid = 'other'
            weight = 0

        input['label'] = clusterid
        input['weight'] = weight

    return inputs

def cluster_evaluation(items, min_size=5):
    '''
    只保留文本数大于num的类
    输入数据:
        items: 新闻数据, 字典的序列, 输入数据示例：[{'news_id': 新闻编号, 'content': 评论内容, 'label': 类别标签}]
        num:类文本最小值
    输出数据:
        各簇的文本, dict
    '''
    # 将文本按照其类标签进行归类
    items_dict = {}
    for item in items:
        try:
            items_dict[item['label']].append(item)
        except:
            items_dict[item['label']] = [item]

    other_items = []
    for label in items_dict.keys():
        items = items_dict[label]
        if len(items) < min_size:
            for item in items:
                item['label'] = 'other'
                other_items.append(item)

            items_dict.pop(label)

    try:
        items_dict['other'].extend(other_items)
    except KeyError:
        items_dict['other'] = other_items

    return items_dict

