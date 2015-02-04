#-*-coding=utf-8-*-

from ad_filter import ad_filter
from rubbish_classifier import rubbish_classifier
from weibo_subob_classifier import subob_classifier
from classify_mid_weibo import mid_sentiment_classify
from triple_sentiment_classifier import triple_classifier
from neutral_classifier import triple_classifier as neutral_classifier
from weibo_subob_rub_neu_classifier import weibo_subob_rub_neu_classifier
from comment_clustering_tfidf_v7 import tfidf_v2, text_classify, \
        cluster_evaluation, choose_cluster


def comments_calculation(comments):
    # 无意义信息的clusterid，包括ad_filter分出来的广告，svm分出的垃圾，主客观分类器分出的新闻
    NON_CLUSTER_ID = 'nonsense'

    # 其他类的clusterid
    OTHER_CLUSTER_ID = 'other'

    # 最小聚类输入信息条数，少于则不聚类
    MIN_CLUSTERING_INPUT = 30

    # 最少簇数量
    MIN_CLUSTER_NUM = 2

    # 最多簇数量
    MAX_CLUSTER_NUM = 10

    # TFIDF词、聚类数量自动选择、vsm作属性也要可设成参数
    # 簇信息，主要是簇的特征词信息
    clusters_infos = {'features': dict()}

    # 单条信息list，每条信息存储 clusterid weight sentiment字段
    items_infos = []

    # 数据字段预处理
    inputs = []
    for r in comments:
        r['title'] = ''
        r['content168'] = r['content168'].encode('utf-8')
        r['content'] = r['content168']
        r['text'] = r['content168']

        # 简单规则过滤广告
        item = ad_filter(r)
        if item['ad_label'] == 0:
            inputs.append(item)
        else:
            item['clusterid'] = NON_CLUSTER_ID + '_rub'
            items_infos.append(item)

    # svm去除垃圾和规则筛选新闻文本
    items = weibo_subob_rub_neu_classifier(inputs)
    inputs = []
    for item in items:
        subob_rub_neu_label = item['subob_rub_neu_label']
        if not subob_rub_neu_label in [1, 0]:
            # 1表示垃圾文本，0表示新闻文本
            inputs.append(item)
        elif subob_rub_neu_label == 1:
            item['clusterid'] = NON_CLUSTER_ID + '_rub'
            items_infos.append(item)
        elif subob_rub_neu_label == 0:
            item['clusterid'] = NON_CLUSTER_ID + '_news'
            items_infos.append(item)

    if len(inputs) >= MIN_CLUSTERING_INPUT:
        tfidf_word, input_dict = tfidf_v2(inputs)
        results = choose_cluster(tfidf_word, inputs, MIN_CLUSTER_NUM, MAX_CLUSTER_NUM)

        #评论文本聚类
        cluster_text = text_classify(inputs, results, tfidf_word)

        evaluation_inputs = []

        for k,v in enumerate(cluster_text):
            inputs[k]['label'] = v['label']
            inputs[k]['weight'] = v['weight']
            evaluation_inputs.append(inputs[k])

        #簇评价, 权重及簇标签
        recommend_text = cluster_evaluation(evaluation_inputs)
        for label, items in recommend_text.iteritems():
            if label != OTHER_CLUSTER_ID:
                clusters_infos['features'][label] = results[label]

                for item in items:
                    item['label'] = label
                    item['weight'] = item['weight']
            else:
                item['label'] = OTHER_CLUSTER_ID
    else:
        # 如果信息条数小于,则直接归为其他类
        for r in inputs:
            r['label'] = OTHER_CLUSTER_ID

    # 情绪计算
    for r in inputs:
        if r['subob_rub_neu_label'] == 2:
            sentiment = 0 # 0 中性
        elif r['subob_rub_neu_label'] == -1:
            sentiment = triple_classifier(r) # 1 高兴、2 愤怒、3 悲伤、0无情感
            if sentiment == 0:
                sentiment = mid_sentiment_classify(r['text'])

            if sentiment == -1:
                sentiment = 0 # 中性

        r['sentiment'] = sentiment
        items_infos.append(r)

    return {'cluster_infos': clusters_infos, 'item_infos': items_infos}


def comments_calculation_v2(comments):
    # 无意义信息的clusterid，包括ad_filter分出来的广告，svm分出的垃圾，主客观分类器分出的新闻
    NON_CLUSTER_ID = 'nonsense'

    # 其他类的clusterid
    OTHER_CLUSTER_ID = 'other'

    # 最小聚类输入信息条数，少于则不聚类
    MIN_CLUSTERING_INPUT = 30

    # 最少簇数量
    MIN_CLUSTER_NUM = 2

    # 最多簇数量
    MAX_CLUSTER_NUM = 10

    # TFIDF词、聚类数量自动选择、vsm作属性也要可设成参数
    # 簇信息，主要是簇的特征词信息
    clusters_infos = {'features': dict()}

    # 单条信息list，每条信息存储 clusterid weight sentiment字段
    items_infos = []

    # 去除sentiment label clusterid ad_label subob_label rub_label
    clear_keys = ['sentiment', 'label', 'clusterid ad_label', 'subob_label', 'rub_label']
    inputs = []
    for r in comments:
        for key in clear_keys:
            if key in r:
                del r[key]

        inputs.append(r)
    comments = inputs

    # 数据字段预处理
    inputs = []
    for r in comments:
        r['title'] = ''
        r['content168'] = r['content168'].encode('utf-8')
        r['content'] = r['content168']
        r['text'] = r['content168']

        inputs.append(r)

    # 先分中性及3类分类器
    svm_inputs = []
    for r in inputs:
        sentiment = neutral_classifier(r)

        if sentiment != 0:
            sentiment = triple_classifier(r)
            if sentiment == 0:
                svm_inputs.append(r)
            else:
                r['clusterid'] = 'sentiment'
                r['sentiment'] = sentiment
                items_infos.append(r)
        else:
            svm_inputs.append(r)

    # 情绪调整
    senti_modify_inputs = []
    for r in svm_inputs:
        sentiment = mid_sentiment_classify(r['text'])
        if sentiment == -1:
            sentiment = 0 # 中性

        if sentiment != 0:
            r['clusterid'] = 'sentiment'
            r['sentiment'] = sentiment
            items_infos.append(r)
        else:
            r['sentiment'] = sentiment
            senti_modify_inputs.append(r)

    # 新闻分类
    inputs = []
    for r in senti_modify_inputs:
        r = subob_classifier(r)
        if r['subob_label'] == 1:
            # 主客观文本分类
            r['clusterid'] = NON_CLUSTER_ID + '_news' # 新闻
            items_infos.append(r)
        else:
            inputs.append(r)

    # 去垃圾
    items = rubbish_classifier(inputs)
    for item in items:
        if item['rub_label'] == 1:
            # svm去垃圾
            item['clusterid'] = NON_CLUSTER_ID + '_rub'
            if 'sentiment' in item:
                del item['sentiment']
        else:
            # 简单规则过滤广告
            item = ad_filter(item)
            if item['ad_label'] == 1:
                item['clusterid'] = NON_CLUSTER_ID + '_rub'
                if 'sentiment' in item:
                    del item['sentiment']

        items_infos.append(item)

    return {'cluster_infos': clusters_infos, 'item_infos': items_infos}

