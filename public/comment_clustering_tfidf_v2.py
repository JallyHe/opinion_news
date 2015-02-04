# -*- coding: utf-8 -*-

import os
import uuid
import math
from collections import Counter
from gensim import corpora
from utils import cut_words, _default_mongo
from config import MONGO_DB_NAME, SUB_EVENTS_COLLECTION, \
        EVENTS_NEWS_COLLECTION_PREFIX, EVENTS_COLLECTION

AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), './')

def process_for_cluto(word, inputs, cluto_input_folder=None):
    """输入词对，评论字典组成的列表
       生成cluto输入文件
    """
    # handle default
    if not cluto_input_folder:
        cluto_input_folder = os.path.join(AB_PATH, "cluto")

    row = len(word) # 词对数
    column = len(inputs) # 特征列数
    nonzero_count = 0 # 非0特征数

    if not os.path.exists(cluto_input_folder):
        os.makedirs(cluto_input_folder)
    file_name = os.path.join(cluto_input_folder, '%s.txt' % os.getpid())

    with open(file_name, 'w') as fw:
        lines = []

        for w in word:
            row_record = [] # 记录每行特征
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
    input：
        k: 聚簇数
        input_file: cluto输入文件路径，如果不指定，以cluto_input_folder + pid.txt方式命名
        vcluster: cluto vcluster可执行文件路径

    output：
        cluto聚类结果, list
    '''
    # handle default
    # 聚类结果文件, result_file
    if not input_file:
        cluto_input_folder = os.path.join(AB_PATH, "cluto")
        input_file = os.path.join(cluto_input_folder, '%s.txt' % os.getpid())
        result_file = os.path.join(cluto_input_folder, '%s.txt.clustering.%s' % (os.getpid(), k))
    else:
        result_file = '%s.clustering.%s' % (input_file, k)

    if not vcluster:
        vcluster = os.path.join(AB_PATH, './cluto-2.1.2/Linux-i686/vcluster')

    command = "%s -niter=20 %s %s" % (vcluster, input_file, k)
    os.popen(command)

    results = [line.strip() for line in open(result_file)]

    if os.path.isfile(result_file):
        os.remove(result_file)

    if os.path.isfile(input_file):
        os.remove(input_file)

    return results


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


def kmeans(words, inputs, k=10):
    '''
    kmeans聚类函数
    输入数据：
    word:前20%tfidf词及tfidf值的列表,示例：[(词,tfidf)]
    inputs:[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
    k:聚类个数
    输出数据：
    每类词构成的字典，{类标签：[词1，词2，...]}
    '''
    if len(inputs) < 2:
        raise ValueError("length of input items must be larger than 2")

    input_file = process_for_cluto(words, inputs)
    labels = cluto_kmeans_vcluster(k=k, input_file=input_file)
    label2id = label2uniqueid(labels)

    # 将词对归类，{类标签：[词1，词2，...]}
    word_label = dict()
    for idx, word in enumerate(words):
        label = labels[idx]
        if int(label) != -1:
            label = label2id[label]
        else:
            # 将-1类归为其它
            label = 'other'

        try:
            word_label[label].append(word[0])
        except KeyError:
            word_label[label] = [word[0]]

    return word_label


def freq_word(items):
    '''
    统计一条文本的词频
    input：
        items:
            新闻组成的列表:字典, 数据示例：{'_id':评论id,'news_id':新闻id,'content':新闻内容}
    output：
        top_word: 词和词频构成的字典, 数据示例：{词：词频，词：词频，...}
    '''
    words_list = []
    text = items['content']
    words = cut_words(text)
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
    前20%tfidf词及tfidf值的列表,示例：[(词,tfidf)]
    '''
    total_document_count = len(inputs)
    tfidf_dict = {}#词在各个文本中的tfidf之和
    count_dict = {}#词出现的文本数
    count = 0#记录每类下词频总数
    for input in inputs:
        word_count = freq_word(input)
        count += sum(word_count.values())
        for k,v in word_count.iteritems():
            tf = v
            document_count = sum([1 for input in inputs if k in input['content']])
            idf = math.log(float(total_document_count)/(float(document_count+1)))
            tfidf = tf*idf
            try:
                tfidf_dict[k] += tfidf
            except KeyError:
                tfidf_dict[k] = 1

    for k,v in tfidf_dict.iteritems():
        tfidf_dict[k] =  float(tfidf_dict[k])/float(len(inputs))

    sorted_tfidf = sorted(tfidf_dict.iteritems(), key = lambda asd:asd[1],reverse = True)
    result_tfidf = [(k,v)for k,v in sorted_tfidf]

    topk = int(math.ceil(float(len(result_tfidf))*0.2))#取前20%的tfidf词
    return result_tfidf[:topk]


def text_classify(inputs,word_label,tfidf_word):
    '''
    对每条评论分别计算属于每个类的权重，将其归入权重最大的类
    输入数据：
    inputs:评论字典的列表，[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
    word_cluster:词聚类结果,{'类标签'：[词1，词2，...]}
    tfidf_word:tfidf topk词及权值，[(词，权值)]

    输出数据：每条文本的归类，字典，{'_id':[类，属于该类的权重]}
    '''
    #将词及权值整理为字典格式
    word_weight = dict()
    for w, c in tfidf_word:
        word_weight[w] = c

    #计算每条评论属于各个类的权值
    for input in inputs:
        cluster_weight = dict()
        text = input['content']
        for label, w_list in word_label.iteritems():
            cluster_weight[label] = sum([text.count(w) * word_weight[w] for w in w_list])

        sorted_weight = sorted(cluster_weight.iteritems(), key = lambda asd:asd[1], reverse = True)

        if sorted_weight[0][1] != 0:
            # 只有一条文本属于任何一个类的权值都不为0时才归类
            clusterid, weight = sorted_weight[0]
        else:
            clusterid = 'other'
            weight = 0

        input['label'] = clusterid
        input['weight'] = weight

    return inputs


def freq_word_evaluation_half(items, topk=10, topk_weight=5):
    '''
    选取权值排在topk_weight的评论
    input：
        items:
            新闻组成的列表:字典的序列, 数据示例：[{'_id':新闻id,'content':新闻内容,'lable':类别标签,'weight':每条评论属于该类的权值},...]

    output：
        权值排在前一半的评论，数据示例：[{'_id':新闻id,'content':新闻内容,'lable':类别标签,'weight':每条评论属于该类的权值},...]
    '''
    words_list = []
    #评论按照权值大小降序排列
    idx = 0
    weight_dict = {}
    for item in items:
        weight_dict[idx] = item['weight']

    sorted_weight = sorted(weight_dict.iteritems(),key = lambda asd:asd[1],reverse=True)
    result_weight = sorted_weight[:topk_weight]

    half_item = []
    for r in result_weight:
        half_item.append(items[int(r[0])])

    for item in half_item:
        text = item['content']
        words = cut_words(text)
        words_list.extend(words)

    counter = Counter(words_list)
    total_weight = sum(dict(counter.most_common()).values())
    topk_words = counter.most_common(topk)
    keywords_dict = {k: v for k, v in topk_words}

    return keywords_dict, total_weight

def freq_word_evaluation(items, topk=10):
    '''
    聚类评价用，统计一类文本的topk高频词
    input：
        items:
            新闻组成的列表:字典的序列, 数据示例：[{'_id':新闻id,'content':新闻内容,'lable':类别标签},...]
        topk:
            按照词频的前多少个词, 默认取10
    output：
        topk_words: 词、词频组成的列表, 数据示例：[(词，词频)，(词，词频)...]
    '''
    words_list = []
    for item in items:
        text = item['content']
        words = cut_words(text)
        words_list.extend(words)

    counter = Counter(words_list)
    total_weight = sum(dict(counter.most_common()).values())
    topk_words = counter.most_common(topk)
    keywords_dict = {k: v for k, v in topk_words}

    return keywords_dict, total_weight


def cluster_tfidf(keywords_count_list, total_weight_list, least_freq=10):
    '''计算tfidf
       input
           keywords_count_list: 不同簇的关键词, 词及词频字典的list
           least_freq: 计算tf-idf时，词在类中出现次数超过least_freq时，才被认为出现
       output
           不同簇的tfidf, list
    '''
    cluster_tf_idf = [] # 各类的tf-idf
    for idx, keywords_dict in enumerate(keywords_count_list):
        tf_idf_list = [] # 该类下词的tf-idf list
        total_freq = total_weight_list[idx] # 该类所有词的词频总和
        total_document_count = len(keywords_count_list) # 类别总数
        for keyword, count in keywords_dict.iteritems():
            tf = float(count) / float(total_freq) # 每个词的词频 / 该类所有词词频的总和
            document_count = sum([1 if keyword in kd.keys() and kd[keyword] > least_freq else 0 for kd in keywords_count_list])
            idf = math.log(float(total_document_count) / float(document_count + 1))
            tf_idf = tf * idf
            tf_idf_list.append(tf_idf)

        cluster_tf_idf.append(sum(tf_idf_list))

    return cluster_tf_idf


def global_text_weight(text, words):
    """计算一个事件下所有文本的权重，按照文本cover聚类词的去重进行计算
       text
       words
    """
    return sum([float(text.count(k)) * v for k, v in words])


def cluster_evaluation(items, top_num=5, topk_freq=10, least_freq=0, least_size=3, topk_weight=5):
    '''
    聚类评价，计算每一类的tf-idf: 计算每一类top词的tfidf，目前top词选取该类下前10个高频词，一个词在一个类中出现次数大于0算作在该类中出现
    input:
        items: 新闻数据, 字典的序列, 输入数据示例：[{'news_id': 新闻编号, 'content': 评论内容, 'label': 类别标签}]
        top_num: 保留top_num的tfidf类
        topk_freq: 选取的高频词的前多少，默认值10
        least_freq: 计算tf-idf时，词在类中出现次数超过least_freq时，才被认为出现，默认值为0
    output:
        各簇的文本, dict
    '''
    # 将文本按照其类标签进行归类
    items_dict = {}
    for item in items:
        try:
            items_dict[item['label']].append(item)
        except:
            items_dict[item['label']] = [item]

    # 对每类文本提取topk_freq高频词
    labels_list = []
    keywords_count_list = []
    total_weight_list = []
    for label, one_items in items_dict.iteritems():
        if label != 'other':
            labels_list.append(label)
            # keywords_count, weight = freq_word_evaluation(one_items, topk=topk_freq)
            # keywords_count_list.append(keywords_count)
            top_half, weight = freq_word_evaluation_half(one_items, topk=topk_freq, topk_weight=topk_weight)
            keywords_count_list.append(top_half)
            total_weight_list.append(weight)

    # 计算每类的tfidf
    tfidf_list = cluster_tfidf(keywords_count_list, total_weight_list, least_freq=least_freq)
    tfidf_dict = dict(zip(labels_list, tfidf_list))
    keywords_dict = dict(zip(labels_list, keywords_count_list))

    def choose_by_tfidf():
        """ 根据tfidf对簇进行选择
            input:
                top_num: 保留top_num的tfidf类
            output:
                更新后的items_dict
        """
        cluster_num = len(tfidf_list)

        sorted_tfidf = sorted(tfidf_dict.iteritems(), key=lambda(k, v): v, reverse=True)
        delete_labels = [l[0] for l in sorted_tfidf[-(len(sorted_tfidf)-top_num):]]

        other_items = []
        for label in items_dict.keys():
            if label != 'other':
                items = items_dict[label]
                if label in delete_labels:
                    for item in items:
                        item['label'] = 'other'
                        other_items.append(item)

                    items_dict.pop(label)

        try:
            items_dict['other'].extend(other_items)
        except KeyError:
            items_dict['other'] = other_items

    # 根据簇的tfidf评价选择
    choose_by_tfidf()

    def choose_by_size():
        """小于least_size的簇被归为其他簇
        """
        other_items = []
        for label in items_dict.keys():
            if label != 'other':
                items = items_dict[label]
                if len(items) < least_size:
                    for item in items:
                        item['label'] = 'other'
                        other_items.append(item)

                    items_dict.pop(label)

        try:
            items_dict['other'].extend(other_items)
        except KeyError:
            items_dict['other'] = other_items

    # 根据簇的大小进行评价选择
    choose_by_size()

    return items_dict

