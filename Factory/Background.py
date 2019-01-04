# -*- coding: utf-8 -*-
#!/usr/bin/python3
import importlib
from Common.Straw import Straw
from Common.Util import Util
import platform, os
import ctypes
import math
import time

class Background(Straw):
    '''
    背景执行
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

        self._isTest = isTest

        taskObj = importlib.import_module('.{}'.format(self._taskName), 'Service.Background')
        # 开始一个任务
        self._taskObj = getattr(taskObj, self._taskName)()

    # 任意 func
    def __getattr__(self, methodName):
        def func(*args, **kwargs):
            getattr(self._taskObj, methodName)(*args, **kwargs)
        return func