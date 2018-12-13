# -*- coding: utf-8 -*-
#!/usr/bin/python3

'''
    所有配置
'''
# 所有环境
uid = '2'

# 可用的分类
cateIds = [
    1,  # iqiyi
    3,  # le
    6,  # youku
    9   # youtube
]

# 代理地址
proxy_host = "127.0.0.1"
# 代理端口
proxy_port = 1080

# 需要代理的 ids
proxyIds = [9]

# 需要下载图片的 ids
needImgIds = [1, 9]

# 使用 youtube-dl 下载
youtubeDls = [3]

mongo_client = 'mongodb://192.168.56.102:27017'
db = 'pi_2017'
# 图片下载目录
images_dir = 'files/images'
# you-get 目录
get_dir = 'you-get'
# 影片下载目录
file_dir = 'files'