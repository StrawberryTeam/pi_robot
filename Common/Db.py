#!/usr/bin/python3
from Common.Straw import Straw
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
import os

class Db(Straw):
    # 任务
    _taskFields = {
        'videoIds': 'string', #待操作的 视频
        'setId': 'objectid', #待操作的视频集 id
        'fromDevice': 'string',
        'toDevice': 'string', #to device uid
        'type': 'string', #copy 复制 zip 打包 addset 添加影片集 addvideo 添加影片 transfer 
        'link': 'string',  #添加影片 / 影片集任务 链接
        'platform': 'int', #影片集 / 影片 对应的平台
        'created_at': 'int',
        'sort': 'int', #排序方法
        'status': 'int', #状态
        'transfer_status': 'int', #传送状态
        'file_md5': 'string', #传送文件的 md5 值
        'file_path': 'string', #传送文件的路径
    }

    # 已连接表
    _collection = {
        # 影片集
        'video_set': {},
        # 影片列表
        'video_list': {},
        # task
        'task': {},
        # setting
        'setting': {},
    }

    # 已连接 db
    _db = {}

    def __init__(self):
        pass

    # 连接表
    def connect(self, table):
        # 已连接过的表
        if self._collection[table]:
            return self._collection[table]

        config = self.getConfig('DB')
        client = MongoClient(config['mongoClient'])
        if not self._db:
            self._db = client[config['dbName']] # 连接库

        self._collection[table] = self._db[table] # 选择表
        return self._collection[table]



    # 获取所有 set 内容 拼音不存在的
    def getNonpySetList(self, count = 10):
        _collection = self.connect('video_set')
        dataList = _collection.find({"title_py": {"$exists": False}, 'non_py': {"$ne": True}}).sort("play_num", pymongo.DESCENDING).limit(count)
        return dataList if dataList.count() > 0 else False

    # 更新 set 拼音内容
    def saveSetPy(self, data, _id):
        _collection = self.connect('video_set')
        avaiableFileds = ['title_py', 'title_pyshow', 'title_sp', 'tags']
        saveData = common.removeUnsafeFields(data, avaiableFileds, self._videoSetFields)
        # saveData = dict(filter(lambda k: k[0] in avaiableFileds, data.items()))
        return _collection.update_one({"_id": _id}, {"$set": saveData})


    # 获取所有 video 内容
    def getNonpyVideoList(self, count = 10):
        _collection = self.connect('video_list')
        dataList = _collection.find({"name_py": {"$exists": False}, 'non_py': {"$ne": True}}).sort("plays", pymongo.DESCENDING).limit(count)
        return dataList if dataList.count() > 0 else False

    # 更新 video 拼音内容
    def saveVideoPy(self, data, _id):
        _collection = self.connect('video_list')
        avaiableFileds = ['name_py', 'name_pyshow', 'name_sp', 'tags']
        saveData = common.removeUnsafeFields(data, avaiableFileds, self._videoListFields)
        # saveData = dict(filter(lambda k: k[0] in avaiableFileds, data.items()))
        return _collection.update_one({"_id": _id}, {"$set": saveData})

    # 获取影片集信息
    def getSetInfo(self, setId):
        _collection = self.connect('video_set')
        item = _collection.find_one({"_id": ObjectId(setId)})
        return item if item else False

    # 获取本影片集所有影片内容
    def getVideoListBySetId(self, setId):
        _collection = self.connect('video_list')
        dataList = _collection.find({"setId": common.conv2(setId, self._videoListFields['setId'])}).sort("_id", pymongo.ASCENDING)
        return dataList if dataList.count() > 0 else False

    # 获取本影片集所有影片内容
    def getVideoListByDlImg(self, uid, setId):
        _collection = self.connect('video_list')
        dataList = _collection.find({"setId": common.conv2(setId, self._videoListFields['setId']), "img." + str(uid): {'$exists': False}}).sort("_id", pymongo.ASCENDING)
        return dataList if dataList.count() > 0 else False

    # 获取一个需要下载封面影片集
    def getVideoSetByDlImg(self, uid, platforms = [1]):
        '''
        platform 1 爱奇艺
        '''
        _collection = self.connect('video_set')
        dataList = _collection.find_one({"platform": {'$in': platforms}, "imgs." + str(uid): {'$exists': False}, "play_num." + str(uid): {'$exists': True}})
        return dataList if dataList else False

    # 更新影片集图片至本地图
    def modifySetImg(self, setId, data, uid):
        if not data['img']:
            return False
        _collection = self.connect('video_set')
        modify = _collection.update_one({"_id": setId}, {"$set": {"imgs." + str(uid): data['img']}})
        return True if modify else False

    # 更新影片内容图片
    def modifyVideoImg(self, _id, data, uid):
        if not data['img']:
            return False
        _collection = self.connect('video_list')
        modify = _collection.update_one({"_id": _id}, {"$set": {"imgs." + str(uid): data['img']}})
        return True if modify else False






    # # 修复用 start
    # def fixGetSet(_id):
    #     table = 'video_set'
    #     _collection = connect(table)
    #     return _collection.find_one({"_id": _id})

    # def fixGetVideo(_id):
    #     table = 'video_list'
    #     _collection = connect(table)
    #     return _collection.find_one({"_id": _id})

    #     # 更新影片集图片
    # def fixModifySetImg(setId, data):
    #     if not data['img']:
    #         return False
    #     table = 'video_set'
    #     _collection = connect(table)
    #     modify = _collection.update_one({"_id": setId}, {"$set": {"img": data['img']}})
    #     modify2 = _collection.update_one({"_id": setId}, {"$unset": {"img_status": ""}})
    #     return True if modify and modify2 else False

    # # 更新影片内容图片
    # def fixModifyVideoImg(_id, data):
    #     if not data['img']:
    #         return False
    #     table = 'video_list'
    #     _collection = connect(table)
    #     modify = _collection.update_one({"_id": _id}, {"$set": {"img": data['img']}})
    #     modify2 = _collection.update_one({"_id": _id}, {"$unset": {"img_status": ""}})
    #     return True if modify and modify2 else False


    # # 修复用 end

    _TASK_READY = 1 #未执行的
    _TASK_FAILD = 2 #已完成的未成功的
    _TASK_SUCCESS = 3 #明确成功的任务
    # 获取下一个需要执行的任务
    def getTask(self, taskTypes, deviceId):
        _collection = self.connect('task')
        deviceId = str(deviceId)
        taskInfo = _collection.find_one({"toDevice": deviceId, "type": {'$in':taskTypes}, 'status': self._TASK_READY})
        return taskInfo if taskInfo else False

    _TRANSFER_FAILD = -1 # 操作中断或失败 不重新尝试
    _TRANSFER_READY = 1 # 等待打包文件
    # _TRANSFER_PACK = 2 # 完成打包等待传送
    _TRANSFER_COMPLETE = 2 # 传送完成，等待接收
    _TRANSFER_SUCCESS = 3 # 任务完成，等待删除原始文件
    _TRANSFER_CLERA = 4 # 任务完成，原始文件清除完成

    # 下载影片集
    def set2Dl(self, setId, deviceId):
        # print("set {} to dl".format(setId))
        _collection = self.connect('video_set')
        modify = _collection.update_one({"_id": setId}, {"$push": {"dl": str(deviceId)}})
        return True if modify else False

    # 传送完成
    def taskTransferComplete(self, taskId, fileMd5, filePath):
        self.taskDoing(taskId)
        _collection = self.connect('task')
        saveData = dict()
        saveData['transfer_status'] = self._TRANSFER_COMPLETE
        saveData['file_md5'] = fileMd5
        saveData['file_path'] =  filePath
        saveData = common.removeUnsafeFields(saveData, self._taskFields.keys(), self._taskFields)
        modify = _collection.update_one({"_id": ObjectId(taskId)}, {"$set": saveData})
        return True if modify else False

    # 传送失败
    def taskTransferFaild(self, taskId):
        self.taskDoing(taskId)
        _collection = self.connect('task')
        modify = _collection.update_one({"_id": ObjectId(taskId)}, {"$set": {"transfer_status": self._TRANSFER_FAILD}})
        return True if modify else False

    # 默认任务为失败
    def taskDoing(self, _id):
        _collection = self.connect('task')
        modify = _collection.update_one({"_id": ObjectId(_id)}, {"$set": {"status": self._TASK_FAILD}})
        return True if modify else False

    # 任务成功
    def taskSuccess(self, _id):
        _collection = self.connect('task')
        modify = _collection.update_one({"_id": ObjectId(_id)}, {"$set": {"status": self._TASK_SUCCESS}})
        return True if modify else False

    # 查询已下载完成的集
    def getDledRes(self, uid):
        # 查 list
        _collection = self.connect('video_list')
        # 找一个未下载的单集
        listItem = _collection.find({"plays." + str(uid): {'$exists': True}})
        return listItem if listItem else False

    # 设置为下载中
    def setVSetOnDl(self, setId, uid):
        _collection = self.connect('video_set')
        uid = str(uid)
        upMap = {"_id": ObjectId(setId)} 
        # 已全部下载完成
        # 移出下载完成
        _collection.update(upMap, {"$pull": {"dled": uid}})
        # 添加已完成
        _collection.update(upMap, {"$addToSet": {"dl": uid}})
            
        # 需要重新更新 play_num -1
        _collection.update_one(upMap, {"$inc": {"play_num." + uid : -1}})
        return True

    # 移出已下载完成的影片
    def rmVideo(self, _id, uid):
        _collection = self.connect('video_list')
        _collection.update({"_id": _id}, {"$unset": {"plays." + str(uid): ""}})
        return True


if __name__ == "__main__":
    db()
