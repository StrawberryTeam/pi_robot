#!/usr/bin/python3
import pymongo
from pymongo import MongoClient
from bson.objectid import ObjectId
from Common.Db import Db
from Common.Util import Util

class VideoSet(Db):

    _db = {}
    def __init__(self):
        super().__init__()
        self._db = self.connect('video_set')


    # 影片集
    videoSetFields = {
        'title': 'string', #剧集名
        'summary': 'string', #剧集内容介绍
        'link': 'string', #内容页地址
        'img': 'string', #剧集封面图 url
        'img_large': 'string', #剧集封面图 url
        'hot': 'int', #热门指数
        'score': 'string', #网站自评
        'episode_over': 'int', #int 1 已完结 0 未完结 2 单次导入
        'area': 'string', #影片地区
        'lang': 'string', #影片语言
        'is_vip': 'int', # 1 需要 vip 账号才能观看 0 无账号可观看,
        'allplaynum': 'int', # 总播放量
        'allplaynum_txt': 'string', # 总播放量文本化
        'now_episode': 'string', # 当前更新集数文本化 例 138集
        'episode': 'int', # 'int 已找到的总集数 保存完所有影片分片后，通过 modifyEpisode(data, _id) 方法更新总分片数为总集数'
        'platform': 'int', # 平台 id
        'category': 'list', #影片分类
        'dl': 'list', #在下载该影片的设备
        'dled': 'list', #已完成下载的设备
        'play_num': 'dict', # 每个设备可供播放数量
        'title_py': 'string', #标题全拼
        'title_pyshow': 'list', #标题全拼 数组
        'title_sp': 'string', #标题首拼
        'imgs': 'dict', #已完成封面图片下载的设备
        'non_py': 'bool', #True 不对该内容产生拼音
        'created_uid': 'string', #自定义影片集创建设备 uid
    }

    
    # 影片集合
    def newSet(self, data, platform):
        if not isinstance(data, dict):
            Util.error('Data must be a dict')
            return False

        requireFields = ['title', 'link', 'summary', 'link', 'img', 'episode_over', 'is_vip', 'area', 'lang']
        # assert common.checkRequire(data, requireFields)
        requireCheckRe = Util.checkRequire(data, requireFields)
        if True != requireCheckRe:
            Util.error('{} Require field {} not found'.format('saveVideoSet', requireCheckRe))
            return False
        data = Util.removeUnsafeFields(data, self.videoSetFields.keys(), self.videoSetFields)
        # 哪个平台的
        data['platform'] = int(platform)
        setId = self._db.insert(data)
        return setId

    # 影片集是否已存在
    def exists(self, title, platform):
        exists = self._db.find_one({
            "title": Util.conv2(title, self.videoSetFields['title']), 
            'platform': Util.conv2(platform, self.videoSetFields['platform'])
            })
        return True if exists else False

    # 更新总集数
    def modifyEpisode(self, data, _id):
        if not data['episode']:
            return False
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        modify = self._db.update_one({"_id": _id}, {"$set": {"episode": Util.conv2(data['episode'], self.videoSetFields['episode'])}})
        return True if modify else False

    #删除影片集
    def remove(self, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        return self._db.delete_one({"_id": _id})


    # 查询可下载的集
    def getUnDlRes(self, uid, platform):
        # setMap = {}
        # 需要根据平台来查询 
        # 取一个 本设备下载量小于已更新集数的 剧集
        # pipe = [{
        #     '$project': {
        #         'cmp': {'$cmp': ['$play_num.' + str(uid), '$episode']},
        #         'platform': 1}
        #     }, {'$match': {'cmp': {'$lt': 0}, 'platform': int(platform)}}, {'$limit': 1}]
        # setList = _collection.aggregate(pipeline=pipe)
        # setList = list(setList)[0]
        # 现在在后台添加 下载中 状态 dl [uid,uid2,uid3] 查看该平台需要下载的即可
        setDict = self._db.find_one({"dl": str(uid), "platform": int(platform)})
        if not setDict:
            return False

        # 找一个未下载的单集
        listItem = self.getModel('VideoList').getUnDlVideo(setDict['_id'], uid)
        if not listItem:
            # 修正 play_num
            listCount = self.getModel('VideoList').getDledVideoListCount(setDict['_id'], uid)
            # 影片集还在下载中 但没有单集 更新影片集信息 认为已经下载完成 @2018.3.3
            self.setVSetDled(setDict['_id'], uid, listCount)
            print("未找到影片集未下载影片内容, 已修正影片集为下载完成 {}".format(setDict))
            return False

        listItem['platform'] = setDict['platform']
        return listItem


    # 设置为下载完成
    def setVSetDled(self, setId, uid, play_num = False):
        uid = str(uid)
        upMap = {"_id": ObjectId(setId)} 
        # 已全部下载完成
        # 移出下载中
        self._db.update(upMap, {"$pull": {"dl": uid}})
        # 添加已完成
        self._db.update(upMap, {"$push": {"dled": uid}})
            
        # 需要重新更新 play_num
        if play_num != False:
            self._db.update_one(upMap, {"$set": {"play_num." + uid : int(play_num)}})
        return True

    # 总剧集 可播放数  + 1
    def setCanPlayNum(self, setId, uid):
        upMap = {"_id": ObjectId(setId)} 
        self._db.update_one(upMap, {"$inc": {"play_num." + str(uid) : 1}})
        # 查看已下载数量 是否 大于等于 总数量 ，如果 是标记为 已下载完成
        item = self._db.find_one(upMap)
        if item['play_num'][uid] >= item['episode']: # 使用 video list num 替代 episode 值 
            self.setVSetDled(setId, uid)
        return True

    # 获取影片集信息
    def getSetInfo(self, setId):
        item = self._db.find_one({"_id": ObjectId(setId)})
        return item if item else False