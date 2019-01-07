# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
import json
import string
import random
import getopt
import time
import platform
import ctypes
import math
from Common.Straw import Straw
from Common.Util import Util


class ToWarehouse(Straw):
    '''
    创建仓库，并上传本地文件至远程仓库
    '''

    _config = {}
    def __init__(self):
        self._config = self.getConfig('WAREHOUSE')
        pass

    # 处理文件
    def process(self, args):
        pass

    # 创建本地仓库
    def createRepo(self):
        pass