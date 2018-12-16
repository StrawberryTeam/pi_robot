# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Common.Straw import Straw

class Run(Straw):
    '''
    执行类
    '''

    def __init__(self):
        super().__init__()
        config = Straw.getConfig(self)
        print('Run init')
        print(config.CATE_IDS)
        taskFactory = Straw.getFactory(self, 'Task')
        iqiyi = taskFactory('Iqiyi')
        iqiyi.getCategoryList()


Run()