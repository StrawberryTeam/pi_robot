# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
import json
from Common.Straw import Straw
from Common.Util import Util
import shutil


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
        
        size = os.path.getsize(os.path.join(self._config.TASK['fileDir'], args['file']))
        # warehouse 单个文件不能超过 95MB
        sizeMb = size / 1024 / 1024
        if sizeMb > 95:
            Util.error('{} 文件超过单个文件大小限制 size: {}MB'.format(args['file'], sizeMb))
            return False

        settingInfo = self.getModel('Setting').getSetting(self._config.UID)
        if 'lastRepoId' not in settingInfo:
            lastRepoId = "1"
        else:
            lastRepoId = str(settingInfo['lastRepoId'] + 1)

        originUrl = self.commitFiles(args['file'], lastRepoId)
        print(originUrl)
        if True == self.createRepo(lastRepoId):
            self.commitFiles(args['file'], lastRepoId)

    # 提交文件至仓库
    def commitFiles(self, file, repoName):
        os.chdir(os.path.join(self._config.TASK['repoDir'], repoName))
        os.system('git pull origin gh-pages')
        shutil.copyfile(os.path.join(self._config.TASK['fileDir'], file), os.path.join(self._config.TASK['repoDir'], repoName, os.path.basename(file)))
        os.system('git add *.mp4 && git add *.jpg && git add *.png && git add *.jpe')
        os.system('git commit -m {}'.format(os.path.basename(file)))
        os.system('git push origin gh-pages')
        print("文件添加至仓库")
        return "https://{}/{}/{}".format(self._config.WAREHOUSE['host'], repoName, os.path.basename(file))

    # 创建仓库
    _apiCreateRepo = {
        'url': 'https://api.github.com/user/repos?access_token={}',
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
    def createRepo(self, lastRepoId):

        # repo name
        self._apiCreateRepo['params']['name'] = '{}'.format(lastRepoId)
        info = Util.postPage(
            self._apiCreateRepo['url'].format(self._config.WAREHOUSE['token']), 
            json.dumps(self._apiCreateRepo['params'])
        )
        # 已经存在
        if 422 == info.status_code:
            Util.info('仓库已存在')
            return True
        elif 201 == info.status_code:
            self.createPage(lastRepoId)
            self.setRepoCname(lastRepoId)
            return True
        else:
            Util.error('本地仓库创建失败')
            return True

    # 创建 gh-pages
    def createPage(self, repoName):
        if not os.path.exists(os.path.join(self._config.TASK['repoDir'], repoName)):
            os.mkdir(os.path.join(self._config.TASK['repoDir'], repoName))
        os.chdir(self._config.TASK['repoDir'])
        # clone
        os.system("git clone https://github.com/{}/{}.git".format(self._config.WAREHOUSE['repoName'], repoName))
        os.chdir(repoName)
        os.system("git branch gh-pages")
        os.system("git checkout gh-pages")
        # os.system("git config user.email {}".format(self._config.WAREHOUSE['gitEmail']))
        # os.system("git config user.name {}".format(self._config.WAREHOUSE['gitUser']))
        os.system("git remote set-url origin git@{}:{}/{}".format(self._config.WAREHOUSE['gitUser'], self._config.WAREHOUSE['repoName'], repoName))
        # sshKey = open("{}{}".format(self._config.WAREHOUSE['sshPath'], self._config.WAREHOUSE['gitUser']), 'w+')
        # sshKey.write(self._config.WAREHOUSE['gitPriKey'].strip())
        # sshKey.close()
        os.system("git push origin gh-pages")
        print("Create gh-pages Ok")
        return True

    # 更新别名
    _apiUpdateCname = {
        'url': 'https://api.github.com/repos/{}/{}/pages?access_token={}',
        'params': {
            "cname": None,
            "source": "gh-pages"
        }
    }

    # 设置仓库别名
    def setRepoCname(self, repoName):
        # self._apiUpdateCname['params']['cname'] = "{}".format(self._config.WAREHOUSE['host'])
        cnameRes = Util.putPage(
            self._apiUpdateCname['url'].format(self._config.WAREHOUSE['repoName'], repoName, self._config.WAREHOUSE['token']),
            json.dumps(self._apiUpdateCname['params']),
            headers={'Accept': 'application/vnd.github.mister-fantastic-preview+json'}
        )

        if 400 == cnameRes.status_code:
            Util.info('仓库创建成功')
            return True
        else:
            Util.info('仓库创建失败 {}'.format(cnameRes))
            return False
