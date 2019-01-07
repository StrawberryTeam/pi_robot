#!/usr/bin/python3
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from Common.Db import Db
from Common.Util import Util

class Setting(Db):

    _db = {}
    def __init__(self):
        super().__init__()
        self._db = self.connect('setting')

    # 影片内容
    settingFields = {
        'name': 'string', # 设备名
        'uid': 'string', # 设备号唯一
        'host': 'string', # 设备地址
        'freeSpace': 'int', # 设备剩余空间 gb
        'lastRepoId': 'string', # warehouse 编号 01,02,03
        'lastRepoSize': 'int', # warehouse 已用空间 mb
    }

    # 设置设备剩余空间
    def setFreeSpace(self, uid, space):
        return self._db.update_one({"uid": str(uid)}, {"$set": {'freeSpace': Util.conv2(space, self.settingFields['freeSpace'])}})


    # 获取一个设备的信息
    def getSetting(self, uid):
        return self._db.find_one({'uid': str(uid)})