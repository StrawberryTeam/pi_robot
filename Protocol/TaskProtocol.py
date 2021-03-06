# -*- coding: utf-8 -*-
#!/usr/bin/python3
from abc import ABCMeta, abstractmethod

class TaskProtocol(metaclass=ABCMeta):
    '''
    任务发布 接口
    '''
    
    @abstractmethod
    def getCategoryList(self, args):
        '''
        获取所有分类列表
        (1, 20)
        startPage 开始页或开始offset
        endPage 结束页或结束offset
        '''
        pass

    @abstractmethod
    def getSetContent(self, movieInfo):
        '''
        获取影片集内容
        '''
        pass

    @abstractmethod
    def getVideoList(self, seterId, setLink):
        '''
        获取影片集下的所有影片列表
        '''
        pass