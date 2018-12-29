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

    _downloader = 'Youget'
    _db = {}
    _args = {}
    def __init__(self, args):
        Util.info('Do {} downloader'.format(self._downloader))
        self._args = args


    def dlFile(self, link, rdlPath, rfileName, dlfileName, toWarehouse = False):
        '''
        下载文件
        toWarehouse 是否上传至 远程仓库
        '''

        '''
        -O FILE, --output-filename FILE
                        Set output filename
        -o DIR, --output-dir DIR
                        Set output directory
        '''

        Util.info("开始下载 {}".format(os.path.join(rdlPath, rfileName)))
        # 需要代理的 平台
        if int(platform) in self._args['proxyIds']:
            Util.info("Dl with proxy")
            try:
                os.system("{} {} -o {} -O {} -s {}".format(self._args['params']['youget'], link, rdlPath, dlfileName, self._args['proxyInfo']))
            except:
                Util.info('影片未成功下载')
                exit()
        else:
            Util.info("Dl without proxy")
            try:
                # 正常平台下载
                os.system("{} {} -o {} -O {}".format(self._args['params']['youget'], link, rdlPath, dlfileName))
            except:
                Util.info('影片未成功下载')
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

