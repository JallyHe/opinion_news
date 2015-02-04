# -*- coding: utf-8 -*-

import os
import math
import uuid
import csv
import re
from gensim import corpora
from collections import Counter
from utils import cut_words, _default_mongo

AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), './')

def process_for_cluto(word, inputs, cluto_input_folder=None):
    '''
    处理成cluto的输入格式
    输入数据：
    word:特征词,[(词，tfidf)]
    inputs:过滤后的评论数据
    '''
    # handle default
    if not cluto_input_folder:
        cluto_input_folder = os.path.join(AB_PATH, "cluto")

    #生成cluto输入文件
    row = len(word)#词数
    column = len(inputs)#特征列数
    nonzero_count = 0#非0特征数

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
    input：
        k: 聚簇数
        input_file: cluto输入文件路径，如果不指定，以cluto_input_folder + pid.txt方式命名
        vcluster: cluto vcluster可执行文件路径

    output：
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
        result_file = os.path.join(cluto_input_folder, '%s.clustering.%s' % (input_file, k))
        evaluation_file = os.path.join(cluto_input_folder, '%s_%s.txt' % (os.getpid(), k))

    if not vcluster:
        vcluster = os.path.join(AB_PATH, './cluto-2.1.2/Linux-i686/vcluster')

    command = "%s -niter=20 %s %s > %s" % (vcluster, input_file, k, evaluation_file)
    os.popen(command)

    results = [line.strip() for line in open(result_file)]

    if os.path.isfile(result_file):
        os.remove(result_file)

    if os.path.isfile(input_file):
        os.remove(input_file)

    return results, evaluation_file

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

def kmeans(word, inputs, k=10):
    '''
    kmeans聚类函数
    输入数据：
    word:前20%tfidf词及tfidf值的列表,示例：[(词,tfidf)]
    inputs:[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
    k:聚类个数
    输出数据：
    每类词构成的字典，{类标签：[词1，词2，...]}
    聚类效果评价文件路径
    '''
    if len(inputs) < 2:
        raise ValueError("length of input items must be larger than 2")

    input_file = process_for_cluto(word, inputs)
    labels, evaluation_file = cluto_kmeans_vcluster(k=k, input_file=input_file)
    label2id = label2uniqueid(labels)

    #将词对归类，{类标签：[词1，词2，...]}
    word_label = {}
    for i in range(len(word)):
        l = labels[i]
        if int(l) != -1:
            l = label2id[l]
        else:
            l = 'other'

        if word_label.has_key(l):
            item = word_label[l]
            item.append(word[i][0])
        else:
            item = []
            item.append(word[i][0])
            word_label[l] = item

    return word_label, evaluation_file

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

def tfidf_v4(inputs):
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
    return result_tfidf[:topk], input_word_dict

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
    word_weight = {}
    for w, c in tfidf_word:
        word_weight[w] = c

    #计算每条评论属于各个类的权值
    for input in inputs:
        cluster_weight = dict()
        text = input['content']
        for label, w_list in word_label.iteritems():
            weight = 0
            for w in w_list:
                weight += text.count(w)*word_weight[w]
            cluster_weight[label] = float(weight)/float(len(w_list))

        sorted_weight = sorted(cluster_weight.iteritems(), key = lambda asd:asd[1], reverse = True)

        if sorted_weight[0][1]!=0:
            # 只有一条文本属于任何一个类的权值都不为0时才归类
            clusterid, weight = sorted_weight[0]
        else:
            clusterid = 'other'
            weight = 0

        input['label'] = clusterid
        input['weight'] = weight

    return inputs

def word_cooccur(word_label,inputs):
    '''
    找出与每类词共线的词的类别
    输入数据：
    word_label:{类标签：[词1，词2，...]}
    inputs:过滤后的评论数据：[{'_id':评论id,'news_id':新闻id,'content':评论内容}]
    输出数据：
    簇与簇间举例组成的字典，{簇标签：[距离0，距离1，...]}
    '''
    label_matrix = {}
    for k,v in word_label.iteritems():
        vector = [0]*len(inputs)
        for w in v:
            for input in inputs:
                if w in input['content']:
                    vector[inputs.index(input)] += 1
        label_matrix[k] = vector

    #计算两个类之间的距离
    dist_dict = {}
    for k,v in label_matrix.iteritems():
        v1 = label_matrix[k]
        dist_vector = [0]*len(word_label)
        for key,value in label_matrix.iteritems():
            v2 = label_matrix[key]
            product = 0
            dist_v1 = 0
            dist_v2 = 0
            for i in range(len(v1)):
                product += float(v1[i])*float(v2[i])
                dist_v1 += math.pow(float(v1[i]),2)
                dist_v2 += math.pow(float(v2[i]),2)
            dist = product/(math.sqrt(dist_v1)*math.sqrt(dist_v2))
            dist_vector[int(key)] = dist
        dist_dict[int(k)] = dist_vector

    return dist_dict

def cut_cluster_net(dist_dict):
    '''
    对词簇组成的网络划分
    输入数据：簇与簇间距离组成的字典,{簇标签：[距离0，距离1，...]}
    '''
    reserved_cluster = []
    near_cluster = {}#记录每个簇相近的簇的标签
    flag_cluster = {}#记录某个类是否保留
    for k,v in dist_dict.iteritems():
        near_label = []
        for i in range(len(v)):
            if v[i]>0.2:
                near_label.append(i)
        near_cluster[k] = near_label
        flag_cluster[k] = 1

    for k,v in near_cluster.iteritems():
        if flag_cluster[k] == 1:
            if len(near_cluster[k])==len(dist_dict):
                flag_cluster[k] == 0
            else:#当某一行权值全部>0.2时，一定不保留
                row1 = near_cluster[k]
                flag = 0
                for item in near_cluster[k]:
                    row2 = near_cluster[item]
                    distinct1=[]#记录row1不同于row2的编号
                    distinct2=[]#记录row2不同于row1的编号
                    if row1 == row2:#如果两行相同，flag加1
                        flag += 1
                    else:#如果两行不同，找到不相同的类标号
                        for i in range(len(row1)):
                            if row1[i] not in row2:
                                distinct1.append(row1[i])
                            else:
                                flag_cluster[row1[i]] = 0
                        for i in range(len(row2)):
                            if row2[i] not in row1:
                                distinct2.append(row2[i])
                            else:
                                flag_cluster[row2[i]] = 0

                if flag == len(near_cluster[k]):#如果某一行和标号相应行相同，则这些类作为一类保留
                    flag_cluster[k] = 0
                    reserved_cluster.append(near_cluster[k])
    for k,v in flag_cluster.iteritems():
        if flag_cluster[k] == 1:
            reserved_cluster.append(k)

    return reserved_cluster

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
    evaluation_result = {}#每类的聚类评价效果
    cluster_result={}#记录每个聚类个数下，kmeans词聚类结果，{聚类个数：{类标签：[词1，词2，...]}}
    for i in range(cluster_min,cluster_max,1):
        results,evaluation = kmeans(tfidf_word, inputs, i)
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

def cluster_evaluation(items, min_size=5):
    '''
    只保留文本数大于num的类
    input:
        items: 新闻数据, 字典的序列, 输入数据示例：[{'news_id': 新闻编号, 'content': 评论内容, 'label': 类别标签}]
        num:类文本最小值
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

