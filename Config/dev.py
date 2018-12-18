# -*- coding: utf-8 -*-
#!/usr/bin/python3

'''
    所有配置
'''
# 所有环境
UID:str = '2'

# 可用的分类
CATE_IDS:list = [
    1,  # iqiyi
    3,  # le
    6,  # youku
    9   # youtube
]

PROXY:dict = {
    # 代理地址
    'proxyHost': "127.0.0.1",
    # 代理端口
    'proxyPort': 1080,
}

DB:dict = {
    'mongoClient': 'mongodb://192.168.56.102:27017',
    'dbName': 'pi_2017'
}


TASK:dict = {
    # 需要代理的 ids
    'proxyIds': [9],
    # 需要下载图片的 ids
    'needImgIds': [1, 9],
    # 图片下载目录
    'images_dir': 'files/images',
    # you-get 目录
    'youGet': 'you-get',
    'youTubeDl': 'youtube-dl',
    # 影片下载目录
    'fileDir': 'files'
}

# 休息时间段 7点 8点 ...
SLEEP:list = [7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22]