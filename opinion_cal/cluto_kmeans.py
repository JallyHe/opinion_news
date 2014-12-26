# -*- coding: utf-8 -*-

import os
import time
import uuid
from gensim import corpora
from utils import cut_words, _default_mongo
from config import MONGO_DB_NAME, SUB_EVENTS_COLLECTION, \
        EVENTS_NEWS_COLLECTION_PREFIX, EVENTS_COLLECTION


def process_for_cluto(inputs, cluto_input_folder="cluto"):
    """
    数据预处理函数
    input：
        inputs: 新闻数据, 示例：[{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳}]
    output:
        cluto输入文件路径
    """
    feature_set = set() # 不重复的词集合
    words_list = [] # 所有新闻分词结果集合
    for input in inputs:
        text = input['title'] + input['content']
        words = cut_words(text)
        words_list.append(words)

    # 特征词字典
    dictionary = corpora.Dictionary(words_list)

    # 将feature中的词转换成列表
    feature_set = set(dictionary.keys())

    row_count = len(inputs) # documents count
    column_count = len(feature_set) # feature count
    nonzero_count = 0 # nonzero elements count

    # 文件名以PID命名
    if not os.path.exists(cluto_input_folder):
        os.makedirs(cluto_input_folder)
    file_name = os.path.join(cluto_input_folder, '%s.txt' % os.getpid())

    with open(file_name, 'w') as fw:
        lines = []

        for words in words_list:
            bow = dictionary.doc2bow(words)
            nonzero_count += len(bow)
            line = ' '.join(['%s %s' % (w + 1, c) for w, c in bow]) + '\n'
            lines.append(line)

        fw.write('%s %s %s\n' % (row_count, column_count, nonzero_count))
        fw.writelines(lines)

    return file_name


def cluto_kmeans_vcluster(k=10, input_file=None, vcluster='./cluto-2.1.2/Linux-i686/vcluster', \
        cluto_output_folder="cluto", cluto_input_folder="cluto"):
    '''
    cluto kmeans聚类
    input：
        k: 聚簇数，默认取10
        input_file: cluto输入文件路径，如果不指定，以cluto_input_folder + pid.txt方式命名
        vcluster: cluto vcluster可执行文件路径

    output：
        cluto聚类结果文件路径，文件内容为一列列标签，与输入新闻对应
    '''
    if not os.path.exists(cluto_output_folder):
        os.makedirs(cluto_output_folder)
    # 聚类效果输出文件
    output_file = os.path.join(cluto_output_folder, '%s_other.txt' % os.getpid())

    # 聚类结果文件, result_file
    if not input_file:
        input_file = os.path.join(cluto_input_folder, '%s.txt' % os.getpid())
        result_file = os.path.join(cluto_input_folder, '%s.txt.clustering.%s' % (os.getpid(), k))
    else:
        result_file = '%s.clustering.%s' % (input_file, k)

    command = "%s -niter=20 %s %s" % (vcluster, input_file, k)
    os.popen(command)

    return result_file


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
        label2id[label] = uuid.uuid4()

    return label2id

def clusteringfile2labels(filename):
    """
       读取聚类结果转化为数组
       input:
           聚类结果文件路径
       output:
           聚类结果数组
    """
    return [line.strip() for line in open(filename)]


def tf_idf_cluster(labeled_inputs, topk=20):
    '''
        计算各类高频词及top tfidf词
        input：
            labeled_inputs: 有类标签的新闻记录, 字典的序列, 数据示例: [{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳,'lable':类别标签}]
            topk: 每类下面选取的高频词词数, 默认为20
        output:
            所有类tfidf值, 字典, 数据示例：{'i':类1tfidf值}
    '''

    w_count = [] # 记录每类下词数
    freq_word_list = [] # 记录所有类的高频词，数组每个元素为一个类的字典

    cluster_items = dict() # 某类下全部的新闻[{新闻1记录（格式同之前）}，...]
    for item in labeled_inputs:
        label = item['label']
        try:
            cluster_items[label].append(item)
        except KeyError:
            cluster_items[label] == [item]

    for label, items in cluster_items.iteritems():
        wordlist, word_count = freq_word(items, label)
        freq_word_list.append(wordlist)
        w_count.append(word_count)

    tf_idf_dict = top_tfidf(freq_word_list,top)

    return tf_idf_dict


def freq_word(items, topk=20):
    '''
    统计一批文本的topk高频词
    input：
        items:
            新闻组成的列表:字典的序列, 数据示例：[{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳,'lable':类别标签},...]
        topk:
            按照词频的前多少个词, 默认取20
    output：
        词、词频组成的列表, 数据示例：[(词，词频)，(词，词频)...]
    '''
    from utils import cut_words
    from collections import Counter
    words_list = []
    for item in items:
        text = item['title'] + item['content']
        words = cut_words(text)
        words_list.extend(words)

    counter = Counter(words_list)
    topk_words = counter.most_common(topk)

    return topk_words


