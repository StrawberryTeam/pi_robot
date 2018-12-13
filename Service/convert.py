# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import json
import string
# import subprocess
from common import common, db, config


class convert():
    '''
    视频转码为 WEB 可播放格式
    ffmpeg -i 'INPUT' -acodec aac -ab 128k -vcodec libx264 -f mp4 -s hd480 out.mp4
    '''

    def __init__(self):
        pass

        
    # 下载文件
    def toMp4(self, dlPath, inputFile):
        outputFile = common.genRandName(10) #重新命名
        rInputFile = os.path.join(config.file_dir, dlPath, inputFile) #完整路径
        rOutputFile = "{}.mp4".format(os.path.join(config.file_dir, dlPath, outputFile)) #完整路径
        print('开始转码 {}'.format(inputFile))
        try:
            os.system("ffmpeg -i {} -acodec aac -ab 128k -vcodec libx264 -f mp4 -s hd480 {}".format(rInputFile, rOutputFile))
        except:
            print('转码失败')
        os.remove(rInputFile)
        return "{}.mp4".format(outputFile)

if __name__ == "__main__":
    convert = convert()
    convert.toMp4('', 'mt1.mp4')
