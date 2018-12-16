# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from common import common, db, config


class clearfile():

    '''
        清理实际未成功下载的影片任务，并重新设置为下载中去下载
    '''

    _db = {}
    def __init__(self):
        self.initDb()
        videoList = self._db.getDledRes(config.uid)
        if False == videoList:
            print('本平台 {} 没有已下载完成的资源'.format(config.uid))
            exit()
        # 开始处理
        for video in videoList:
            videoFile = os.path.join(config.file_dir, video['plays'][config.uid])
            if not os.path.exists(videoFile):
                # 文件不存在
                # 移出本片下载地址
                self._db.rmVideo(video['_id'], config.uid)
                # 移出下载完成 设置为下载中 减少下载成功数量
                self._db.setVSetOnDl(video['setId'], config.uid)

        print('全部处理完成')
        exit()

    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

clearfile()
