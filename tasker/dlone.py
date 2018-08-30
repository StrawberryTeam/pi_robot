# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import getopt
import time
import random
from urllib import request
from bs4 import BeautifulSoup
from common import common, db


class dlone():

    '''
        下一部影片集
    '''

    _host = "http://192.168.1.10/"

    _setId = "5ae10c1672ab8a1a226b897a"

    _db = {}
    def __init__(self):
        self.initDb()
        videoList = self._db.getVideoListBySetId(self._setId)
        print(videoList)
        if False == videoList:
            print('没有找到任何影片内容')
            exit()
            
        for video in videoList:
            if video['plays']['1']:
                url = self._host + video['plays']['1']
                # setid 作为文件夹
                if not os.path.exists(self._setId):
                    os.mkdir(self._setId)
                with request.urlopen(url) as file:
                    # 为保险起见使用二进制写文件模式，防止编码错误
                    name = BeautifulSoup(video['name'], 'lxml').get_text()
                    name = name.replace("|", "").replace("(","").replace(")","").replace("?","").replace("/","").replace("\\","")
                    filename = self._setId + '/' + name + '.mp4'
                    with open(filename, 'wb') as outfile:
                        outfile.write(file.read())
        print('全部下载完成')

    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

dlone()
