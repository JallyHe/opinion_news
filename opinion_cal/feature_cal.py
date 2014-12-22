#-*-coding=utf-8-*-

from utils import _default_mongo
from xapian_case.utils import load_scws, cut
from config import MONGO_DB_NAME, EVENTS_NEWS_COLLECTION_PREFIX 

s = load_scws()
cx_dict = set(['Ag','a','an','Ng','n','nr','ns','nt','nz','Vg','v','vd','vn','@','j']) # 关键词词性词典

def load_black_words():
    #one_words = set([line.strip('\r\n') for line in file(EXTRA_BLACK_LIST_PATH)])
    one_words = set([])
    return one_words

black_words = load_black_words()


def cut_words(text):
    '''分词, 加入黑名单过滤单个词，保留名词、动词、形容词
       input
           texts: 输入text的list，utf-8
       output:
           terms: 关键词list
    '''
    if not isinstance(text, str):
        raise ValueError("cut words input text must be string")

    cx_terms = cut(s, text, cx=True)

    return [term for term, cx in cx_terms if cx in cx_dict and term not in black_words]


def tfidf_cal(keywords_dict_list, topk=100):
    '''计算tfidf
       input
           keywords_dict_list: 不同簇的关键词字典, list
       output
           不同簇的top tfidf词
    '''
    for keywords_dict in keywords_dict_list:
        tf_idf_dict = dict()

        for keyword, count in keywords_dict.iteritems():
            tf = float(count) / float(sum(keywords_dict.values()))
            document_count = sum([1 for kd in keywords_dict_list if keyword in kd.keys()])
            idf = log(float(len(keywords_dict.keys())) / float(document_count))
            tf_idf = tf * idf
            tf_idf_dict[keyword] = tf_idf

        tf_idf_results = sorted(tf_idf_dict.iteritems(), key=lambda(k, v): v, reverse=False)
        tf_idf_results = tf_idf_results[len(tf_idf_results)-topk:]
        tf_idf_results.reverse()

        return tf_idf_results


def extract_feature(items, title_term_weight=5, content_term_weight=1):
    '''
    提取特征词函数: Tf-idf, 名词/动词/形容词, TOP100, 标题与内容权重区分 5:1
    input：
        items: 新闻数据, 不考虑时间段, 字典的序列, 输入数据示例：[{'feature_title': 新闻标题, 'feature_content': 新闻内容, 'label': 类别标签}]
        title_term_weight: title中出现词的权重
        content_term_weight: content中出现词的权重
    output:
        每类特征词及权重, 数据格式：字典 {'我们': 32, '他们': 43}
    '''
    def extract_keyword(items):
        keywords_weight = dict()
        for item in items:
            title = item['feature_title']
            content = item['feature_content']

            title_terms = cut_words(title)
            content_terms = cut_words(content)

            for term in title_terms:
                try:
                    keywords_weight[term] += title_term_weight
                except KeyError:
                    keywords_weight[term] = title_term_weight

            for term in content_terms:
                try:
                    keywords_weight[term] += content_term_weight
                except KeyError:
                    keywords_weight[term] = content_term_weight

        # 筛掉频率大于或等于0.8, 频数小于或等于3的词
        keywords_count = dict()
        total_weight = sum(keywords_weight.values())
        for keyword, weight in keywords_weight.iteritems():
            ratio = float(weight) / float(total_weight)
            if ratio >= 0.8 or weight <= 3:
                continue

            keywords_count[keyword] = weight

        return keywords_count

    items_dict = {}
    for item in items:
        try:
            items_dict[item['label']].append(item)
        except:
            items_dict[item['label']] = [item]

    for label, one_items in items_dict.iteritems():
        keywords_count = extract_keyword(one_items)

    return 


if __name__ == '__main__':
    mongo = _default_mongo(usedb=MONGO_DB_NAME)
    topic = "APEC2014"
    topicid = "54916b0d955230e752f2a94e"
    results = mongo[EVENTS_NEWS_COLLECTION_PREFIX + topicid].find()
    for r in results:
        print r

    results = extract_feature(items, title_term_weight=5, content_term_weight=1)
    for k, v in results.iteritems():
        print k, v

