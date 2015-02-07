#-*-coding=utf-8-*-
"""将mongodb中的comment数据导出到jl文件，加上news_content字段
   usage: python etl.py comment_54916b0d955230e752f2a94e apec.jl
"""

import os
import sys
import json
from utils import _default_mongo
from load_settings import load_settings

settings = load_settings()
MONGOD_HOST = settings.get("MONGOD_HOST")
MONGOD_PORT = settings.get("MONGOD_PORT")
MONGO_DB_NAME = settings.get("MONGO_DB_NAME")

mongo = _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, \
        usedb=MONGO_DB_NAME)

collection_name = sys.argv[1]
results = mongo[collection_name].find()

def get_news_content(news_id):
    result = mongo['post_' + collection_name.split('_')[1]].find_one({"_id": news_id})
    if result:
        return None
    else:
        return result['content168']

jl_file = sys.argv[2]
fw = open(jl_file, 'w')
for r in results:
    r['news_content'] = get_news_content(r['news_id'])
    fw.write('%s\n' % json.dumps(r))
fw.close()

