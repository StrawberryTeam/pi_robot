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
    videoListFields = {
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
        data = Util.removeUnsafeFields(data, self.videoListFields.keys(), self.videoListFields)
        return self._db.insert_many(data)

    # 分集在剧集下是否存在
    def exists(self, name, setId):
        exists = self._db.find_one({
            "name": Util.conv2(name, self.videoListFields['name']), 
            'setId': Util.conv2(setId, self.videoListFields['setId'])
            })
        return True if exists else False

    # 获取一个影片内容
    def getVideo(self, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        item =  self._db.find_one({"_id": _id})
        setDict = self.getModel('VideoSet').getSetInfo(item['setId'])
        print(setDict)
        item['platform'] = setDict['platform']
        return item


    # 获取本设备未下载的影片 
    def getUnDlVideo(self, setId, uid):
        return self._db.find_one({"setId": Util.conv2(setId, self.videoListFields['setId']), "plays." + str(uid): {'$exists': False}})

    # 获取本设备已下载的影片数
    def getDledVideoListCount(self, setId, uid):
        listCount = self._db.find({"setId": Util.conv2(setId, self.videoListFields['setId']), "plays." + str(uid): {'$exists': True}}).count()
        return listCount

    # 新的可播放 单集 
    # data 本设备 播放地址
    def newPlay(self, _id, uid, data):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        # 更新已下载（可播放）数量
        return self._db.update_one({"_id": _id}, {"$set": {"plays." + str(uid): data}})
