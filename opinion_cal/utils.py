#-*-coding=utf-8-*-

import pymongo

MONGOD_HOST = '219.224.135.46'
MONGOD_PORT = 27019

def _default_mongo(host=MONGOD_HOST, port=MONGOD_PORT, usedb='boat'):
    # 强制写journal，并强制safe
    connection = pymongo.MongoClient(host=host, port=port, j=True, w=1)
    db = connection.admin
    # db.authenticate('root', 'root')
    db = getattr(connection, usedb)
    return db

