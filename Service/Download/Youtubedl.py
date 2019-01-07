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


class Youtubedl(DownloadProtocol, Straw):
    '''
    Youtubedl 下载器
    '''

    _downloader = 'Youtubedl'
    _db = {}
    _args = {}
    def __init__(self, args):
        '''
        --get-duration                   Simulate, quiet but print video length
        --get-filename                   Simulate, quiet but print output filename
        --get-format                     Simulate, quiet but print output format
        --proxy URL                      Use the specified HTTP/HTTPS/SOCKS proxy.
                                         To enable SOCKS proxy, specify a proper
                                         scheme. For example
                                         socks5://127.0.0.1:1080/. Pass in an empty
                                         string (--proxy "") for direct connection
        -f, --format FORMAT              Video format code, see the "FORMAT
                                        SELECTION" for all the info
        --all-formats                    Download all available video formats
        --prefer-free-formats            Prefer free video formats unless a specific
                                        one is requested
        -o, --output TEMPLATE            Output filename template, see the "OUTPUT
                                        TEMPLATE" for all the info
        '''
        Util.info('Do {} downloader'.format(self._downloader))
        self._args = args

    def dlFileWithProxy(self, link, rdlPath, dlfileName):
        Util.info("Dl with proxy")

        filename = subprocess.check_output([self._args['params']['youtubeDl'], link, '--get-filename', '-o', '{}.%(ext)s'.format(dlfileName), '--proxy', 'socks5://{}/'.format(self._args['proxyInfo'])])
        # 正常平台下载
        try:
            subprocess.check_call([self._args['params']['youtubeDl'], link, '-o', '{}/{}.%(ext)s'.format(rdlPath, dlfileName), '-f', 'bestvideo+bestaudio/best', '--proxy', 'socks5://{}/'.format(self._args['proxyInfo'])])
        except subprocess.CalledProcessError as err:
            Util.error(err) # 记录 Error 至 db
            Util.info('Youtubedl:影片未成功下载')
            return False

        return filename.decode('UTF-8').strip()


    def dlFile(self, link, rdlPath, dlfileName):
        Util.info("Dl without proxy")

        filename = subprocess.check_output([self._args['params']['youtubeDl'], link, '--get-filename', '-o', '{}.%(ext)s'.format(dlfileName)])
        # 正常平台下载
        try:
            subprocess.check_call([self._args['params']['youtubeDl'], link, '-o', '{}/{}.%(ext)s'.format(rdlPath, dlfileName), '-f', 'bestvideo+bestaudio/best'])
        except subprocess.CalledProcessError as err:
            Util.error(err) # 记录 Error 至 db
            Util.info('Youtubedl:影片未成功下载')
            return False

        return filename.decode('UTF-8').strip()