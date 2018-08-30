# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from bs4 import BeautifulSoup
import requests
# import re
import json
# import you_get
import os,time
from common import common, db


class youku():
    '''
        优酷 http://list.youku.com/category/show/c_100_s_1_d_1_p_1.html?spm=a2h1n.8251845.0.0 动漫
    '''
    # 平台标识
    _platform = 6

    # 总分类链接
    _cateLink = [
        # 动漫
        # "http://list.youku.com/category/show/c_100_s_1_d_1_p_{}.html",
        # 儿童
        "http://list.youku.com/category/show/c_177_s_1_d_1_p_{}.html",
    ]

    # 分集链接
    _detailLink = "http://list.youku.com/show/id_{}.html"

    # 总分类最大取页数
    _cateMaxPage = 20

    # 分类开始页
    _cateStartPage = 1

    _dataSaver = {}
    _db = {}
    def __init__(self):
        self.initDb()

        # # 所有分类链接
        # for link in self._cateLink:
        #     self.getCateContent(link)

        # # for test
        # # self.getMovieCate({'link':'http://www.iqiyi.com/a_19rrhaw9hl.html#vfrm=2-4-0-1'})
        # print('Cate end')
    
    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True

    # 所有分片查询 地址
    _moviceListUrl = 'http://cache.video.iqiyi.com/jp/avlist/%s/%s/50/'
    # 获取电影分片
    def getMovieCate(self, movie):
        movieInfo = {}
        r = common.getPage(movie['link'])
        html = BeautifulSoup(r.text, 'lxml')
        # 分片页链接
        try:
            findLink = html.find("div", {"class": "player-title clearfix"}).find('a')
        except TypeError as msg:
            return False
        detailLink = findLink['href']
        del r, html, movie['link']
        if "http:" not in detailLink:
            detailLink = "http:{}".format(detailLink)
        # 换 link
        movieInfo['link'] = detailLink
        r = common.getPage(detailLink)
        html = BeautifulSoup(r.text, 'lxml')
        detailContent = html.find("div", {"class": "mod fix"})
        # 是否是 vip 片
        movieInfo['is_vip'] = 1 if detailContent.find_all('span', {'class': 'vip-free'}) else 0 
        movieInfo['summary'] = detailContent.find("span", {"class": "intro-more"}).text.strip() if detailContent.find("span", {"class": "intro-more"}) else ""
        ulContent = detailContent.find_all("li")

        findEpisode = detailContent.find("li", {"class": "p-row p-renew"})
        if not findEpisode:
            return False
        episodeHtml = findEpisode.text.strip()
        # 当前集数
        movieInfo['now_episode'] = episodeHtml.replace('集数：', '').strip()
        # 是否已完结
        movieInfo['episode_over'] = 1 if '全' in episodeHtml else 0
        for li in ulContent:
            liT = li.get_text()
            if "地区：" in liT:
                movieInfo['area'] = liT.replace('地区：', '').strip()
            movieInfo['lang'] = '默认'
            if "总播放数：" in liT:
                allplayNum = liT.replace('总播放数：', '').replace(',', '').strip()
                movieInfo['allplaynum_txt'] = common.getPlayNumTxt(allplayNum)
                movieInfo['allplaynum'] = int(allplayNum)
            if '类型：' in liT:
                movieInfo['category'] = [x.strip() for x in liT.replace('类型：', '').strip().split('/')]

        # 存集合 
        seterId = self._db.saveVideoSet(dict(movieInfo, **movie), self._platform)
        del movieInfo, movie, episodeHtml, ulContent
        # 该集合已经存在
        if False == seterId:
            print('该剧集已经存在')
            return False
        print("Do set {}".format(seterId))
        # get show id 
        rText = r.text
        showid = rText[rText.find('showid:"') + 8 : rText.find('",', rText.find('showid:"') + 8)]
        del rText
        # 分集有多少页
        sublist = []
        page = 0
        while True:
            # suburl = 'http://v.youku.com/page/playlist/pm_' + pm + '_vid_' + vid + '_showid_' + showid + '_page_' + str(i) + '?beta&callback=tuijsonp' + str(tuijsonp)
            #http://v.youku.com/page/playlist/pm_3_vid_808529812_showid_316817_page_1?beta&callback=tuijsonp14
            # @todo the video set list
            jq = "jQuery111204903571909754745_"
            jqtime = int(time.time())
            suburl = "http://list.youku.com/show/point?id={}&stage=reload_{}1&callback={}{}&_={}"
            subr = requests.get(suburl.format(showid, str(page), jq, jqtime, jqtime))
            # subs = subr.text
            rpTxt = 'window.{} && {}('.format(jq + str(jqtime), jq + str(jqtime))
            # print(rpTxt)
            subTxt = subr.text.replace(rpTxt, '')
            subs = json.loads(subTxt[:-2])

            if 'html' not in subs:
                #没有更多内容了
                print('This page is over {}'.format(movie['title']))
                break
            else:
                #翻页
                page = page + 1
            
            subHtml = BeautifulSoup(subs['html'], 'lxml')
            liList = subHtml.find_all('div', {'class': "p-item"})
            for li in liList:
                titleLink = li.find('a')
                if not titleLink:
                    continue
                # 查询单集是否存在
                movieExists = self._db.videoListExists(titleLink['title'], seterId)
                # 单集不存在 并且有数据的情况下写 videolist
                if True == movieExists:
                    print('单集 {} 已存在于 setId {}'.format(titleLink['title'], seterId))
                    continue
                try:
                    sublist.append({  
                        'name': titleLink['title'],
                        'link': 'http:' + titleLink['href'],
                        'summary': li.find('div', {"class": "item-intro c999"}).text if li.find('div', {"class": "item-intro c999"}) else "",
                        'img': li.find('img')['src'],
                        'setId': seterId,
                        "duration": li.find('span', {"class": 'p-time'}).text
                    })
                except KeyError as msg:
                    print("单集缺少参数 {}".format(msg))
                    continue
                except TypeError as msg:
                    print('分类参数不完整 {}'.format(msg))
                    continue
                # break # 测试单集 0-20 一条
            # break # 所有 0-20 21-30 第一页

        # 所有分集信息
        if len(sublist) > 0:
            # 更新总集数数据
            self._db.modifyEpisode({'episode': len(sublist)}, seterId)
            print('成功保存单集 {} 部'.format(len(sublist)))
            self._db.saveVideoList(sublist)
            return seterId
        else:
            print('setId: {} 没有找到任何单集，删除剧集'.format(seterId))
            # 如果 没有找到任何分集信息 删除该剧集
            self._db.rmSet(seterId)
        del sublist
        return False

    # link 正文内容链接 title 片名 summary 简介 img 封图
    # 总分类所有内容
    def getCateContent(self, link):
        # 先看该总分类有几页
        for page in range(self._cateStartPage, self._cateMaxPage + self._cateStartPage):
            print("Do page {}".format(page))
            fLink = link.format(page)
            print("Do on Cate: %s" % fLink)
            r = common.getPage(fLink)
            html = BeautifulSoup(r.text, 'lxml')
            # a = html.find('div', {'class': 'mod-page'})
            mainContent = html.find('div', {'class': 'box-series'})
            allLi = mainContent.find_all('li', {"class": "yk-col4 mr1"})
            try:
                cateData = []
                for li in allLi:
                    imgEle = li.img
                    c_title = li.a['title']
                    c_img = imgEle['src']
                    c_link = li.a['href']
                    if "http:" not in c_link:
                        c_link = "http:" + c_link
                    # 所有本分类本页下的内容
                    cateData.append({
                        'title': c_title.strip(),
                        'link': c_link.strip(),
                        'img': c_img.strip(),
                        # 'summary': c_summary.strip()
                    })
                    del imgEle, c_title, c_img, c_link
                    # break # 测试一条影片集
            except KeyError as msg:
                print('分类参数不完整 {}'.format(msg))
                continue
            except TypeError as msg:
                print('分类参数不完整 {}'.format(msg))
                continue

            del r, html, mainContent, allLi, fLink

            if len(cateData) <= 0:
                print('Category empty')
                continue

            for movie in cateData:
                self.getMovieCate(movie)

if __name__ == "__main__":
    y = youku()
    for link in y._cateLink:
        y.getCateContent(link)
    print('Cate end')
