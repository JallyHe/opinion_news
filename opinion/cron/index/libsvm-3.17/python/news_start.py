# -*- coding: utf-8 -*-

import os
import scws
import csv
from news_cut import *

def main(topic,flag,cluster):

    news, cluster_ids, big_news, big_lable = cut_word(flag,cluster)#进行新闻的分类与聚类

    count1,rate1,n1,title1 = keyword(topic,flag,news,cluster_ids[0],0)#对聚类的新闻提关键词对、代表性文本

    count2,rate2,n2,title2 = keyword(topic,flag,big_news,big_lable,1)#对分类的新闻提关键词对、代表性文本

    #write_rate(topic,count1,count2,flag)#计算每一类的混杂度

    write_z_count(topic,n1,n2,flag,title1,title2)#计算每一类的比例

if __name__ == '__main__':
    topic = '两会'
    main(topic,'lianghui',20)
