# -*- coding: utf-8 -*-
#!/usr/bin/python3
import importlib
from Common.Straw import Straw
from Protocol.DownloadProtocol import DownloadProtocol
from Common.Util import Util
import platform, os
import ctypes
import math

class Download(DownloadProtocol, Straw):
    '''
    执行任务类
    '''
    _taskObj = {}
    _taskName = None
    _isTest = False

    # 下载器 id
    _uid = None

    # 可用 分类 (风行 cid = 2 会自动下载剧集中的全部影片，计划任务中先不下载风行的影片)
    _cateIds = []

    # 下载文件不需要加 .mp4 后缀的 cate
    _notMp4 = [3, 6, 9] 

    # 需要代理的 cate
    _proxyIds = []

    # 代理地址:端口
    _proxyInfo = None

    _params = {}

    # 可用的下载器
    _dlMatchines = ['youget', 'youtubedl']

    def __init__(self, taskName, isTest = False):
        super().__init__()
        '''
        初始化任务类 
        taskName 任务类名
        '''
        self._taskName = taskName
        taskObj = importlib.import_module('.{}'.format(taskName), 'Service.Download')
        # 未指定下载器
        if not taskName:
            taskName = self._dlMatchines[0]

        # 指定一个下载器
        self.getNewMatchine(taskObj, taskName)

        self._isTest = isTest


    # 获取一个新的下载器
    def getNewMatchine(self, taskObj, taskName):
        configList = {}
        config = self.getConfig()
        configList['uid'] = config.UID
        configList['cateIds'] = config.CATE_IDS
        configList['proxyIds'] = config.PROXY_IDS
        configList['proxyInfo'] = "{}:{}".format(config.PROXY['proxyHost'], config.PROXY['proxyPort'])
        configList['params'] = {
            'youget': config.TASK['youGet'],
            'youtubedl': config.TASK['youTubeDl'],
            'dir': config.TASK['fileDir']
        }
        self._taskObj = getattr(taskObj, taskName)(configList)
        if not isinstance(self._taskObj, DownloadProtocol):
            raise TypeError('Task must instance of DownloadProtocol')



    def dlFile(self, args = {}):
        '''
        下载影片
        videoId 指定下载视频 id
        dlMachine 指定下载方法 youget / youtubedl 默认自动，即不可用时切换
        toHouseware 上传至仓库
        '''
        Util.info("Download:{} dlFile".format(self._taskName))
        self._taskObj.dlFile(args)
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
