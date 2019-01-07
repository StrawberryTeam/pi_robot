# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from pypinyin import pinyin, lazy_pinyin, Style, slug #拼音
from pypinyin.contrib.mmseg import seg #分词
from functools import reduce
import getopt
import time
import random
from common import common, db



class zh2py():

    '''
    中文标题或内容 转 拼音/首拼 提供内容分词后 做为 tags 供搜索
    title_py/name_py 全拼  batamu like 匹配
    title_pyshow 拼音展示 bā tǎ mù 数组形式 匹配每个字
    summary_pyshow 简介拼音展示 
    title_sp 首拼  btm like 匹配
    tags 所有内容的 分词 大于1字  数组形式

    # @todo 训练分词 Seg.traion()
    '''

    _db = {}
    def __init__(self):
        self.initDb()


    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

    # 将所有 list 视频拼音化处理
    def list2py(self, runType = 'once'):
        vlist = self._db.getNonpyVideoList(10)
        if False == vlist:
            print("所有影片拼音全部处理完毕")
            exit()
        for data in vlist:
            newData = {}
            newData['name_py'] = slug(data['name'], errors='ignore', separator = '')
            newData['name_sp'] = slug(data['name'], style=Style.FIRST_LETTER, errors='ignore', separator = '')
            newData['name_pyshow'] = reduce(lambda x,y: x + y, pinyin(data['name']))
            # if data['summary']:
            #     newData['summary_pyshow'] =  reduce(lambda x,y: x + y, pinyin(data['summary']))
            #newData['tags'] = list(set(list(filter(lambda v: len(v) > 1, list(seg.cut(data['name'])))) + list(filter(lambda v: len(v) > 1, list(seg.cut(data['summary']))))))
            # print(newData['tags'])
            self._db.saveVideoPy(newData, data['_id']) # 保存拼音数据
            print("{} 影片拼音处理完毕".format(data['_id']))
            del newData
        del vlist, data
        if runType == 'loop': self.list2py() 

    # 剧集说明拼音化
    def set2py(self, runType = 'once'):
        # 每10条处理一次 递归直到全部完成
        vlist = self._db.getNonpySetList(10)
        if False == vlist:
            print("所有剧集拼音全部处理完毕")
            exit()
        for data in vlist:
            newData = {}
            newData['title_py'] = slug(data['title'], errors='ignore', separator = '')
            newData['title_sp'] = slug(data['title'], style=Style.FIRST_LETTER, errors='ignore', separator = '')
            newData['title_pyshow'] = reduce(lambda x,y: x + y, pinyin(data['title']))
            # if data['summary']:
            #     newData['summary_pyshow'] =  reduce(lambda x,y: x + y, pinyin(data['summary']))
            #newData['tags'] = list(set(list(filter(lambda v: len(v) > 1, list(seg.cut(data['title'])))) + list(filter(lambda v: len(v) > 1, list(seg.cut(data['summary']))))))
            # print(newData['tags'])
            self._db.saveSetPy(newData, data['_id']) # 保存拼音数据
            print("{} 剧集拼音处理完毕".format(data['_id']))
            del newData
        del vlist, data
        if runType == 'loop': self.set2py()


# 开启每日任务
if __name__ == "__main__":
    common.canISleep()

    zh = zh2py()
    try:
        if ('set' == sys.argv[1]):
            zh.set2py('loop')
        elif ('list' == sys.argv[1]):
            zh.list2py('loop')
    except IndexError:
        # 随机选择一个执行
        runNum = random.randint(1, 50)
        if runNum <= 1:
            zh.set2py('once')
        else:
            zh.list2py('once')
