# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Protocol.TaskProtocol import TaskProtocol
from Common.Util import Util
from bs4 import BeautifulSoup
from Common.Straw import Straw
import json

class Iqiyi(TaskProtocol, Straw):
    '''
    爱奇艺内容
    '''

    # 平台 id
    platform = 1

    _isProxy = False

    def __init__(self):
        print('Init Task Iqiyi')
        self._isProxy = True if self.platform in self.getConfig("PROXY_IDS") else False


    # 总分类链接
    cateLinks = [
        # 儿童
        # "http://list.iqiyi.com/www/15/-------------11-{}-1-iqiyi--.html"
        # 动漫
        "http://list.iqiyi.com/www/4/-------------11-{}-1-iqiyi--.html",
        # # 儿歌
        # "http://list.iqiyi.com/www/15/---28983----------11-{}-1---.html",
        # # 故事
        # "http://list.iqiyi.com/www/15/---28984----------11-{}-1---.html",
        # # 英语
        # "http://list.iqiyi.com/www/15/---28985----------11-{}-1---.html"
    ]

    def getCategoryList(self, fLink):
        '''
        获取分类页数据 
        '''
        Util.info('Task:Iqiyi getCategoryList')
        Util.info("Do on Cate: {}".format(fLink))
        r = Util.getPage(fLink, proxy=self._isProxy)
        # 获取分类页内容
        html = BeautifulSoup(r.text, self.getConfig('FETCH_LIBRARY'))
        # a = html.find('div', {'class': 'mod-page'})
        mainContent = html.find('ul', {'class': 'site-piclist site-piclist-180236 site-piclist-auto'})
        allLi = mainContent.find_all('li')
        cateData = []
        for li in allLi:
            try:
                # 其他信息去除，都从获取影片集信息中获得
                c_link = li.a['href']
                cateData.append(c_link.strip())
                del c_link
            except KeyError:
                Util.info("未找到影片集链接跳过")
                continue

        del r, html, mainContent, allLi, fLink

        # 每取一页处理一页
        return cateData


    _moviceListUrl = 'http://cache.video.iqiyi.com/jp/avlist/{}/{}/50/'

    _scoreUrl = 'http://pcw-api.iqiyi.com/video/score/getsnsscore?qipu_ids={}&tvid={}&pageNo=1&callback=window.Q.__callbacks__.cbtr3be1'
    def getSetScore(self, tvid, qipu_ids):
        '''
        获取影片集评分
        '''
        try:
            res = Util.getPage(self._scoreUrl.format(qipu_ids, tvid), proxy=self._isProxy)
            resText = res.text
            startTxt = '"sns_score":'
            resStart = resText.find(startTxt)
            resText = resText[resStart + len(startTxt):resText.find("}]});")]
            return resText
        except KeyError:
            return 0
        

    def getSetContent(self, link):
        '''
        获取本影片集信息
        '''
        movieInfo = {}
        r = Util.getPage(link, proxy=self._isProxy)
        html = BeautifulSoup(r.text, self.getConfig('FETCH_LIBRARY'))
        # print(html)
        movieInfo['link'] = link # 原始链接
        # 是否是 vip 片
        movieInfo['is_vip'] = 1 if html.find_all('img', {'class': 'icon-viedo-mr'}) else 0 
        movieInfo['title'] = html.find('a', {'class': 'info-intro-title'}).text
        # summary 如果有完整的取完整的
        summaryList = html.find_all('span', {'class': "briefIntroTxt"})
        movieInfo['summary'] = summaryList[-1].text
        movieInfo['img'] = html.find('div', {'class': 'info-img'}).img['src'] # 小图
        movieInfo['img_large'] = movieInfo['img'].replace('195_260', '480_360') # 大图
        try:
            movieInfo['area'] = html.find("p", {'class': "episodeIntro-area"}).a.text
        except AttributeError:
            pass
        try:
            movieInfo['lang'] = html.find('p', {'class': 'episodeIntro-lang'}).a.text
        except AttributeError:
            pass
        try:
            movieInfo['category'] = [x.text for x in html.find('p', {'class': "episodeIntro-type"}).find_all('a')]
        except AttributeError:
            pass

        try:
            movieInfo['hot'] = html.find("span", {"class": "heat-info"}).text.replace('热度', '').strip()
        except AttributeError:
            pass
        
        # 获取影片集评分
        tvid = html.find("span", {'class': "effect-score"})['data-score-tvid']
        movieInfo['score'] = self.getSetScore(tvid, tvid)

        # 统一单次导入
        movieInfo['episode_over'] = 2

        # 影片集本平台不重复添加
        setExists = self.getModel('VideoSet').exists(movieInfo['title'], self.platform)

        if True == setExists:
            Util.info('Set exists {}'.format(movieInfo['title']))
            return False

        # 保存set
        seterId = self.getModel('VideoSet').newSet(movieInfo, self.platform)

        return seterId

    # 获取这个影片集下所有影片内容
    def getVideoList(self, seterId, setLink):
        r = Util.getPage(setLink, proxy=self._isProxy)
        html = BeautifulSoup(r.text, self.getConfig('FETCH_LIBRARY'))
        # 处理 影片集下的所有影片列表
        # album
        albumHtml = r.text
        try:
            albumId = albumHtml[albumHtml.index("albumId:") + 8 : albumHtml.index("tvId:")]
        except ValueError:
            return False
        # albumHtml = html.gethtml.get_text().index("albumId:")html.get_text().index(",tvId:")
        albumId = albumId.replace(',', '').replace("\"", "").strip()
        del r, html
        # 通过 json 获取所有集数

        # 所有视频列表
        videoList = []
        page = 0
        while True:
            page = page + 1
            url = self._moviceListUrl.format(str(albumId), str(page))
            Util.info("Set video list : {}".format(url))
            r = Util.getPage(url, proxy=self._isProxy)
            # 变为 json
            r = json.loads(r.text.replace('var tvInfoJs=', ''))

            if not r or 'data' not in r:
                Util.info('Video is empty {}'.format(url))
                continue
            # 所有内容
            """
            {'mdown': 0, 'vn': '汪汪队立大功全集 第1集', 'vpic': 'http://pic4.qiyipic.com/image/20170923/55/5b/v_111715119_m_601_m1.jpg', 'lgh': [], 'vurl': 'http://www.iqiyi.com/v_19rralnqpo.html', 'purType': 0, 'payMark': 0, 'id': 608736400, 'plcdown': {'17': 0, '15': 0}, 'desc': '精通科技的10岁男孩Ryder在拯救了6条小狗之后，将他们训练成了一组本领高强的狗狗巡逻队。每个小狗都性格鲜明，也各有特长。斑点狗Marshall擅长火中急救；斗牛犬Rubble精通工程机械；牧羊犬Chase是个超级特工；混血儿Rocky是个维修能手；拉布拉多犬Zuma最熟悉水中救援；而可卡颇犬Skye掌握着各种航空技术。拥有这么多解决问题的能力，在加上Ryder提供的炫酷装备支持，不管遇到多么困难和危险的救援任务，他们还总是忘不了相互玩闹，制作轻松的气氛，而每次幽默乐观的狗狗能总能顺利完成任务。', 'pds': '1', 'vt': '海上救援', 'shortTitle': '汪汪队立大功全集 第1集', 'isProduced': 0, 'pd': 1, 'tvQipuId': 608736400, 'type': '1', 'vid': 'e50a9d800b84f5bc42b0b87a82df5dac', 'exclusive': 0, 'videoFocuses': [], 'publishTime': 1485254688000, 'timeLength': 660, 'wmarkPos': 0}
            """
            if 0 == r['data']['pn']:
                break
            # 更新总集数数据
            if page == 1:
                self.getModel('VideoSet').modifyEpisode({'episode': r['data']['allNum'] if r['data']['allNum'] else 1}, seterId)
            cateData = r['data']['vlist']
            for data in cateData:
                # 查询单集是否存在
                movieExists = self.getModel("VideoList").exists(data['vn'], seterId)
                # 单集不存在 并且有数据的情况下写 videolist
                if True == movieExists:
                    Util.info('单集 {} 已存在于 setId {}'.format(data['vn'], seterId))
                    continue

                if 'vurl' in data and 'vn' in data:
                    videoList.append({
                        'setId': seterId,
                        'name': data['vn'],
                        'summary': data['desc'],
                        'link': data['vurl'],
                        'img': data['vpic'],
                        'duration': '%02d:%02d' % (data['timeLength'] // 60,data['timeLength']  % 60),
                        'created_at': int(data['publishTime'])
                    })


        # 所有分集信息
        if len(videoList) > 0:
            self.getModel("VideoList").newList(videoList)
            Util.info('成功保存单集 {} 部'.format(len(videoList)))
        else:
            Util.info('setId: {} 没有找到任何影片，删除影片集'.format(seterId))
            # 如果 没有找到任何分集信息 删除该剧集
            self.getModel("VideoSet").remove(seterId)

        return True