# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import json
import string
import random
import getopt
import time
import platform
import ctypes
import math
from common import common, db, config
import convert


class downloader():
    '''
    下载器
    '''
    # 下载器 id
    _uid = config.uid

    # 可用 分类 (风行 cid = 2 会自动下载剧集中的全部影片，计划任务中先不下载风行的影片)
    _cateIds = config.cateIds

    # 下载文件不需要加 .mp4 后缀的 cate
    _notMp4 = [3, 6, 9] 

    # 需要代理的 cate
    _proxyIds = config.proxyIds

    # 代理地址:端口
    _proxyInfo = "{}:{}".format(config.proxy_host, config.proxy_port)

    # status file
    _taskFile = 'task.json'

    _params = {}

    _db = {}
    def __init__(self):
        self.initDb()
        self._params = {
            'get': config.get_dir,
            'dir': config.file_dir
        }

        

    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

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

    # 下载文件
    def dlFile(self, platform):
        data = self._db.getUnDlRes(self._uid, platform)
        if False == data:
            print('该设备 {} 没有需要下载的资源'.format(self._uid))
            exit()

        print("正在下载影片 {}, videoId: {} setId: {}".format(data['name'], data['_id'], data['setId']))
        # 月日 文件夹
        dlPath = time.strftime("%m%d", time.localtime())
        # 绝对路径
        rdlPath = os.path.join(self._params['dir'], dlPath)
        if not os.path.exists(rdlPath):
            os.mkdir(rdlPath)
        # 文件名重新命名
        fileName = common.genRandName(10)
        '''
        -O FILE, --output-filename FILE
                        Set output filename
        -o DIR, --output-dir DIR
                        Set output directory
        '''
        rfileName = fileName + '.mp4' # 写入数据库的 名称
        dlfileName = fileName # 下载时用的名称
        if int(platform) not in self._notMp4: # 乐视不需要 .mp4
            print('File Add .mp4')
            dlfileName = rfileName
        print("开始下载 {}".format(os.path.join(rdlPath, rfileName)))
        # 需要代理的 平台
        if int(platform) in self._proxyIds:
            print("Dl with proxy")
            try:
                os.system("{} {} -o {} -O {} -s {}".format(self._params['get'], data['link'], rdlPath, dlfileName, self._proxyInfo))
            except:
                print('影片未成功下载')
                exit()
        else:
            print("Dl without proxy")
            try:
                # 正常平台下载
                os.system("{} {} -o {} -O {}".format(self._params['get'], data['link'], rdlPath, dlfileName))
            except:
                print('影片未成功下载')
                exit()
        
        # 下载完成后首先确认文件是否存在
        if not os.path.exists(os.path.join(rdlPath, rfileName)):
            print('确认影片失败，需要重新下载该影片')
            exit()

        # 视频转码 uid = 2 转码 其他暂时不转
        if '2' == config.uid:
            convertCls = convert.convert()
            rfileName = convertCls.toMp4(dlPath, rfileName)

        # 下载完成写入新记录
        self._db.newPlay(data['_id'], self._uid, os.path.join(dlPath, rfileName))
        # 影片集 总下载数  + 1
        self._db.setCanPlayNum(data['setId'], self._uid)
        print('影片下载完成')
        exit()

if __name__ == "__main__":
    common.canISleep()

    dl = downloader()

    cid = 0
    # 计划任务执行 每小时执行不同分类

    # 没给参数 走 task.json 文件获取
    if len(sys.argv) <= 1:
        print('Get cid from task.json')
        try:
            with open(dl._taskFile, 'r') as f:
                fContent = json.load(f)
                cid = fContent['cid']
        except FileNotFoundError:
            print('Task file not found')
        finally:
            # cid + 1 换分类
            try:
                cid = dl._cateIds[dl._cateIds.index(cid) + 1]
            except Exception:
                cid = dl._cateIds[0]
            print('Now task cid is {}'.format(cid))
        # 保存当前已操作的 分类
        with open(dl._taskFile, 'w') as f:
            f.write(json.dumps({'cid': cid}))
    else:
        '''
            直接给参数测试一个分类
            -c / -cid [cid]
        '''
        print('Get cid from args')
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hc:",["cid="])
            for opt, arg in opts:
                if opt == '-h':
                    print('downloader.py -c <cid {}>'.format(dl._cateIds))
                    sys.exit()
                elif opt in ("-c", "--cid"): 
                    cid = int(arg)
        except getopt.GetoptError:
            print('Do not found cid param')
        finally:
            if cid not in dl._cateIds:
                cid = dl._cateIds[0]
    # 开始下载过程
    dl.dlFile(cid)
