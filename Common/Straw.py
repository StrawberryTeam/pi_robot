# -*- coding: utf-8 -*-
#!/usr/bin/python3

import importlib
class Straw():
    '''
    核心类
    '''
    
    env = 'dev' # 默认生产环境
    def __init__(self):
        try:
            from Config import Config
            self.env = Config.APP_ENV
        except ImportError:
            pass

    # 获取配置
    def getConfig(self, node = None):
        config = importlib.import_module('.{}'.format(self.env), 'Config')
        if node is not None:
            try:
                return getattr(config, node)
            except TypeError:
                print('Config node {} not found.'.format(node))
                return
        else:
            return config

    # 获取一个 model
    def getModel(self, model):
        try:
            modelObj = importlib.import_module('.{}'.format(model), 'Model')
            modelName = model.split('.')[-1] if model.split('.') else model # get service fun name
            return getattr(modelObj, modelName)
        except ImportError:
            print("No model found {}.".format(model))
            return

    # 获得一个 service
    def getService(self, service):
        try:
            serviceObj = importlib.import_module('.{}'.format(service), 'Service')
            serviceName = service.split('.')[-1] if service.split('.') else service # get service fun name
            return getattr(serviceObj, serviceName)
        except ImportError:
            print("No service found {}.".format(service))
            return

    # 获得一个工厂类
    def getFactory(self, factory):
        try:
            factoryObj = importlib.import_module('.{}'.format(factory), 'Factory')
            return getattr(factoryObj, factory)
        except ImportError:
            print("No factory found {}.".format(factory))
            return