# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
import json
import string
from Common.Straw import Straw
from Common.Util import Util
# import subprocess

class Convert(Straw):
    '''
    视频转码为 WEB 可播放格式
    ffmpeg -i 'INPUT' -acodec aac -ab 128k -vcodec libx264 -f mp4 -s hd480 out.mp4
    '''

    _config = {}
    def __init__(self):
        self._config = self.getConfig('TASK')
        pass

        
    # 下载文件
    def toMp4(self, args):
        print('Do convert:tomp4')
        if 'dlPath' not in args:
            dlPath = ''
        else:
            dlPath = args['dlPath']

        if 'inputFile' not in args:
            Util.error('Input file not found.')
        else:
            inputFile = args['inputFile']
        '''
        dlPath 文件目录
        inputFile 输入文件
        '''
        outputFile = Util.genRandName(11) #重新命名
        rInputFile = os.path.join(self._config['fileDir'], dlPath, inputFile) #完整路径
        rOutputFile = "{}.mp4".format(os.path.join(self._config['fileDir'], dlPath, outputFile)) #完整路径
        Util.info('开始转码 {}'.format(inputFile))
        convertStatus = os.system("ffmpeg -i {} -acodec aac -ab 128k -vcodec libx264 -f mp4 -s hd1080 {}".format(rInputFile, rOutputFile))
        if 0 == convertStatus:
            Util.info('转码成功 {}'.format(rOutputFile))
            # 移除原文件
            os.remove(rInputFile)
            return "{}.mp4".format(os.path.join(dlPath, outputFile))
        else:
            Util.error('转码失败')
            return False

