# -*- coding: utf-8 -*-
#!/usr/bin/python3

from bs4 import BeautifulSoup
import requests
# import re
import json
# import you_get
import os
import dataSaver
import urllib



class fun():
    '''
    风行视频 http://www.fun.tv/retrieve/a-e585a8e983a8.c-e58aa8e6bcab.t-e5b091e584bf/
    @todo 风行只需要给第一集的下载地址，会自动下载全集
    '''
    # 平台标识
    _platform = 2

    # 总分类链接
    _cateLink = [
        # 少儿
        "http://www.fun.tv/retrieve/a-e585a8e983a8.c-e58aa8e6bcab.pg-%s.t-e5b091e584bf"
    ]

    # 总分类最大取页数
    _cateMaxPage = 10

    _funUrl = 'http://www.fun.tv'

    _dataSaver = {}
    def __init__(self):
        # 所有分类链接
        for link in self._cateLink:
            self.getCateContent(link)

        if len(self._cateData) <= 0:
            print('Category empty')
            exit()

        for movie in self._cateData:
            self.getMovieCate(movie)
        # self.getMovieCate({'summary': '猪小妹的探险惊喜', 'title': '粉红猪小妹', 'img': 'http://img.funshion.com/img/blank.gif', 'link': 'http://www.fun.tv/vplay/g-103332/'})
        print('Cate end')

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
        movieInfo = {}
        r = self.getPage(movie['link'])
        html = r.text
        # 是否是 vip 片
        movieInfo['is_vip'] = 0 
        start = "window.vplayInfo = "
        content = html[html.index(start) + len(start) : html.index('window.shareInfo = ')]
        content =  urllib.parse.unquote(content).strip()
        content = json.loads(content[:-1])
        del start, r, html
        # print(content)
        # 当前集数
        movieInfo['now_episode'] = '全集'
        # 是否已完结
        movieInfo['episode_over'] = 1
        # 存集合 
        seterId = dataSaver.saveVideoSet(dict(movieInfo, **movie), self._platform)
        # exit()
        # 该集合已经存在
        if False == seterId:
            print('该内容集合已经存在')
            return

        '''
        {
            "id": "232552",
            "name": "u7b2c1u96c6",
            "num": "1",
            "still": "http://img3.funshion.com/sdw?oid=f2af6ba082e36b6932b1445672bdab79&w=0&h=0",
            "duration": "4:59",
            "total_vv": "10277002",
            "isvip": "0",
            "isnew": "0",
            "isfee": "0",
            "videoid": "232552",
            "title": "1",
            "number": "1",
            "dtype": "normal",
            "desc": "u7b2c1u96c6",
            "current": 1,
            "url": "/vplay/g-103332.v-232552/",
            "play_index": 0,
            "playnum": 0,
            "pic": "http://img3.funshion.com/sdw?oid=f2af6ba082e36b6932b1445672bdab79&w=130&h=73",
            "special": 0
        }
        '''
        videoList = []
        # print(content)
        allNum = 0
        # 每一大段
        for videos in content['dvideos']:
            # 每集
            for video in videos['videos']:
                for v in video['lists']:
                    if v and 'name' in v and 'url' in v:
                        videoList.append({
                            'setId': seterId,
                            'name': movie['title'] + ' ' + v['name'],
                            'summary': v['desc'],
                            'link': self._funUrl + v['url'],
                            'img': v['pic'] if 'pic' in v else movie['img'],
                            'duration': v['duration']
                        })
                        allNum += 1
        # 更新总集数数据
        dataSaver.modifyEpisode({'episode': allNum}, seterId)
        # 所有分集信息
        if len(videoList) > 0:
            dataSaver.saveVideoList(videoList)
        del movieInfo, content, videoList, allNum


    # link 正文内容链接 title 片名 summary 简介 img 封图
    _cateData = []
    # 总分类所有内容
    def getCateContent(self, link):
        # 先看该总分类有几页
        for page in range(0, self._cateMaxPage):
            fLink = link % str(page + 1)
            print("Do on Cate: %s" % fLink)
            r = self.getPage(fLink)
            html = BeautifulSoup(r.text, 'lxml')
            # a = html.find('div', {'class': 'mod-page'})
            mainContent = html.find('div', {'class': 'mod-videos'})
            allLi = mainContent.find_all('div', {'class': 'mod-vd-i'})
            for li in allLi:
                imgEle = li.img
                c_title = imgEle['alt']
                c_img = imgEle['_lazysrc']
                c_link = li.a['href']
                c_summary = li.find('p', {'class': 'desc'}).text
                # 所有本分类本页下的内容
                self._cateData.append({
                    'title': c_title.strip(),
                    'link': self._funUrl + c_link.strip(),
                    'img': c_img.strip(),
                    'summary': c_summary.strip()
                })
                print(self._cateData)
                del imgEle, c_title, c_img, c_link, c_summary
            del r, html, mainContent, allLi, fLink



fun()