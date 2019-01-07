# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
import json
from Common.Straw import Straw
from Common.Util import Util


class ToWarehouse(Straw):
    '''
    创建仓库，并上传本地文件至远程仓库
    '''

    _config = {}
    def __init__(self):
        self._config = self.getConfig()
        pass

    # 处理文件
    def process(self, args):
        if 'file' not in args:
            Util.error('File can not found')
            return False
        
        size = os.path.getsize(os.path.join(self._config['TASK']['fileDir'], args['file']))
        # warehouse 单个文件不能超过 95MB
        sizeMb = size / 1024 / 1024
        if sizeMb > 95:
            Util.error('{} 文件超过单个文件大小限制 size: {}MB'.format(args['file'], sizeMb))
            return False

        self.createRepo()

    _apiCreateRepo = {
        'url': 'https://api.github.com/user/repos?access_token={}',
        'method': 'post',
        'params': {
            "name": "",
            "private": False,
            "has_issues": False,
            "has_projects": False,
            "has_wiki": False,
            "auto_init": True
        }
    }
    # 创建本地仓库
    def createRepo(self):
        settingInfo = self.getModel('Setting').getSetting(self._config['UID'])
        if 'lastRepoId' not in settingInfo:
            lastRepoId = 1
        else:
            lastRepoId = settingInfo['lastRepoId'] + 1

        # v1 video repo p1 pic repo
        self._apiCreateRepo['params']['name'] = 'v{}'.format(lastRepoId)
        Util.postPage(
            self._apiCreateRepo['url'].format(self._config['WAREHOUSE']['token']), 
            self._apiCreateRepo['params']
        )