# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
import json
import string
import random
import getopt
import time
import platform
import ctypes
import math
from Protocol.DownloadProtocol import DownloadProtocol
from Common.Straw import Straw
from Common.Util import Util


class Youget(DownloadProtocol, Straw):
    '''
    Youget 下载器
    '''

    _db = {}
    def __init__(self, args):
        print(args)
        print('Do Youget downloader')


    # 下载文件
    def dlFile(self, args):
        exit()
        # data = self._db.getUnDlRes(self._uid, platform)
        # if False == data:
        #     print('该设备 {} 没有需要下载的资源'.format(self._uid))
        #     exit()

        print("正在下载影片 {}, videoId: {} setId: {}".format(data['name'], data['_id'], data['setId']))
        # 月日 文件夹
        dlPath = time.strftime("%m%d", time.localtime())
        # 绝对路径
        rdlPath = os.path.join(self._params['dir'], dlPath)
        if not os.path.exists(rdlPath):
            os.mkdir(rdlPath)
        # 文件名重新命名
        fileName = common.genRandName(10)
        '''
        -O FILE, --output-filename FILE
                        Set output filename
        -o DIR, --output-dir DIR
                        Set output directory
        '''
        rfileName = fileName + '.mp4' # 写入数据库的 名称
        dlfileName = fileName # 下载时用的名称
        if int(platform) not in self._notMp4: # 乐视不需要 .mp4
            print('File Add .mp4')
            dlfileName = rfileName
        print("开始下载 {}".format(os.path.join(rdlPath, rfileName)))
        # 需要代理的 平台
        if int(platform) in self._proxyIds:
            print("Dl with proxy")
            try:
                os.system("{} {} -o {} -O {} -s {}".format(self._params['get'], data['link'], rdlPath, dlfileName, self._proxyInfo))
            except:
                print('影片未成功下载')
                exit()
        else:
            print("Dl without proxy")
            try:
                # 正常平台下载
                os.system("{} {} -o {} -O {}".format(self._params['get'], data['link'], rdlPath, dlfileName))
            except:
                print('影片未成功下载')
                exit()
        
        # 下载完成后首先确认文件是否存在
        if not os.path.exists(os.path.join(rdlPath, rfileName)):
            print('确认影片失败，需要重新下载该影片')
            exit()

        # 视频转码 uid = 2 转码 其他暂时不转
        if '2' == config.uid:
            convertCls = convert.convert()
            rfileName = convertCls.toMp4(dlPath, rfileName)

        # 下载完成写入新记录
        self._db.newPlay(data['_id'], self._uid, os.path.join(dlPath, rfileName))
        # 影片集 总下载数  + 1
        self._db.setCanPlayNum(data['setId'], self._uid)
        print('影片下载完成')
        exit()

