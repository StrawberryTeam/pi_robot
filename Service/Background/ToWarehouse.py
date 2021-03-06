# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
import json
from Common.Straw import Straw
from Common.Util import Util
import shutil
import subprocess
import math


class ToWarehouse(Straw):
    '''
    创建仓库，并上传本地文件至远程仓库
    文件大于单个文件数量时 分割文件
        显示时长 s
    ffprobe -i VEYCaSRIBFn.mp4 -show_format -v quiet | sed -n 's/duration=//p'
        duration / filezise * maxsize 
    ffmpeg -i .\GxEfOYUhozv.mp4 -map 0 -c copy -f segment -segment_time 500 output_%03d.mp4
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

        if 'id' not in args:
            Util.error("Video id can not found")
            return False
        
        size = os.path.getsize(os.path.join(self._config.TASK['fileDir'], args['file']))
        # warehouse 单个文件不能超过 45MB
        sizeMb = size / 1024 / 1024
        # if sizeMb > 45:
        #     Util.error('{} 文件超过单个文件大小限制 size: {}MB'.format(args['file'], sizeMb))
        #     return False

        settingInfo = self.getModel('Setting').getSetting(self._config.WAREHOUSE['uid'])
        if 'lastRepoId' not in settingInfo:
            lastRepoId = "1"
        else:
            lastRepoId = str(settingInfo['lastRepoId'] + 1)

        # 本地文件夹不存在时
        if not os.path.exists(os.path.join(self._config.TASK['repoDir'], lastRepoId)):
            if False == self.createRepo(lastRepoId):
                # 创建仓库失败
                return False

        # 开始提交文件
        fileList = self.commitFiles(args['file'], lastRepoId, sizeMb)
        Util.info('更新远程地址 {}'.format(fileList))
        # 更新远程地址至 远程 UID
        self.getModel('VideoList').newPlay(args['id'], self._config.WAREHOUSE['uid'], fileList)
        return True


    _maxSize = 45 # max size MB
    # 获取总时长
    _getDuration = "ffprobe -i {} -show_format -v quiet"
    # 开始切分
    _doSegment = "ffmpeg -i {} -map 0 -c copy -f segment -segment_time {} {}_%03d.mp4"
    # 提交文件至仓库
    def commitFiles(self, file, repoName, fileSize):
        '''
            file 待提交文件
            repoName 待提交创建名称
            fileSize 待提交文件大小 MB
        '''

        os.chdir(os.path.join(self._config.TASK['repoDir'], repoName))
        os.system('git pull origin gh-pages')
        fileList = []
        # 超过单个文件大小限制的
        if fileSize > self._maxSize:
            fileDuration = subprocess.check_output(self._getDuration.format(os.path.join(self._config.TASK['fileDir'], file)))
            fileDuration = fileDuration.decode('UTF-8')
            fileDuration = fileDuration[fileDuration.find('duration=', 0) + 9:fileDuration.find('size=', fileDuration.find('duration=', 0))]
            segmentTime = float(fileDuration) / float(fileSize) * self._maxSize
            Util.info('Files duration')
            Util.info(segmentTime, float(fileDuration),  float(fileSize), self._maxSize)
            # 创建新的批量文件名 newFileName_000.mp4
            newFileName = Util.genRandName(11)
            os.system(self._doSegment.format(os.path.join(self._config.TASK['fileDir'], file), segmentTime, newFileName))
            # 最大文件数
            fileNum = math.ceil(float(fileDuration) / segmentTime)
            # 确认文件列表
            print('filenummmmm', fileNum)
            for num in range(fileNum):
                if True == os.path.isfile("%s_%03d.mp4" % (newFileName, num)): 
                    fileList.append("https://%s/%s/%s_%03d.mp4" % (self._config.WAREHOUSE['host'], repoName, newFileName, num))
        else:
            shutil.copyfile(os.path.join(self._config.TASK['fileDir'], file), os.path.join(self._config.TASK['repoDir'], repoName, os.path.basename(file)))
            fileList.append("https://{}/{}/{}".format(self._config.WAREHOUSE['host'], repoName, os.path.basename(file)))
        os.system('git add *.mp4 && git add *.jpg && git add *.png && git add *.jpeg')
        os.system('git commit -m {}'.format(os.path.basename(file)))
        os.system('git push origin gh-pages')
        Util.info("文件添加至仓库成功")
        return fileList

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
            return False

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
