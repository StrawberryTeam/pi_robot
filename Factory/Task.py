# -*- coding: utf-8 -*-
#!/usr/bin/python3
import importlib
from Common.Straw import Straw
from Protocol.TaskProtocol import TaskProtocol
from Common.Util import Util

class Task(TaskProtocol, Straw):
    '''
    执行任务类
    '''
    _taskObj = {}
    _taskName = None
    _isTest = False

    def __init__(self, taskName, isTest = False):
        super().__init__()
        '''
        初始化任务类 
        taskName 任务类名
        '''
        self._taskName = taskName.capitalize()
        taskObj = importlib.import_module('.{}'.format(self._taskName), 'Service.Task')
        self._taskObj = getattr(taskObj, self._taskName)()
        if not isinstance(self._taskObj, TaskProtocol):
            raise TypeError('Task must instance of TaskProtocol')
        self._isTest = isTest

    def getCategoryList(self, args):
        '''
        一次性获取所有分类内容
        '''
        Util.info("Task:{} getCategoryList args {}".format(self._taskName, args))
        if not self._taskObj.cateLinks or len(self._taskObj.cateLinks) == 0:
            Util.error('Task:{} cateLinks can not empty on getCategoryList'.format(self._taskName))

        startPage = args[0] if args[0] else 1
        endPage = args[1] if args[1] else 10
        # 取所有链接
        for link in self._taskObj.cateLinks:
            # 每一页
            for page in range(startPage, startPage + endPage):
                print("Do page {}".format(page))
                # 带 page 的 链接
                fLink = link.format(str(page))
                # 影片集内容
                setList = self._taskObj.getCategoryList(fLink)
                # 没有待处理数据
                if len(setList) <= 0:
                    Util.info('Category {} with page {} empty'.format(link, page))
                    continue

                # 测试用
                # print(setList)
                # exit()
                # 测试用 end

                # 处理每个影片集
                for setInfo in setList:
                    self.getSetContent(setInfo)

    def getSetContent(self, link):
        '''
        获取本影片集信息, 保存影片集信息
        '''
        Util.info("Task:{} getSetContent link {}".format(self._taskName, link))
        seterId = self._taskObj.getSetContent(link)

        Util.info("Task:{} getSetContent end".format(self._taskName))
        if False != seterId:
            self.getVideoList(seterId, link)

    def getVideoList(self, seterId, setLink):
        '''
        获取影片集下的所有影片列表
        '''
        Util.info("Task:{} getVideoList seterId {}".format(self._taskName, seterId))
        self._taskObj.getVideoList(seterId, setLink)
        Util.info("Task:{} getVideoList end".format(self._taskName))
