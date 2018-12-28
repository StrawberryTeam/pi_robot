# -*- coding: utf-8 -*-
#!/usr/bin/python3
from abc import ABCMeta, abstractmethod

class DownloadProtocol(metaclass=ABCMeta):
    '''
    下载 接口
    '''
    
    @abstractmethod
    def dlFile(self, args):
        '''
        开始下载过程
        '''
        pass
