# -*- coding: utf-8 -*-
# User: linhaobuaa
# Date: 2014-12-26 22:00:00
# Version: 0.2.0


def subevent_classifier(text, labels, feature_words):
    """input
           text: 单条文本, utf-8编码
           labels: 子事件标签，list
           feature_words: 各子事件的特征词，与上述标签对应，list, [{"word1": count1, "word2": count2}, {"word1": count1, "word2": count2}]
           其中词以utf-8编码
       output
           单条文本的类别标签
    """
    if len(labels) != len(feature_words):
        raise ValueError("labels and feature words list must have same length")

    if not isinstance(text, str):
        raise ValueError("text must be encode utf-8")

    label_score = dict()
    for idx, count_words in enumerate(feature_words):
        sum_count =  sum([count for word, count in count_words.iteritems()])
        weight_count = float(sum_count) * 0.05
        hit_count = sum([count for word, count in count_words.iteritems() if word in text])

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

