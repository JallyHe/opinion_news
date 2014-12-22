# -*- coding: utf-8 -*-
# User: linhaobuaa
# Date: 2014-12-21 22:00:00
# Version: 0.1.0


def subevent_classifier(text, labels, feature_words):
    """input
           text: 单条文本
           labels: 子事件标签，list
           feature_words: 各子事件的特征词，与上述标签对应，list
       output
           单条文本的类别标签
       example
           from trace import subevent_classifier

    """
    if len(labels) != len(feature_words):
        raise ValueError("labels and feature words list must have same length")

    if not isinstance(text, str):
        raise ValueError("text must be encode utf-8")

    label_score = dict()
    for idx, count_words_list in enumerate(feature_words):
        sum_count = reduce(lambda x, y: x[0] + y[0], count_words_list)
        weight_count = float(sum_count) * 0.05
        hit_count = sum([count for count, word in count_words if word in text])

        if hit_count > weight_count:
            label = labels[idx]
            label_score[label] = hit_count

    if label_score != {}:
        results = sorted(label_score.iteritems(), key=lambda(k, v): v, reverse=True)
        # 归为类得分最高的一类
        return results[0][1]
    else:
        # 归为其他类
        return 'other'


def text_classify(input_data, r_words):
    '''
    话题跟踪主函数
    输入数据：话题名、新闻数据、每一类的关键词
    输入数据格式：
    新闻数据：字典的序列，如：[{'_id':新闻id,'source_from_name':新闻来源,'title':新闻标题,'content':新闻内容,'timestamp':时间戳}]
    每一类的关键词：字典，如：{'类别标号1':[[32,'我们'],[43,'他们']....]}

    输出数据：有演化的类标签、演化的新闻、其他类新闻
    输出数据格式：
    有演化的类标签：序列，如['类别标号1','类别标号2','类别标号3'...]
    演化的新闻：字典，如{'mid':[新闻来源，标题，内容，时间戳，类标签]}
    其他类新闻：字典，如{'mid':[新闻来源，标题，内容，时间戳，类标签]}
    '''

    data_lable = dict()
    data_other = dict()
    ex_lable = []
    for item in input_data:
        p_time = item['timestamp']
        mid = item['_id']
        place = item['source_from_name']
        t = item['title']
        c = item['content']
        text = t + '__' + c
        l = find_cluster(text,r_words)
        if l not in ex_lable:
            ex_lable.append(l)
        if l == -1:
            data_other[str(mid)] = [place,str(t),str(c),p_time,l]
        else:
            data_lable[str(mid)] = [place,str(t),str(c),p_time,l]

    return ex_lable,data_lable,data_other


if __name__=="__main__":
    from Event import Event
    eventid = ""
    event = Event(eventid)
    subevents = event.getSubEvents()

    print subevents
