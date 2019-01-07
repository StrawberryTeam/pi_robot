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
import subprocess


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

    def dlFileWithProxy(self, link, rdlPath, dlfileName):
        Util.info("Dl with proxy")
        try:
            subprocess.check_call([self._args['params']['youGet'], link, '-o', rdlPath, '-O', dlfileName, '-s', self._args['proxyInfo']])
        except subprocess.CalledProcessError as err:
            Util.error(err) # 记录 Error 至 db
            Util.info('Youget:影片未成功下载')
            return False

        return dlfileName


    def dlFile(self, link, rdlPath, rfileName, dlfileName):
        Util.info("Dl without proxy")
        try:
            subprocess.check_call([self._args['params']['youGet'], link, '-o', rdlPath, '-O', dlfileName])
        except subprocess.CalledProcessError as err:
            Util.error(err) # 记录 Error 至 db
            Util.info('Youget:影片未成功下载')
            return False

        return dlfileName
