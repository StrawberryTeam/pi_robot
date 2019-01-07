# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import getopt
import time
import random
import shutil
import tarfile
from urllib import request
from bs4 import BeautifulSoup
from common import common, db, config


class transfer():

    '''
        传送影片
    '''

    _db = {}
    _fromUid = ''
    _toUid = ''
    _setId = ''
    _taskId = ''
    '''
        fromUid 从哪个设备复制，即有影片的设备 id
        toUid 复制至设备 id
        setId 待复制的影片集 id
    '''
    def __init__(self, fromUid, toUid, taskId):
        self.initDb()
        self._fromUid = str(fromUid)
        self._toUid = str(toUid)
        self._taskId = str(taskId)

    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

    # 待打包数据
    _packList = []
    # 打包需要传送的文件
    def getPackFiles(self, setId):
        self._setId = setId
        setItem = self._db.getSetInfo(self._setId)
        # 当前设备本影片集是否下载完成
        if self._fromUid not in setItem['dled']:
            print("该影片还未下载完成 setId: {}".format(self._setId))
            exit()

        # 目标设备是否存在或正在下载该影片
        if self._toUid in setItem['dled'] or self._toUid in setItem['dl']:
            print('目标设备 Uid: {}, 正在下载或已存在本影片集内容 setId: {}'.format(self._toUid, self._setId))
            exit()

        # 影片集封面图
        if setItem['imgs'][self._fromUid]:
            self._packList.append((config.file_dir, setItem['imgs'][self._fromUid]))

        # 找影片内容
        videoList = self._db.getVideoListBySetId(self._setId)
        if False == videoList:
            print('没有找到任何影片内容')
            exit()
            
        for video in videoList:
            # 影片封面
            if video['imgs'][self._fromUid]:
                self._packList.append((config.file_dir, video['imgs'][self._fromUid]))
            # 影片内容
            if video['plays'][self._fromUid]:
                self._packList.append((config.file_dir, video['plays'][self._fromUid]))

        return self.doPack()

    # 开始打包文件至临时文件夹 
    def doPack(self):
        if len(self._packList) == 0:
            print("没有找到已下载的影片或封面文件")
            exit()
        
        # 创建本任务的临时文件夹
        packName = str(self._setId)#common.genRandName(8)
        packPath = config.temp_dir#os.path.join(config.temp_dir, packName)
        # try:
        #     if not os.path.exists(packPath):
        #         os.mkdir(packPath)
        # except OSError as msg:
        #     print("{} 临时文件夹未创建或没有写入权限, 打包文件失败: {}".format(packPath, msg))
        #     exit()
        if not os.path.exists(packPath):
            print("{} 临时文件夹未创建或没有写入权限".format(packPath))
            exit()

        # 复制文件
        tarFilePath = "{}.tar.gz".format(os.path.join(config.temp_dir, packName))
        tar = tarfile.open(tarFilePath, "w:gz")
        for file in self._packList:
            (fileDir, fileUrl) = file

            # newFileDir = os.path.dirname(os.path.join(packPath, fileUrl))
            # if not os.path.exists(newFileDir):
            #     os.makedirs(newFileDir)
            toFile = os.path.join(fileDir, fileUrl) 
            try:
                # shutil.copyfile(os.path.join(fileDir, fileUrl), toFile)
                tar.add(toFile, arcname=fileUrl)
            except FileNotFoundError as msg:
                print('部分文件未找到 {}'.format(msg))
                continue
            del fileDir, fileUrl, toFile
        tar.close()

        # 删除文件夹
        # shutil.rmtree(packPath)

        if os.path.exists(tarFilePath):
            return self.doTransfer(tarFilePath)
        else:
            self._db.taskDoing(self._setId) # 任务失败
            print('未能成功打包文件')
            exit()

    
    # 开始传送
    def doTransfer(self, tarFilePath):
        print('Do Trans {} taskId: {}'.format(tarFilePath, self._taskId))
        tranStatus = os.system("rsync -P --rsh=ssh {0} {1}:{2}/{3}".format(tarFilePath, config.server_ssh, config.server_disk1, os.path.basename(tarFilePath)))
        # os.system("scp {0} {1}:{2}/{3}".format(tarFilePath, config.server_ssh, config.server_disk1, os.path.basename(tarFilePath)))
        if 0 != tranStatus:
            self._db.taskTransferFaild(self._taskId)
            print('传送失败 {}'.format(tarFilePath))
            exit()

        self._db.taskTransferComplete(self._taskId, common.fileHashMd5(tarFilePath), "{0}/{1}".format(config.server_disk1, os.path.basename(tarFilePath)))
        # os.remove(tarFilePath)
        print('传送完成')

    # 开始接收
    def doReceive(self, fileMd5, filePath):
        print("Do receivce taskId: {}".format(self._taskId))

        pass

trans = transfer('1', '3', '5b10eaa011e4f0e0456d269d')
# 传送
# trans.getPackFiles('5a3b5e9a72ab8a4f934b7ebf')
# 接收
trans.doReceive('c9c70a5b80fea4657dba39eafe9f53f7', 'C:/Users/zackl/python/pi_robot/files/_temp/5a3b5e9a72ab8a4f934b7ebf.tar.gz')