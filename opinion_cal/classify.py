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


if __name__=="__main__":
    from Event import Event
    eventid = ""
    event = Event(eventid)
    subevents = event.getSubEvents()

    print subevents
