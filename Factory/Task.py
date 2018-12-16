# -*- coding: utf-8 -*-
#!/usr/bin/python3
import importlib
from Protocol.TaskProtocol import TaskProtocol

class Task(TaskProtocol):
    '''
    执行任务类
    '''
    _taskObj = {}

    def __init__(self, taskName):
        taskObj = importlib.import_module('.{}'.format(taskName), 'Service.Task')
        self._taskObj = getattr(taskObj, taskName)()


    def getCategoryList(self):
        '''
        一次性获取所有分类内容
        '''
        self._taskObj.getCategoryList()