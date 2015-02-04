#-*-coding=utf-8-*-

import os
import sys
import math

AB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../public/')
sys.path.append(os.path.join(AB_PATH, './liblinear-1.96/python/'))
from rubbish_filter import rubbish_filter

def rubbish_classifier(items, batch=1000):
    """垃圾过滤器，批处理模式
       batch: 1000
    """
    results = []

    items_length = len(items)
    iters = int(math.ceil(float(items_length) / float(batch)))

    for i in range(0, iters):
        batch_items = items[i * batch: (i + 1) * batch - 1]
        batch_results = rubbish_filter(batch_items)
        results.extend(batch_results)

    return results

