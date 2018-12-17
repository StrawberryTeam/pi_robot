# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Common.Straw import Straw
import getopt, sys

class Run(Straw):
    '''
    执行类
    '''
    _taskType = None
    _taskName = None
    _process = None
    _args = None

    def __init__(self):
        super().__init__()
        print('Run init')
        self.parseArgs()

        # 测试用
        self._taskType = 'task'
        self._taskName = 'iqiyi'
        self._process = 'getCategoryList'
        self._args = None
        # 测试用 end

        # 根据传入参数拉起一个任务
        taskFactory = Straw.getFactory(self, self._taskType.capitalize())(self._taskName.capitalize())
        # 拉起执行方法
        getattr(taskFactory, self._process)(self._args)


    def parseArgs(self):
        '''
        使用参数执行
        -d Download
        --download=NAME Download
        --task=TASKNAME Task
        --background=BGNAME Background
        OPTIONAL
        --process=PROCESSNAME 指定调用方法
        --params=PARAMS 指定方法的参数
        '''
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hdtb:",["download=", 'task=', 'background=', 'process='])
            for opt, arg in opts:
                if opt == '-h':
                    print('Run.py')
                    print('Add a tasker')
                    print('     -d <download> --download=<download name>')
                    print('     --task=<task name>')
                    print('     --background=<background name>')
                    print('Optional add a process')
                    print('     --process=<process name>')
                    print('Optional add some process params')
                    print('     --params=<params>')
                    sys.exit()
                elif opt in ("-d", "--download"): 
                    self._taskType = 'download'
                    self._taskName = arg
                elif opt == "--task":
                    self._taskType = 'task'
                    self._taskName = arg
                elif opt == "--background":
                    self._taskType = 'background'
                    self._taskName = arg
                if opt == "--process":
                    self._process = arg
                if opt == "--params":
                    self._args = arg
        except getopt.GetoptError:
            print('Key -h see keymap.')
            sys.exit()
        finally:
            pass


Run()
