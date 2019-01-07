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
        'freeSpace': 'string', # 设备剩余空间 gb
    }

    # 设置设备剩余空间
    def setFreeSpace(self, uid, space):
        return self._db.update_one({"uid": str(uid)}, {"$set": {'freeSpace': Util.conv2(space, self.settingFields['freeSpace'])}})




