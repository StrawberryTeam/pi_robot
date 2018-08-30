# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
# from bs4 import BeautifulSoup
import requests
# import re
import json
# import you_get
import os
from common import common, db
import math


class le():
    '''
    # 3 乐视 http://list.le.com/listn/c5_t-1_a-1_y-1_vt-1_f511001_s1_lg-1_st-1_md_o9_d1_p.html
    '''
    # 平台标识
    _platform = 3

    # 总分类链接
    _cateLink = [
        # 全部
        "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={}&ph=420001&dt=1&cg=5&or=4&stt=1&s=1",
        # 6岁以下
        # "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={}&ph=420001&dt=1&cg=5&or=4&stt=1&ag=511001&s=1",
        # 6-12
        # "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={}&ph=420001&dt=1&cg=5&or=4&stt=1&ag=511002&s=1",
        # 12-18
        # "http://list.le.com/getLesoData?from=pc&src=1&stype=1&ps=30&pn={}&ph=420001&dt=1&cg=5&or=4&stt=1&ag=511003&s=1",
    ]

    # 集合页url
    # _leContentUrl = 'http://www.le.com/comic/%s.html'

    # 最终播放页 url
    _lePageUrl = 'http://d.api.m.le.com/detail/episode?callback=&pid=%s&platform=pc&page=%s&pagesize=50&type=1&_='

    # 播放 url "/vplay_2068458.html"
    _lePlayUrl = 'http://www.le.com/ptv/vplay/%s.html#vid=%s'

    # 总分类最大取页数 30一页
    _cateMaxPage = 20

    _cateStartPage = 1

    _dataSaver = {}
    _db = {}
    def __init__(self):
        self.initDb()
        # # 所有分类链接
        # for link in self._cateLink:
        #     self.getCateContent(link)

        # # self.getMovieCate({'aid': '94075', 'img': 'http://i0.letvimg.com/lc02_isvrs/201602/07/15/01/d60b3320-bad9-4912-a448-0151002f27da.jpg', 'title': '小猪佩奇 全集版', 'is_vip': 0, 'summary': '红猪小妹是一只非常可爱的小粉红猪，她与弟弟乔治、爸爸、妈妈快乐地住在一起。粉红猪小妹最喜欢做的事情是玩游戏，打扮的漂漂亮亮，渡假，以及住在小泥坑里快乐的跳上跳下!除了这些，她还喜欢到处探险，虽然有些时候会遇到一些小状况，但总可以化险为夷，而且都会带给大家意外的惊喜!!', 'episode': '156'})
        # print('Cate end')
    
    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

    # get 方式获取
    def getPage(self, link, isJson = False):
        res = requests.get(link)
        try:
            res.raise_for_status()
        except res.exceptions.HTTPError as e:
            # Whoops it wasn't a 200
            return "Error: " + str(e)
        if True == isJson:
            res = res.json()
        return res

    # post 方式获取
    def postPage(self, link, data = {}):
        return requests.post(link, data=data)

    # 所有分片查询 地址
    _moviceListUrl = 'http://cache.video.iqiyi.com/jp/avlist/%s/%s/50/'
    # 获取电影分片
    def getMovieCate(self, movie):
        # 存集合 
        seterId = self._db.saveVideoSet(movie, self._platform)
        # exit()
        # 该集合已经存在
        if False == seterId:
            print('该剧集已经存在')
            return
        print("Do {}".format(seterId))
        # 每页50个
        # maxPage = math.floor(movie['episode'] / 50)
        # 所有视频列表
        videoList = []
        page = 1
        while True:
        # for page in range(0, maxPage):
            print(self._lePageUrl % (movie['aid'], str(page)))
            r = self.getPage(self._lePageUrl % (movie['aid'], str(page)), True)
            # 没有更多了
            if 'data' not in r or len(r['data']['list']) <= 0:
                print('This page is over {}'.format(movie['title']))
                break
            else:
                page = page + 1

            '''
            {
                "cid": 5,
                "vid": 2068458,
                "url": "/vplay_2068458.html",
                "pid": 92063,
                "title": "字母歌-贝瓦儿歌",
                "sub_title": "字母歌",
                "pic": "http://i2.letvimg.com/lc_yunzhuanma/201501/13/197ea1b06933051a292bc6fa525e7f2e_2934250/thumb/2_400_225.jpg",
                "duration": 79,
                "description": "贝瓦儿歌集儿童歌谣、经典儿歌、三字经、古诗为一体的儿歌汇合，具有动画精美、节奏欢快、语言简单、易学易懂等特点，深受广大小朋友和家长的喜爱。",
                "video_type": {
                    "180001": "正片"
                },
                "episode": "1",
                "guest": null,
                "ispay": 0,
                "isyugao": 0
            }
            '''
            cateData = r['data']['list']
            for data in cateData:
                # 查询单集是否存在
                movieExists = self._db.videoListExists(data['title'], seterId)
                # 单集不存在 并且有数据的情况下写 videolist
                if True == movieExists:
                    print('单集 {} 已存在于 setId {}'.format(data['title'], seterId))
                    continue
                try:
                    videoList.append({
                        'setId': seterId,
                        'name': data['title'],
                        'summary': data['description'],
                        'link': self._lePlayUrl % (data['vid'], data['vid']),
                        'img': data['pic'],
                        'duration': '%02d:%02d' % (data['duration'] // 60,data['duration']  % 60)
                    })
                except KeyError as msg:
                    print('单集 {} 缺少必要参数跳过 {}'.format(data['title'], msg))
                    continue
        # 所有分集信息
        if len(videoList) > 0:
            print('成功保存单集 {} 部'.format(len(videoList)))
            self._db.saveVideoList(videoList)
        else:
            print('setId: {} 没有找到任何单集，删除剧集'.format(seterId))
            self._db.rmSet(seterId)


    # link 正文内容链接 title 片名 summary 简介 img 封图
    # 总分类所有内容
    def getCateContent(self, link):
        # 先看该总分类有几页
        for page in range(self._cateStartPage, self._cateStartPage + self._cateMaxPage):
            fLink = link.format(page)
            print("Do on Cate: %s" % fLink)
            r = self.getPage(fLink, True)
            if 'data' not in r or 'arr' not in r['data'] or len(r['data']['arr']) <= 0:
                print('该页无内容')
                continue
            cateData = []
            for li in r['data']['arr']:
                try:
                    now_episode = li['nowEpisodes'] if 'nowEpisodes' in li else 1
                    all_episode = li['episodes'] if 'episodes' in li else 0
                    categoryList = li['subCategoryName'].split(',')
                    # 所有本分类本页下的内容
                    cateData.append({
                        'title': li['name'],
                        'aid': li['aid'],
                        'img': li['images']['300*400'] if '300*400' in li['images'] else li['images']['320*200'],
                        'bg_img': li['images']['1440*810'] if '1440*810' in li['images'] else '',
                        'summary': li['description'],
                        'is_vip': 0, # 乐视取消了 vip @2018.3 #if li['vipCount'] == 'null' else 1,
                        'lang': '默认', #li['lgName'],
                        'area': li['areaName'],
                        'allplaynum': li['playCount'],
                        'allplaynum_txt': common.getPlayNumTxt(li['playCount']),
                        'category': categoryList.append(li['categoryName']),
                        'episode_over': int(li['isEnd']), #1 if all_episode >= now_episode else 0, # 是否完结
                        'now_episode': '更新至%s集/共%s集' % (now_episode, all_episode),
                        'episode': int(now_episode)
                    })
                    # break # 测试一条记录
                except KeyError as msg:
                    print("分类缺少必须参数跳过 {}".format(msg))
                    continue

            del r, fLink

            # 当前页所有子内容
            if len(cateData) <= 0:
                print('Category empty')
                continue

            for movie in cateData:
                self.getMovieCate(movie)
            del cateData



if __name__ == "__main__":
    l = le()
    for link in l._cateLink:
        l.getCateContent(link)
    print('Cate end')
