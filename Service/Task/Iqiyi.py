# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Protocol.TaskProtocol import TaskProtocol

class Iqiyi(TaskProtocol):
    '''
    爱奇艺内容
    '''

    def __init__(self):
        print('Init task iqiyi')

    def getCategoryList(self):
        print('iqiyi get category list')