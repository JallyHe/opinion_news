#-*-coding=utf-8-*-
# User: linhaobuaa
# Date: 2014-12-22 10:00:00
# Version: 0.1.0

from utils import _default_mongo
from config import MONGO_DB_NAME, SUB_EVENTS_FEATURE_COLLECTION

class Feature(object):
    """特征词类, 按子事件组织
    """
    def __init__(self, subeventid):
        """初始化特征词类
           input
               subeventid: 子事件ID
        """
        self.subeventid = subeventid
        self.mongo = _default_mongo(usedb=MONGO_DB_NAME)

    def set_newest(self, words, during):
        """计算子事件最新的特征词并存储
        """
        pass

    def get_newest(self):
        """获取子事件最新的特征词
        """
        results = self.mongo[SUB_EVENTS_KEYWORDS_COLLECTION].find({"eventid": self.id, "$not": {"_id": other_subevent_id}})

    def set_range(self, words, start_ts, end_ts):
        """计算子事件某时间范围的特征词并存储
        """
        pass

    def get_range(self):
        """获取子事件某时间范围的特征词
        """
        pass

