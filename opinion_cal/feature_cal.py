#-*-coding=utf-8-*-

from xapian_case.utils import load_scws, cut

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
    if isinstance(text, str):
        raise ValueError("cut words input text must be string")

    cx_terms = cut(s, text, cx=True)

    return [term for cx, term in cx_terms if cx in cx_dict and term not in black_words]


def extract_feature(items, title_term_weight=5, content_term_weight=1):
    '''
    提取特征词函数: Tf-idf, 名词/动词/形容词, TOP100, 标题与内容权重区分 5:1
    input：
        items: 新闻数据, 不考虑时间段, 字典的序列, 输入数据示例：[{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳,'lable':类别标签}]
        title_term_weight: title中出现词的权重
        content_term_weight: content中出现词的权重
    output:
        关键词及权重, 数据格式：字典 {'我们': 32, '他们': 43}
    '''
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
    keywords_ratio = dict()
    total_weight = sum(keywords_weight.values())
    for keyword, weight in keywords_weight.iteritems():
        ratio = float(weight) / float(total_weight)
        if ratio >= 0.8 or weight <= 3:
            continue

        keywords_ratio[keyword] = ratio

    return keywords_ratio


if __name__ == '__main__':
    items = [{"feature_title": "TF-IDF的主要思想", "feature_content": "如果某个词或短语在一篇文章中出现的频率TF高，并且在其他文章中很少出现，则认为此词或者短语具有很好的类别区分能力，适合用来分类。TF-IDF实际上是：TF * IDF"}, {"feature_title": "平面设计作品", "feature_content": "网页设计欣赏 三维动画赏析 标志设计欣赏 插画设计作品 建筑设计欣赏 VI设计欣赏 UI设计欣赏 摄影艺术 设计理念"}]
    extract_feature(items, title_term_weight=5, content_term_weight=1)

