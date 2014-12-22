#-*-coding=utf-8-*-

import os

def split_other(lable_data,other_data):
'''
    判断其他类是否分裂主函数
    输入数据：演化的新闻、其他类新闻
    输入数据格式：
    演化的新闻：字典，如{'mid':[新闻来源，标题，内容，时间戳，类标签]}
    其他类新闻：字典，如{'mid':[新闻来源，标题，内容，时间戳，类标签]}

    输出数据：是否进行分裂
    输出数据格式：0或1,0表示不进行分裂，1表示进行分裂
'''

    lable_count = len(lable_data)
    other_count = len(other_data)
    total_count = lable_count + other_count

    if float(other_count)/float(total_count) >  0.5:
        return 1

    lable_list = []
    for k,v in lable_data.iteritems():
        if v[4] not in lable_list:
            lable_list.append(v[4])

    if len(lable_list) < 3:
        return 1
        
