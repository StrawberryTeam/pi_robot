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
        '''
        -O FILE, --output-filename FILE
                        Set output filename
        -o DIR, --output-dir DIR
                        Set output directory
        '''
        Util.info('Do {} downloader'.format(self._downloader))
        self._args = args

    def dlFileWithProxy(self, link, rdlPath, rfileName, dlfileName):
        Util.info("Dl with proxy {}".format(os.path.join(rdlPath, rfileName)))
        dlStatus = os.system("{} {} -o {} -O {} -s {}".format(self._args['params']['youget'], link, rdlPath, dlfileName, self._args['proxyInfo']))
        if 0 == dlStatus:
            return True
        else:
            Util.info('Youget:影片未成功下载')
            return False

    def dlFile(self, link, rdlPath, rfileName, dlfileName):
        Util.info("Dl without proxy {}".format(os.path.join(rdlPath, rfileName)))
        # 正常平台下载
        dlStatus = os.system("{} {} -o {} -O {}".format(self._args['params']['youget'], link, rdlPath, dlfileName))
        if 0 == dlStatus:
            return True
        else:
            Util.info('Youget:影片未成功下载')
            return False