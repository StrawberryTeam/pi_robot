# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Common.Straw import Straw
import getopt, sys
from Common.Util import Util

class Run(Straw):
    '''
    执行类
    '''
    _taskType = None # 当前待执行的任务类型 task / download / background / front
    _taskName = None # 当前待执行任务名 iqiyi / youku / download
    _process = None # 当前待执行的任务 getSetContent 若为空则执行默认方法
    _args = None # 当前任务的参数 tuple or dict
    _test = False # True 不执行写入操作，而是立即返回结果

    def __init__(self):
        super().__init__()
        Util.info('Run init')
        self.parseArgs()

        # 测试用
        self._taskType = 'download'
        self._taskName = ''
        self._process = 'dlFile'
        self._args = ''#{'videoId': '5c19fddde203c64bdc192997'}
        # 测试用 end

        # 根据传入参数拉起一个任务
        taskFactory = self.getFactory(self._taskType.capitalize())(self._taskName.capitalize(), isTest = self._test)
        # 拉起执行方法
        getattr(taskFactory, self._process)(self._args)


    def parseArgs(self):
        '''
        使用参数执行
        -d Download
        -t Test 不写入信息, 仅测试抓取并立即返回
        --download=NAME Download
        --task=TASKNAME Task
        --background=BGNAME Background
        OPTIONAL
        --process=PROCESSNAME 指定调用方法
        --params=PARAMS 指定方法的参数
        '''
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hdt:",["download=", 'task=', 'background=', 'process='])
            Util.info((opts, args))
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
                # 测试
                if opt == '-t':
                    self._test = True
        except getopt.GetoptError:
            print('Key -h see keymap.')
            sys.exit()
        finally:
            pass


Run()