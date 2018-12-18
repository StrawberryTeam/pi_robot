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

    def __init__(self, taskName):
        super().__init__()
        '''
        初始化任务类 
        taskName 任务类名
        '''
        self._taskName = taskName
        taskObj = importlib.import_module('.{}'.format(taskName), 'Service.Task')
        self._taskObj = getattr(taskObj, taskName)()
        if not isinstance(self._taskObj, TaskProtocol):
            raise TypeError('Task must instance of TaskProtocol')

    def getCategoryList(self, args):
        '''
        一次性获取所有分类内容
        '''
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
                setInfo = self._taskObj.getCategoryList(fLink)
                if None == setInfo:
                    continue

    def getSetContent(self, movieInfo):
        pass

    def getVideoList(self, link, startPage = 1, endPage = None):
        pass