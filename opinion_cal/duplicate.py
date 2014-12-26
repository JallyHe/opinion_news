#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

import time
import pydablooms
import Levenshtein

class ShingLing(object):
    """shingle算法
    """
    def __init__(self, text1, text2, n=3):
        """input
               text1: 输入文本1, unicode编码
               text2: 输入文本2, unicode编码
               n: 切片长度
        """
        if not isinstance(text1, unicode):
            raise ValueError("text1 must be unicode")

        if not isinstance(text2, unicode):
            raise ValueError("text2 must be unicode")

        self.n = n
        self.threshold = 0.2
        self.text1 = text1
        self.text2 = text2
        self.set1 = set()
        self.set2 = set()
        self._split(self.text1, self.set1)
        self._split(self.text2, self.set2)
        self.jaccard = 0

    def _split(self, text, s):
        if len(self.text1) < self.n:
            self.n = 1

        for i in range(len(text) - self.n + 1):
            piece = text[i: i + self.n]
            s.add(piece)

    def cal_jaccard(self):

        intersection_count = len(self.set1 & self.set2)
        union_count = len(self.set1 | self.set2)

        self.jaccard = float(intersection_count) / float(union_count)
        return self.jaccard

    def check_duplicate(self):
        return True if self.jaccard > self.threshold else False

def max_same_rate(items, item):
    #计算item 和 items 的相似度
    reserve = True
    idx = 0
    rate_threshold = 0.8
    max_rate = 0
    for i in items:
        ratio = Levenshtein.ratio(i['text4duplicate'], item['text4duplicate'])
        if ratio >= rate_threshold:
            max_rate = ratio
            reserve = False
            break

        idx += 1

    return idx, max_rate, reserve

def max_same_rate_shingle(items, item):
    reserve = True
    idx = 0
    rate_threshold = 0.2
    max_rate = 0
    for i in items:
        sl = ShingLing(i['text4duplicate'], item['text4duplicate'], n=3)
        sl.cal_jaccard()
        if sl.jaccard >= rate_threshold:
            max_rate = sl.jaccard
            reserve = False
            break

        idx += 1

    return idx, max_rate, reserve


if __name__ == '__main__':
    text1 = u"中国中央电视台"
    text2 = u"中央电视台广播"
    s = ShingLing(text1, text2, 3)
    print s.cal_jaccard()
    print s.check_duplicate()
