# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Common.Straw import Straw
import getopt, sys

class Run(Straw):
    '''
    执行类
    '''
    _taskType = None
    _args = None

    def __init__(self):
        super().__init__()
        print('Run init')
        self.parseArgs()
        # config = Straw.getConfig(self)
        # print(config.CATE_IDS)
        # taskFactory = Straw.getFactory(self, 'Task')('Iqiyi')
        # taskFactory.getCategoryList()

    def parseArgs(self):
        '''
        使用参数执行
        -d Download
        --download=NAME Download
        --task=TASKNAME Task
        --background=BGNAME Background
        '''
        try:
            opts, args = getopt.getopt(sys.argv[1:],"hdtb:",["download=", 'task=', 'background='])
            for opt, arg in opts:
                if opt == '-h':
                    print('Run.py -d <download>')
                    sys.exit()
                elif opt in ("-d", "--download"): 
                    print('Download')
                    print(arg)
                    pass
                elif opt in ("--task"):
                    print("Task")
                    print(arg)
                    pass
                elif opt in ("--background"):
                    print("Background")
                    pass
        except getopt.GetoptError:
            print('Key -h see keymap.')
            sys.exit()
        finally:
            pass


Run()