def top_tfidf(items, topk_freq=20):
    '''
    计算每一类top词的tfidf，目前top词选取该类下前20个高频词，一个词在一个类中出现次数大于10算作在该类中出现
    input:
        words_list: 由每类下词和词频组成的列表构成的列表、top词数目
    输入数据格式：列表组成的列表、数字
    输入数据示例：
    [[(词，词频)，(词，词频),...],[(词，词频)，(词，词频),...],...]即[[类别1下的词和词频],[类别2下的词和词频],...]

    输出参数：由每类tfidf构成的字典
    输出数据格式：字典
    输出数据示例：
    {'i'：第i类tfidf值}    
    '''

    #计算每一类下的总词频
    tf = []#记录每个类下的词频总数
    df = []
    w_list = []#每个类top词在每个类出现的次数
    for i in range(len(word)):#i:类
        total = 0
        for j in range(len(word[i])):
            total += word[i][j][1]
        tf.append(total)
        df_dict = {}
        w_occur = {}
        w_class = {}

        #for j in range(num[i]):#统计某个类下的某个词在多少个类里出现过；j:第几个top词
        for j in range(num):#top词20，出现次数成比例
            all_count_dict = {}#记录一个高频词在各个类中出现的次数
            for m in range(len(word)):#m：类
                count = 0
                all_count = 0#记录一个高频词分别在每个类中出现的次数
                for n in range(len(word[m])):#n:第m类下的第n个词
                    if word[i][j][0] in word[m][n][0]:
##                        count += 1
                        all_count += word[m][n][1]
                        if word[m][n][1]>10:
                            count += 1#一个词在一个类中出现次数大于10词算作出现
##                        if word[m][n][1]>10*(num[m]/20):#一个词出现在最小类的次数超过10算出现，其他类中出现次数大于(该类下次数/最小类词数)*10算出现
##                            count += 1
                if count !=0:
                    try:
                        df_dict[word[i][j][0]] += 1
                    except KeyError:
                        df_dict[word[i][j][0]] =1

                all_count_dict[m]=all_count#特征word[i][j][0]在第m个类中出现的次数
            w_occur[word[i][j][0]]=all_count_dict#word[i][j][0]在m个类中出现次数组成的字典

        df.append(df_dict)#每个类下排在前20的每个单词出现的类的个数，是字典组成的列表
        w_class[i]=w_occur#第i个类下各特征在各个类中出现的次数，[{{{类1第1个feature在第1个类中出现的次数},{类1第1个feature在第2个类中出现的次数},{类1第3个特征在第3个类中出现的次数},....},{},...}]
        w_list.append(w_class)

    tfidf = {}#记录所有类下前top_num个词的tfidf
    for i in range(len(word)):
        tfidf_dict = {}#存每个类下每个词的tfidf
        tfidf_class = 0#计算每个类下top词的tfidf加和
        #print len(df[i])
        for k,v in df[i].items():
            for j in range(len(word[i])):
                if k in word[i][j]:
                    freq_w = word[i][j][1]#一个词的词频
                    df_w = df[i][k]#一个词在多少个类中出现过
                    tf_w = float(freq_w)/tf[i]
                    idf_w = math.log(float(10)/float(df_w))
                    tfidf_w = tf_w*idf_w
                    tfidf_dict[k]=str(freq_w)+','+str(df_w)+','+str(tf_w)+','+str(idf_w)+','+str(tfidf_w)
                    tfidf_class += tfidf_w
        #tfidf_class = float(tfidf_class)/num[i]#平均每个高频词的tfidf
        tfidf[i] = tfidf_class
            
    return tfidf

if __name__=="__main__":
    mongo = _default_mongo(usedb=MONGO_DB_NAME)
    topic = "APEC2014"
    topicid = "54916b0d955230e752f2a94e"

    begin = time.time()
    results = mongo[EVENTS_NEWS_COLLECTION_PREFIX + topicid].find()

    search_ts = time.time()
    print 'search cost %s seconds' % (search_ts - begin)
    inputs = []
    for r in results:
        inputs.append({"title": r["title"].encode("utf-8"), "content": r["content168"].encode("utf-8")})

    print freq_word(inputs)
    """
    print 'read data cost %s seconds' % (time.time() - search_ts)
    process_for_cluto(inputs)

    # cluto聚类，生成文件，每行为一条记录的簇标签
    cluto_labels_file = cluto_kmeans_vcluster(input_file='./cluto/2698.txt')

    # 读取簇标签文件, 生成数组，并转化为全局唯一ID
    cluto_labels = clusteringfile2labels(cluto_labels_file)
    label2id = label2uniqueid(cluto_labels)
    for label in cluto_labels:
        print label2id[label]
    """

