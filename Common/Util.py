# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Common.Straw import Straw
import socks
import urllib.request as urllib2
import requests
from sockshandler import SocksiPyHandler
from bson.objectid import ObjectId
import random
import string
import time
import hashlib

class Util(Straw):
    
    # get 方式获取
    @staticmethod
    def getPage(link, isJson = False, proxy = False, openOnly = False):
        '''
        link 地址
        isJosn json 格式解析
        proxy 使用代理
        openOnly 仅打开为流
        '''
        # 要求使用 代理
        if True == proxy:
            Util.info('Open page with proxy')
            proxyConfig = Straw.getConfig(Straw, 'PROXY')
            proxies = {'http': "socks5://{}:{}".format(proxyConfig['proxyHost'], proxyConfig['proxyPort'])}
            # opener = urllib2.build_opener(SocksiPyHandler(socks.SOCKS5, proxyConfig['proxyHost'], proxyConfig['proxyPort']))
            # if True == openOnly:
            #     res = opener.open(link)
            # else:
            #     res = opener.open(link).read()
        else:
            Util.info('Open page without proxy')

        if True == openOnly:
            # @todo urlopen 使用 Proxy 的选项
            res = urllib2.urlopen(link)
        else:
            try:
                res = requests.get(link, proxies=proxies if True == proxy else False)
                res.raise_for_status()
            except res.exceptions.HTTPError as e:
                # Whoops it wasn't a 200
                Util.error("Get page error: {}".format(str(e)))
                return False
        if True == isJson:
            res = res.json()
        return res

    # post 方式获取
    @staticmethod
    def postPage(link, data = {}):
        return requests.post(link, data=data)

    # 检查必须字段
    @staticmethod
    def checkRequire(data, fields):
        # 多维数组
        if isinstance(data, list):
            for childData in data:
                return Util.checkRequire(childData, fields)
        else:
            # 从必须字段中 找不存在于 data 中的 key
            for k in fields:
                if k not in data:
                    return k
        return True

    # 移除非法字段  转换字段类型
    '''
    fields 合法字段 list
    convertFields 转换字段类型 dict
    '''
    @staticmethod
    def removeUnsafeFields(data, fields, convertFields):
        # 多维数组
        if isinstance(data, list):
            safeData = []
            for childData in data:
                safeData.append(Util.removeUnsafeFields(childData, fields, convertFields))
        else:
            safeData = {}
            for k, v in data.items():
                if k not in fields:
                    continue
                safeData[k] = Util.conv2(v, convertFields[k])
        return safeData


    # 转换类型
    @staticmethod
    def conv2(v, stype):
        if 'objectid' == stype and not isinstance(v, ObjectId):
            return ObjectId(v)
        if 'string' == stype and not isinstance(v, str):
            return str(v)
        if 'int' == stype and not isinstance(v, int):
            return int(v)
        if 'dict' == stype and not isinstance(v, dict):
            return dict(v)
        if 'list' == stype and not isinstance(v, list):
            return list(v)
        if 'bool' == stype and not isinstance(v, bool):
            return bool(v)
        # 原始类型
        return v

    # 中文化显示 播放量数量
    @staticmethod
    def getPlayNumTxt(playnum):
        try:
            playnum = int(playnum)
            if playnum < 10000:
                return str(playnum) 
            if playnum >= 10000 and playnum < 100000000:
                return str(round(playnum / 10000, 1)) + '万'
            if playnum >= 100000000:
                return str(round(playnum / 100000000, 1)) + '亿'
        except ValueError as msg:
            return playnum

    # 中文转数字化
    @staticmethod
    def getRealPlayNum(numtxt):
        if -1 != numtxt.find('亿'):
            num = numtxt.replace('亿', '').strip()
            return int(float(num) * 100000000)
        if -1 != numtxt.find('万'):
            num = numtxt.replace('万', '').strip()
            return int(float(num) * 10000)
        if -1 != numtxt.find('千'):
            num = numtxt.replace('千', '').strip()
            return int(float(num) * 1000)

    # 获取随机名称 目录名/文件夹
    @staticmethod
    def genRandName(length = 5):
        return ''.join(random.sample(string.digits+string.ascii_letters * 10, length))

    # 是否该休息了
    @staticmethod
    def canISleep():
        sleepTime = Straw.getConfig(Straw, 'SLEEP')
        Util.info('任务开始 {}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        # 23 - 2点休息
        nhour = int(time.localtime(time.time()).tm_hour)
        if (nhour in sleepTime):
            Util.info('Sleep time, quit!') 
            exit()
        return True

    # 对文件做 md5 验证完整性
    @staticmethod
    def fileHashMd5(file):
        hash_md5 = hashlib.md5()
        with open(file, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    # 错误信息
    @staticmethod
    def error(msg):
        '''
        @todo 入 mongodb
        '''
        print("Error: ---- {}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        print(msg)
        exit()

    # 显示 info 日志
    @staticmethod
    def info(*msg):
        '''
        @todo 入 mongodb / es 查看
        '''
        print(msg)