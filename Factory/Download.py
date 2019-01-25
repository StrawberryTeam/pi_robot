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

    # 可用的下载器
    _dlMatchines = ['youtubedl', 'youget']

    def __init__(self, taskName, isTest = False):
        super().__init__()
        '''
        初始化任务类 
        taskName 任务类名
        '''
        self._taskName = taskName
        self._isTest = isTest
        # 未指定下载器
        if not self._taskName:
            self._taskName = self._dlMatchines[0].capitalize()
        # 指定一个下载器
        self.getNewMatchine(self._taskName)



    configList = {}
    # 获取一个新的下载器
    def getNewMatchine(self, taskName):

        taskObj = importlib.import_module('.{}'.format(taskName), 'Service.Download')
        config = self.getConfig()
        self.configList = {
            'uid': config.UID,
            'cateIds': config.CATE_IDS,
            'proxyIds': config.PROXY_IDS,
            'proxyInfo': "{}:{}".format(config.PROXY['proxyHost'], config.PROXY['proxyPort']),
            'warehouse': config.WAREHOUSE,
            'params': {
                'youGet': config.TASK['youGet'],
                'youtubeDl': config.TASK['youtubeDl'],
                'dir': config.TASK['fileDir']
            }
        }
        self._taskObj = getattr(taskObj, taskName)(self.configList)
        if not isinstance(self._taskObj, DownloadProtocol):
            raise TypeError('Task must instance of DownloadProtocol')


    # 下载文件不需要加 .mp4 后缀的 cate
    _notMp4 = [3, 6, 9] 
    _videoExt = ['', 'mp4', 'webm', 'flv', 'mkv', 'wmv', 'mov', 'avi']

    def dlFile(self, args = {}):
        '''
        下载影片
        videoId 指定下载视频 id
        dlMachine 指定下载方法 youget / youtubedl 默认自动，即不可用时切换
        '''
        if 'videoId' in args:
            # 指定视频 
            videoInfo = self.getModel('VideoList').getVideo(args['videoId'])
        else:
            # 获取一个未下载的视频 @todo 平台/获取规则 修改
            videoInfo = self.getModel('VideoSet').getUnDlRes(self.configList['uid'], 1)

        if not videoInfo:
            Util.info('该设备 {} 没有需要下载的资源'.format(self.configList['uid']))
            return False

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

        # 是否使用代理
        doDl = 'dlFile'
        if int(videoInfo['platform']) in self.configList['proxyIds']:
            doDl = 'dlFileWithProxy'

        Util.info("Download to {}".format(os.path.join(rdlPath, fileName)))
        # 下载过程
        dlFileName = getattr(self._taskObj, doDl)(videoInfo['link'], rdlPath, fileName)
            
        # 下载完成后首先确认文件是否存在
        videoExists = False
        for ext in self._videoExt:
            if os.path.exists(os.path.join(rdlPath, "{}.{}".format(dlFileName, ext))):
                dlFileName = "{}.{}".format(dlFileName, ext)
                videoExists = True
                break

        switchMatchine = True
        # 下载成功
        if False == videoExists:
            # 每次执行允许切换一次
            if False == switchMatchine:
                return False
            switchMatchine = False
            # 换下载方法进行下载
            tmpMatchine = self._dlMatchines
            tmpMatchine.remove(self._taskName.lower())
            return self.getNewMatchine(tmpMatchine[0].capitalize())
        else:
            # 开始转码 转为 web 可用格式
            webVideo = self.getService('Background.Convert').toMp4({'dlPath': dlPath, 'inputFile': dlFileName})
            # 下载完成写入新记录
            self.getModel('VideoList').newPlay(videoInfo['_id'], self.configList['uid'], webVideo)
            # 影片集 总下载数  + 1
            self.getModel("VideoSet").setCanPlayNum(videoInfo['setId'], self.configList['uid'])

            # 下载至 warehouse
            if self.configList['uid'] == self.configList['warehouse']['uid']:
                pass

            Util.info("Download:{} dlFile end".format(self._taskName))
            self.getFreeDisk()
            

    # 获取剩余空间 当前磁盘
    # return int GB 
    def getFreeDisk(self, folder = '/'):
        if platform.system() == 'Windows':
            free_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
            freeGb = math.floor(free_bytes.value / 1024 / 1024 / 1024)
        else:
            st = os.statvfs(folder)
            freeGb = math.floor(st.f_bavail * st.f_frsize / 1024 / 1024)

        # 写入剩余空间
        self.getModel('Setting').setFreeSpace(self.configList['uid'], freeGb)
        return freeGb
