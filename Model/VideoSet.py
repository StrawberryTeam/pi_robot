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
    _videoSetFields = {
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
        data = Util.removeUnsafeFields(data, self._videoSetFields.keys(), self._videoSetFields)
        # 哪个平台的
        data['platform'] = int(platform)
        setId = self._db.insert(data)
        return setId

    # 影片集是否已存在
    def exists(self, title, platform):
        exists = self._db.find_one({
            "title": Util.conv2(title, self._videoSetFields['title']), 
            'platform': Util.conv2(platform, self._videoSetFields['platform'])
            })
        return True if exists else False

    # 更新总集数
    def modifyEpisode(self, data, _id):
        if not data['episode']:
            return False
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        modify = self._db.update_one({"_id": _id}, {"$set": {"episode": Util.conv2(data['episode'], self._videoSetFields['episode'])}})
        return True if modify else False

    #删除影片集
    def remove(self, _id):
        if not isinstance(_id, ObjectId):
            _id = ObjectId(_id)
        return self._db.delete_one({"_id": _id})