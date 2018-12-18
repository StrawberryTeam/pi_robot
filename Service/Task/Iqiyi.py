# -*- coding: utf-8 -*-
#!/usr/bin/python3
from Protocol.TaskProtocol import TaskProtocol
from Common.Util import Util
from bs4 import BeautifulSoup


class Iqiyi(TaskProtocol):
    '''
    爱奇艺内容
    '''

    def __init__(self):
        print('Init Task Iqiyi')


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
        r = Util.getPage(fLink)
        # 获取分类页内容
        html = BeautifulSoup(r.text, 'html5lib')
        # a = html.find('div', {'class': 'mod-page'})
        mainContent = html.find('ul', {'class': 'site-piclist site-piclist-180236 site-piclist-auto'})
        allLi = mainContent.find_all('li')
        cateData = []
        for li in allLi:
            try:
                # imgEle = li.img
                # c_title = imgEle['alt']
                # c_img = imgEle['src']
                c_link = li.a['href']
                # if li.find('div', {'class': 'role_info'}):
                #     c_summary = li.find('div', {'class': 'role_info'}).text
                # else:
                #     c_summary = ''
                # 所有本分类本页下的内容
                # cateData.append({
                #     'title': c_title.strip(),
                #     'link': c_link.strip(),
                #     'img': c_img.strip(),
                #     'summary': c_summary.strip()
                # })
                cateData.append(c_link.strip())
                del c_link
            except KeyError as msg:
                Util.info("分类缺少必须参数跳过 {}".format(msg))
                continue

        del r, html, mainContent, allLi, fLink

        # 每取一页处理一页
        return cateData


    _moviceListUrl = 'http://cache.video.iqiyi.com/jp/avlist/%s/%s/50/'

    def getSetContent(self, link):
        '''
        获取本影片集信息
        '''
        movieInfo = {}
        r = Util.getPage(link)
        html = BeautifulSoup(r.text, 'html5lib')
        # print(html)
        # 是否是 vip 片
        movieInfo['link'] = link # 原始链接
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

        #     # if "总播放量：" in lc:
        #     #     movieInfo['allplaynum_txt'] = lc[lc.find('总播放量：') + 5:lc.find('次')].strip()
        #     #     movieInfo['allplaynum'] = Util.getRealPlayNum(movieInfo['allplaynum_txt'])
        # 本影片内容 set
        return movieInfo
        # 存集合 
        seterId = self._db.saveVideoSet(dict(movieInfo, **movie), self._platform)
        # exit()
        # 该集合已经存在
        if False == seterId:
            print('该剧集已经存在')
            return
        print("Do set {}".format(seterId))
        # max page
        pageHtml = html.find_all('a', {'data-delegate': 'albumlist-page'})
        maxPage = 1
        if pageHtml:
            lastPage = pageHtml[-1]
            maxPage = lastPage['data-avlist-page'] if lastPage['data-avlist-page'] else 1
            del lastPage
        # album
        albumHtml = r.text
        try:
            albumId = albumHtml[albumHtml.index("albumId:") + 8 : albumHtml.index("tvId:")]
        except ValueError as identifier:
            return False
        # albumHtml = html.gethtml.get_text().index("albumId:")html.get_text().index(",tvId:")
        albumId = albumId.replace(',', '').strip()
        del r, html, lcontent, rcontent, pageHtml, albumHtml, movieInfo, movie
        # 通过 json 获取所有集数
        # @todo 当片子更新时反向推送

        # 所有视频列表
        videoList = []
        for page in range(0, int(maxPage)):
            url = self._moviceListUrl % (str(albumId), str(page + 1))
            print(url)
            r = self.getPage(url)
            # 变为 json
            r = json.loads(r.text.replace('var tvInfoJs=', ''))
            # print(r)
            if not r or 'data' not in r:
                print('This page is empty %s' % url)
                continue
            # 所有内容
            """
            {'mdown': 0, 'vn': '汪汪队立大功全集 第1集', 'vpic': 'http://pic4.qiyipic.com/image/20170923/55/5b/v_111715119_m_601_m1.jpg', 'lgh': [], 'vurl': 'http://www.iqiyi.com/v_19rralnqpo.html', 'purType': 0, 'payMark': 0, 'id': 608736400, 'plcdown': {'17': 0, '15': 0}, 'desc': '精通科技的10岁男孩Ryder在拯救了6条小狗之后，将他们训练成了一组本领高强的狗狗巡逻队。每个小狗都性格鲜明，也各有特长。斑点狗Marshall擅长火中急救；斗牛犬Rubble精通工程机械；牧羊犬Chase是个超级特工；混血儿Rocky是个维修能手；拉布拉多犬Zuma最熟悉水中救援；而可卡颇犬Skye掌握着各种航空技术。拥有这么多解决问题的能力，在加上Ryder提供的炫酷装备支持，不管遇到多么困难和危险的救援任务，他们还总是忘不了相互玩闹，制作轻松的气氛，而每次幽默乐观的狗狗能总能顺利完成任务。', 'pds': '1', 'vt': '海上救援', 'shortTitle': '汪汪队立大功全集 第1集', 'isProduced': 0, 'pd': 1, 'tvQipuId': 608736400, 'type': '1', 'vid': 'e50a9d800b84f5bc42b0b87a82df5dac', 'exclusive': 0, 'videoFocuses': [], 'publishTime': 1485254688000, 'timeLength': 660, 'wmarkPos': 0}
            """
            # 更新总集数数据
            if page == 0:
                self._db.modifyEpisode({'episode': r['data']['allNum'] if r['data']['allNum'] else 1}, seterId)
            cateData = r['data']['vlist']
            for data in cateData:
                # 查询单集是否存在
                movieExists = self._db.videoListExists(data['vn'], seterId)
                # 单集不存在 并且有数据的情况下写 videolist
                if True == movieExists:
                    print('单集 {} 已存在于 setId {}'.format(data['vn'], seterId))
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
            print('成功保存单集 {} 部'.format(len(videoList)))
            self._db.saveVideoList(videoList)
        else:
            print('setId: {} 没有找到任何单集，删除剧集'.format(seterId))
            # 如果 没有找到任何分集信息 删除该剧集
            self._db.rmSet(seterId)

    def getVideoList(self, link, startPage = 1, endPage = None):
        pass