# -*- coding: utf-8 -*-
#!/usr/bin/python3
from abc import ABCMeta, abstractmethod

class TaskProtocol(metaclass=ABCMeta):
    '''
    任务发布 接口
    '''
    
    @abstractmethod
    def getCategoryList(self):
        '''
        获取所有分类列表
        '''
        pass

    @abstractmethod
    def getVideoList(self, link, startPage = 1, endPage = None):
        '''
        给定分类获取所有 videos
        '''
        pass