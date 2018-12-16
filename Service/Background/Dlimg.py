# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import getopt
import time
from common import common, db, config



class dlimg():

    '''
        本地化图片文件
    '''
    # 下载器 id
    _uid = config.uid

    _params = {}
    _db = {}

    # 下载图片时是否使用代理
    isProxy = False
    def __init__(self):
        self.initDb()
        self._params['dir'] = config.images_dir
    
    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

    def dling(self):
        # 所有需要下载图片的 ids
        setInfo = self._db.getVideoSetByDlImg(self._uid, config.needImgIds)
        # 首先下载 set 图片
        if False == setInfo:
            print("没有更多影片集图片需要下载")
            exit()

        # 本分类需要代理
        if setInfo['platform'] in config.proxyIds:
            self.isProxy = True
        else:
            self.isProxy = False

        dlPath = self.createImgDir() # 图片下载到文件夹
        # 下载所有内容数据
        videoList = self._db.getVideoListByDlImg(self._uid, setInfo['_id'])
        if False == videoList:
            print("没有更多影片内容图片需要下载")
            exit()

        for video in videoList:
            if not video['img']:
                continue
            # print(video)
            dlStatus = self.dlFile(video['img'], os.path.join(dlPath, common.genRandName() + os.path.splitext(video['img'])[1]))
            # 下载成功后写回数据
            if False != dlStatus:
                saveStatus = self._db.modifyVideoImg(video['_id'], {"img": dlStatus}, self._uid)
                if False == saveStatus:
                    print("video _id : {} 影片内容封面图片更新失败".format(video['_id']))
                else:
                    print('video _id : {} 影片内容封面图片下载成功，已更新至影片集'.format(video['_id']))
                del saveStatus
            del dlStatus

        dlStatus = self.dlFile(setInfo['img'], os.path.join(dlPath, common.genRandName() + os.path.splitext(setInfo['img'])[1]))
        # 下载成功后写回数据
        if False != dlStatus:
            saveStatus = self._db.modifySetImg(setInfo['_id'], {"img": dlStatus}, self._uid)
            if False == saveStatus:
                print("setId : {} 影片集封面图片更新失败".format(setInfo['_id']))
            else:
                print('setId: {} 影片集封面图片下载成功，已更新至影片集'.format(setInfo['_id']))
            del  saveStatus
        del dlStatus

        print("所有图片下载完成")



    def createImgDir(self):
        # 月日 文件夹
        dlPath = time.strftime("%m%d", time.localtime())
        # 绝对路径
        rdlPath = os.path.join(self._params['dir'], dlPath)
        if not os.path.exists(rdlPath):
            os.mkdir(rdlPath)
        return dlPath

    def dlFile(self, url, saveFile):
        if "http:" not in url and "https:" not in url:
            url = "http:" + url
        try:
            # with request.urlopen(url) as file:
            with common.getPage(url, proxy = self.isProxy, openOnly=True) as file:
                with open(os.path.join(self._params['dir'], saveFile), 'wb') as outfile:
                    outfile.write(file.read())
        except IOError as fileWriteError:
            print('写入文件失败 file {} save as {}'.format(url, os.path.join(self._params['dir'], saveFile)))
            return False
        else:
            return os.path.join('images', saveFile)


# 开启每日任务
if __name__ == "__main__":
    common.canISleep()

    dl = dlimg()
    dl.dling()