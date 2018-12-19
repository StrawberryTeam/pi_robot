#!/usr/bin/python3
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from Common.Db import Db
from Common.Util import Util

class VideoList(Db):

    _db = {}
    def __init__(self):
        super().__init__()
        self._db = self.connect('video_list')

    # 影片内容
    _videoListFields = {
        'setId': 'objectid', #ideo_set 剧集 _id,
        'name': 'string', #影片名称 
        'summary': 'string', #影片介绍
        'link': 'string', #影片播放地址
        'img': 'string', #影片封面图
        'created_at': 'int', #影片发布时间
        'duration': 'string', #'影片时间 例 01:10 没有不写该字段'
        'name_sp': 'string', #影片名首拼
        'name_py': 'string', #影片名全拼
        'name_pyshow': 'list',#影片名数组
        'plays': 'dict', #每个设备该影片的播放地址
        'imgs': 'dict', #每个设备该影片的封面图
        'non_py': 'bool', #True 不对该内容产生拼音
    }


    # 各影片分片
    def newList(self, data):
        if not isinstance(data, list):
            Util.error('Data must be a list')
            return False

        requireFields = ['setId', 'name', 'summary', 'link', 'img']
        # assert common.checkRequire(data, requireFields)
        requireCheckRe = Util.checkRequire(data, requireFields)
        if True != requireCheckRe:
            Util.error('{} Require field {} not found'.format('saveVideoList', requireCheckRe))
            return False
        data = Util.removeUnsafeFields(data, self._videoListFields.keys(), self._videoListFields)
        return self._db.insert_many(data)

    # 分集在剧集下是否存在
    def exists(self, name, setId):
        exists = self._db.find_one({
            "name": Util.conv2(name, self._videoListFields['name']), 
            'setId': Util.conv2(setId, self._videoListFields['setId'])
            })
        return True if exists else False


