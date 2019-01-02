# -*- coding: utf-8 -*-
#!/usr/bin/python3
import importlib
from Common.Straw import Straw
from Common.Util import Util
from Protocol.DownloadProtocol import DownloadProtocol
import platform, os
import ctypes
import math
import time

class Download(Straw):
    '''
    执行任务类
    '''
    _taskObj = {}
    _taskName = None
    _isTest = False

    # 下载文件不需要加 .mp4 后缀的 cate
    _notMp4 = [3, 6, 9] 

    # 可用的下载器
    _dlMatchines = ['youget', 'youtubedl']

    def __init__(self, taskName, isTest = False):
        super().__init__()
        '''
        初始化任务类 
        taskName 任务类名
        '''
        self._taskName = taskName.capitalize()
        # 未指定下载器
        if not self._taskName:
            self._taskName = self._dlMatchines[0].capitalize()

        taskObj = importlib.import_module('.{}'.format(self._taskName), 'Service.Download')
        # 指定一个下载器
        self.getNewMatchine(taskObj, self._taskName)

        self._isTest = isTest


    configList = {}
    # 获取一个新的下载器
    def getNewMatchine(self, taskObj, taskName):
        config = self.getConfig()
        self.configList = {
            'uid': config.UID,
            'cateIds': config.CATE_IDS,
            'proxyIds': config.PROXY_IDS,
            'proxyInfo': "{}:{}".format(config.PROXY['proxyHost'], config.PROXY['proxyPort']),
            'notMp4': self._notMp4,
            'housewareUid': config.HOUSEWARE_UID,
            'params': {
                'youget': config.TASK['youGet'],
                'youtubedl': config.TASK['youTubeDl'],
                'dir': config.TASK['fileDir']
            }
        }
        self._taskObj = getattr(taskObj, taskName)(self.configList)
        if not isinstance(self._taskObj, DownloadProtocol):
            raise TypeError('Task must instance of DownloadProtocol')



    def dlFile(self, args = {}):
        '''
        下载影片
        videoId 指定下载视频 id
        dlMachine 指定下载方法 youget / youtubedl 默认自动，即不可用时切换
        toHouseware 上传至仓库
        '''
        if 'videoId' in args:
            # 指定视频 
            videoInfo = self.getModel('VideoList').getVideo(args['videoId'])
        else:
            # 获取一个未下载的视频 @todo 平台/获取规则 修改
            videoInfo = self.getModel('VideoSet').getUnDlRes(self.configList['uid'], 1)

        if not videoInfo:
            Util.info('该设备 {} 没有需要下载的资源'.format(self.configList['uid']))
            exit()

        Util.info("Download:{} dlFile".format(self._taskName))
        Util.info("正在下载影片 {}, videoId: {} setId: {}".format(videoInfo['name'], videoInfo['_id'], videoInfo['setId']))
        # 月日 文件夹
        dlPath = time.strftime("%m%d", time.localtime())
        # 绝对路径
        rdlPath = os.path.join(self.configList['params']['dir'], dlPath)
        if not os.path.exists(rdlPath):
            os.mkdir(rdlPath)
        # 文件名重新命名
        fileName = Util.genRandName(11) # 10位文件夹的 video 为 17版本, 11位的为 18版本
        rfileName = fileName + '.mp4' # 写入数据库的 名称
        dlfileName = fileName # 下载时用的名称
        if int(videoInfo['platform']) not in self.configList['notMp4']: # 乐视不需要 .mp4
            Util.info('File Add .mp4')
            dlfileName = rfileName

        # 是否使用代理
        doDl = 'dlFile'
        if int(videoInfo['platform']) in self.configList['proxyIds']:
            doDl = 'dlFileWithProxy'

        # 下载过程
        dlStatus = getattr(self._taskObj, doDl)(videoInfo['link'], rdlPath, rfileName, fileName)
            
        # 下载完成后首先确认文件是否存在
        if not os.path.exists(os.path.join(rdlPath, rfileName)):
            Util.error('确认影片失败，需要重新下载该影片')
            exit()

        # 下载成功
        if True == dlStatus:
            # 下载完成写入新记录
            self.getModel('VideoList').newPlay(videoInfo['_id'], self.configList['uid'], os.path.join(dlPath, rfileName))
            # 影片集 总下载数  + 1
            self.getModel("VideoSet").setCanPlayNum(videoInfo['setId'], self.configList['uid'])

            # 下载至 houseware
            if self.configList['uid'] == self.configList['housewareUid']:
                pass

            

        Util.info("Download:{} dlFile end".format(self._taskName))


    # 获取剩余空间 当前磁盘
    # return int GB 
    def getFreeDisk(self, folder = '/'):
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            return math.floor(free_bytes.value / 1024 / 1024 / 1024)
        else:
            st = os.statvfs(folder)
            return math.floor(st.f_bavail * st.f_frsize / 1024 / 1024)
