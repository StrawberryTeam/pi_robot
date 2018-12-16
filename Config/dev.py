# -*- coding: utf-8 -*-
#!/usr/bin/python3

'''
    所有配置
'''
# 所有环境
UID = '2'

# 可用的分类
CATE_IDS = [
    1,  # iqiyi
    3,  # le
    6,  # youku
    9   # youtube
]

PROXY = {
    # 代理地址
    'proxyHost': "127.0.0.1",
    # 代理端口
    'proxyPort': 1080,
}

DB = {
    'mongoClient': 'mongodb://192.168.56.102:27017',
    'dbName': 'pi_2017'
}


TASK = {
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