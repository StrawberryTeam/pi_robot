# -*- coding: utf-8 -*-
#!/usr/bin/python3
import importlib
from Common.Straw import Straw
from Protocol.TaskProtocol import TaskProtocol

class Task(Straw):
    '''
    执行任务类
    '''
    _taskObj = {}

    def __init__(self, taskName):
        super().__init__()
        '''
        初始化任务类 
        taskName 任务类名
        '''
        taskObj = importlib.import_module('.{}'.format(taskName), 'Service.Task')
        self._taskObj = getattr(taskObj, taskName)()
        if not isinstance(self._taskObj, TaskProtocol):
            raise TypeError('Task must instance of TaskProtocol')


    def getCategoryList(self, args):
        '''
        一次性获取所有分类内容
        '''
        self._taskObj.getCategoryList(args)

    def getVideoList(self, link, startPage = 1, endPage = None):
        pass