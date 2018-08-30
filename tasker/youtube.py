# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os, sys
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from bs4 import BeautifulSoup
# import re
import json
# import you_get
import time
from common import common, db


class youtube():
    '''
        youtube playlist
        https://www.youtube.com/playlist?list=PLzAVL_ayaL5Q2zlwC3kluDjkYPyHKhTDg
    '''
    # 平台标识
    _platform = 9

    # 总分类链接
    # Youtube 账号登录后 添加到 播放列表 / 保存播放列表
    _cateLink = [
        #badanamu 1
        # 'https://www.youtube.com/playlist?list=PLzAVL_ayaL5Q2zlwC3kluDjkYPyHKhTDg'
        # 'https://www.youtube.com/playlist?list=PLzAVL_ayaL5TRvXjdA0eWUObHXGEC3Gum'
        'https://www.youtube.com/playlist?list=PLzAVL_ayaL5TRdMj9aqz9Mt6jcGRXC0vR'
    ]

    _playLink = "https://www.youtube.com/watch?v={}"

    # 总分类最大取页数
    _cateMaxPage = 20

    # 分类开始页
    _cateStartPage = 1

    _dataSaver = {}
    _db = {}
    def __init__(self):
        self.initDb()

        # for test
        # self.getMovie([{'link': 'https://www.youtube.com/watch?v=M1mgbt_C7EE', 'img': 'https://i.ytimg.com/vi/M1mgbt_C7EE/hqdefault.jpg', 'name': 'Little Butterfly'}], "5aa633cc12348741f8e9eb34")


    # 返回 db 对象
    def initDb(self):
        # 初始化 db
        if not self._db:
            self._db = db.db()
        return True


    # 获取电影分片
    def getMovie(self, subs, seterId):
        sublist = []
        for movie in subs:
            movieInfo = {}
            # r = getPage(movie['link'])
            # html = BeautifulSoup(r, 'lxml')
            # try:
            #     detailContent = html.find("div", {'id': "watch-description-clip"})
            #     movie['summary'] = detailContent.find("p", {'id': 'eow-description'}).text
            # except TypeError as msg:
            #     print("内容参数不完整 {}".format(msg))

            # 查询单集是否存在
            movieExists = self._db.videoListExists(movie['name'], seterId)
            # 单集不存在 并且有数据的情况下写 videolist
            if True == movieExists:
                print('单集 {} 已存在于 setId {}'.format(movie['name'], seterId))
                continue

            movie['summary'] = ''
            movie['setId'] = seterId;
            movie['non_py'] = True;
            sublist.append(movie)

        # 所有分集信息
        if len(sublist) > 0:
            listStatus = self._db.saveVideoList(sublist)
            if False == listStatus:
                print('setId: {} 所有单集保存失败, 删除剧集'.format(seterId))
                self._db.rmSet(seterId)
            else:
                # 更新总集数数据
                self._db.modifyEpisode({'episode': len(sublist)}, seterId)
                print('成功保存单集 {} 部'.format(len(sublist)))
                return seterId
        else:
            print('setId: {} 没有找到任何单集，删除剧集'.format(seterId))
            # 如果 没有找到任何分集信息 删除该剧集
            self._db.rmSet(seterId)

        return False

    # link 正文内容链接 title 片名 summary 简介 img 封图
    # 总分类所有内容
    def getCateContent(self, link):
        r = common.getPage(link, False, True)
        html = BeautifulSoup(r, 'lxml')
        # set 内容
        setContent = html.find("div", {"class": "branded-page-box clearfix"})
        setImg = setContent.img['src']
        try:
            cateData = {
                "link": link,
                "img": setImg[:setImg.find("?")],
                "title": setContent.h1.text.strip(),
                "summary": setContent.h1.text.strip(),
                "area": "Unknown",
                "is_vip": 0,
                "lang": "Default",
                "episode_over": 2, #一次性导入
                "non_py": True
            }
        except TypeError as msg:
            print('分类参数不完整 {}'.format(msg))
            return False
        # 附加信息
        ulContent = setContent.find("ul", {"class": "pl-header-details"})
        allLi = ulContent.find_all("li")
        for li in allLi:
            liT = li.get_text()
            if "videos" in liT:
                cateData['now_episode'] = liT.strip()
            if "views" in liT:
                try:
                    allplayNum = liT.replace('views', '').replace(',', '').strip()
                    cateData['allplaynum_txt'] = common.getPlayNumTxt(allplayNum)
                    cateData['allplaynum'] = int(allplayNum)
                except (IndexError):
                    pass

        # 存集合 
        seterId = self._db.saveVideoSet(cateData, self._platform)
        del allLi, ulContent, setContent, setImg
        # 该集合已经存在
        if False == seterId:
            print('该剧集已经存在')
            return False
        print("Do set {}".format(seterId))

        # 分集内容 部分
        mainContent = html.find("div", {'class': "pl-video-list"})
        allLi = mainContent.find_all("tr", {"class": "yt-uix-tile"})
        print("Find video num {}".format(len(allLi)))

        sublist = []
        for li in allLi:
            try:
                imgEle = li.find("img", {'width': '72'})
                c_img = imgEle['data-thumb']
                c_img = c_img[:c_img.find("?")] #使用完整图
                c_title = li['data-title']
                c_link = self._playLink.format(li['data-video-id'])
                # 所有本分类本页下的内容
                sublist.append({
                    'name': c_title.strip(),
                    'link': c_link.strip(),
                    'img': c_img.strip(),
                    # 'summary': c_summary.strip()
                })
                del imgEle, c_title, c_img, c_link
            except KeyError as msg:
                print('内容参数不完整 {}'.format(msg))
                continue
            except TypeError as msg:
                print('内容参数不完整 {}'.format(msg))
                continue

        del r, html, mainContent, allLi

        if len(sublist) <= 0:
            print("没有任何单集")
            return False

        # 补充更新 video info
        return self.getMovie(sublist, seterId)

if __name__ == "__main__":
    y = youtube()
    # 所有分类链接
    for link in y._cateLink:
        y.getCateContent(link)
    print('Cate end')
