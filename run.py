# -*- coding: utf-8 -*-
#!/usr/bin/python3

'''
    拉起 tasker 各类目
'''
from common import common, db, config
from tasker import iqiyi, le, youku, youtube

# 执行 Youtube 任务
class runYoutube():

    def __init__(self, taskInfo):
        taskCls = youtube.youtube()

        # 拉取影片集信息
        if 'addset' == taskInfo['type']:
            setId = taskCls.getCateContent(taskInfo['link'])

        if False == setId:
            print('影片集数据拉取失败')
            exit()

        # 完成
        task2Dl(setId, taskInfo['toDevice'])
    
# 执行 youku
# class runYouku():

#     def __init__(self, taskInfo):
#         taskCls = youku.youku()

#         # 拉取影片集信息
#         if 'addset' == taskInfo['type']:
#             setId = taskCls.getMovieCate(taskInfo['link'])

#         if False == setId:
#             print('影片集数据拉取失败, 任务执行失败')
#             exit()
#         else:
#             # 完成
#             task2Dl(setId, taskInfo['toDevice'])

# 完成下载后调用 已标记为本平台下载
class task2Dl():

    def __init__(self, setId, deviceId):
        # 标记为下载中
        taskDb.set2Dl(setId, deviceId)
        print('任务执行成功')
        # 任务成功执行
        taskDb.taskSuccess(taskInfo['_id'])


# 是否在允许执行时间段内 
common.canISleep()

# 有哪些需要执行的任务
taskType = [
    'addset', # 添加影片集
    #'addvideo', # 添加影片
    'transfer', # 传送影片
    'receive', # 接收影片
]

# 获取一个可用任务
taskDb = db.db()
taskInfo = taskDb.getTask(taskType, config.uid)
if False == taskInfo:
    print("没有可执行的任务, 任务列表: {}".format(taskType))
    exit()

print('当前任务 {}'.format(taskInfo))
# 有可执行的任务，先标记为已完成，避免任务无法执行无限循环该任务
taskDb.taskDoing(taskInfo['_id'])

# youku 需要从总分类抓取 @todo 后面分离出来
# # youku run
# if 6 == taskInfo['platform']:
#     runYouku(taskInfo)
#     exit()

# youtube run
if 9 == taskInfo['platform']:
    runYoutube(taskInfo)
    exit()