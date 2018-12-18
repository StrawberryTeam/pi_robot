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
        # "http://list.iqiyi.com/www/15/-------------11-%s-1-iqiyi--.html"
        # 动漫
        "http://list.iqiyi.com/www/4/-------------11-%s-1-iqiyi--.html",
        # # 儿歌
        # "http://list.iqiyi.com/www/15/---28983----------11-%s-1---.html",
        # # 故事
        # "http://list.iqiyi.com/www/15/---28984----------11-%s-1---.html",
        # # 英语
        # "http://list.iqiyi.com/www/15/---28985----------11-%s-1---.html"
    ]

    def getCategoryList(self, fLink):
        '''
        获取分类页数据 
        '''
        print('Task:Iqiyi getCategoryList')
        print("Do on Cate: {}".format(fLink))
        r = Util.getPage(fLink)
        # 获取分类页内容
        html = BeautifulSoup(r.text, 'html')
        # a = html.find('div', {'class': 'mod-page'})
        mainContent = html.find('ul', {'class': 'site-piclist site-piclist-180236 site-piclist-auto'})
        allLi = mainContent.find_all('li')
        cateData = []
        for li in allLi:
            try:
                imgEle = li.img
                c_title = imgEle['alt']
                c_img = imgEle['src']
                c_link = li.a['href']
                if li.find('div', {'class': 'role_info'}):
                    c_summary = li.find('div', {'class': 'role_info'}).text
                else:
                    c_summary = ''
                # 所有本分类本页下的内容
                cateData.append({
                    'title': c_title.strip(),
                    'link': c_link.strip(),
                    'img': c_img.strip(),
                    'summary': c_summary.strip()
                })
                del imgEle, c_title, c_img, c_link, c_summary
            except KeyError as msg:
                print("分类缺少必须参数跳过 {}".format(msg))
                continue

        del r, html, mainContent, allLi, fLink
        # 第一页数据
        if len(cateData) <= 0:
            print('Category empty')
            continue

        # 取第一页数据所有子页
        for movie in cateData:
            self.getSetContent(movie)
        del cateData

    _moviceListUrl = 'http://cache.video.iqiyi.com/jp/avlist/%s/%s/50/'

    def getSetContent(self, movie):
        '''
        获取分类页内容
        '''
        movieInfo = {}
        r = Util.getPage(movie['link'])
        html = BeautifulSoup(r.text, 'html')
        # print(html)
        # 是否是 vip 片
        movieInfo['is_vip'] = 1 if html.find_all('img', {'src': 'http://pic0.qiyipic.com/common/20171106/ac/1b/vip_100000_v_601_0_20.png'}) else 0 
        rcontent = html.find_all('div', {'class': 'right_col'})
        lcontent = html.find_all('div', {'class': 'left_col'})

        # 所有左侧数据
        for lc in lcontent:
            lc = lc.get_text()
            if "地区：" in lc:
                movieInfo['area'] = lc.replace('地区：', '').strip()
            if "语言：" in lc:
                movieInfo['lang'] = lc.replace('语言：', '').strip()
            if "总播放量：" in lc:
                movieInfo['allplaynum_txt'] = lc[lc.find('总播放量：') + 5:lc.find('次')].strip()
                movieInfo['allplaynum'] = Util.getRealPlayNum(movieInfo['allplaynum_txt'])
        for rc in rcontent:
            rc = rc.get_text()
            if '集数：' in rc:
                # 当前集数
                movieInfo['now_episode'] = rc.replace('集数：', '').strip()
                # 是否已完结
                movieInfo['episode_over'] = 1 if '全' in rc else 0
                break
            if '类型：' in rc:
                movieInfo['category'] = [x.strip() for x in rc.replace('类型：', '').strip().split('/')]

        # 本影片内容 set
        return dict(movieInfo, **movie)
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