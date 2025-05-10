'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-25 23:06:09
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-05-08 23:57:03
FilePath: \OldFriend\ContentAPI\XiMalaya.py
Description: 喜马拉雅api实现
'''
import datetime
import time
import requests
from urllib.parse import quote
from enum import Enum
        
class XiMalaya:
    def __init__(self):
        self.opDelayTime = 0.5
        self.lastReqTime: dict[str, float] = {
            'searchAlbums': 0.0,
            'getPlaylist': 0.0
        }

    '''
    description: 此函数为防ban函数，人为制造一个连续操作延迟，防止被ban
    param {*} self
    param {str} opName: 操作函数的名字
    '''    
    def _waitForOpDelay(self, opName: str):
        if opName not in self.lastReqTime.keys():
            time.sleep(self.opDelayTime)
            self.lastReqTime[opName] = time.time()
            return
        lastOpTime = self.lastReqTime[opName]
        nowTime = time.time()
        while nowTime - lastOpTime < self.opDelayTime:
            time.sleep(0.05)
            nowTime = time.time()
        self.lastReqTime[opName] = nowTime

    '''
    description: 
    param {str} keyword: 搜索关键词
    param {int} page: 页码(默认为1)
    param {int} rows: 每页数量(默认为20)
    return {dict}: 解析后的JSON结果
    '''
    def getPlaylist(self, albumId: int, page=1) -> dict:
        # 基础URL
        base_url = "http://mobwsa.ximalaya.com/mobile/playlist/album/page"
        # 构建请求参数
        params = {
            "albumId": albumId,
            "pageId": page
        }
        
        # 必须的请求头（部分禁止API）
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.ximalaya.com/search/",
            "X-Requested-With": "XMLHttpRequest"
        }

        self._waitForOpDelay('getPlaylist')
        
        try:
            # 发送请求
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=1  # 10秒超时
            )
            # 状态检查
            response.raise_for_status()
            # 解析JSON
            # return self.__processAlbumsDict(response.json())
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e.response.status_code}")
            print(f"响应内容: {e.response.text[:200]}...")  # 显示部分错误内容
            return None
        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {str(e)}")
            return None
        except ValueError as e:
            print(f"JSON解析失败: {str(e)}")
            return None
            
    '''
    description: 
    param {str} keyword: 搜索关键词
    param {int} page: 页码(默认为1)
    param {int} rows: 每页数量(默认为20)
    return {dict}: 解析后的JSON结果
    '''
    def searchAlbums(self, keyword: str, page=1, rows=20):
        # 编码关键词
        encoded_kw = quote(keyword)
        # 基础URL
        base_url = "https://www.ximalaya.com/revision/search"
        # 构建请求参数
        params = {
            "core": "album",
            "kw": encoded_kw,
            "page": page,
            "spellchecker": "true",
            "rows": rows,
            "condition": "relation",
            "device": "iPhone"
        }
        
        # 必须的请求头（部分禁止API）
        headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://www.ximalaya.com/search/",
            "X-Requested-With": "XMLHttpRequest"
        }
        
        self._waitForOpDelay('searchAlbums')

        try:
            # 发送请求
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=1  # 10秒超时
            )
            # 状态检查
            response.raise_for_status()
            # 解析JSON
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP错误: {e.response.status_code}")
            print(f"响应内容: {e.response.text[:200]}...")  # 显示部分错误内容
            return None
        except requests.exceptions.RequestException as e:
            print(f"网络请求异常: {str(e)}")
            return None
        except ValueError as e:
            print(f"JSON解析失败: {str(e)}")
            return None

class XiMalayaAlbumInfo:
    def __init__(self, albumJson: dict, index: int=0):
        self.title = albumJson['title']
        self.customTitle = albumJson['custom_title'] if 'custom_title' in albumJson else ''
        self.id = albumJson['id']
        self.intro = albumJson['intro']
        self.vip = albumJson['vipType']
        self.updateTime = datetime.datetime.fromtimestamp(albumJson['updated_at'] / 1000.0).strftime(f"%Y-%m-%d")
        self.index = index
    
    def __str__(self):
        res = '======title: ' + self.title + '======\r\n'
        res += 'customTitle: ' + self.customTitle + '\r\n'
        res += 'index: ' + str(self.index) + '\r\n'
        res += 'id: ' + str(self.id) + '\r\n'
        res += 'intro: ' + self.intro + '\r\n'
        res += 'vip: ' + str(self.vip) + '\r\n'
        res += 'updateTime: ' + self.updateTime + '\r\n'
        return res

    def __repr__(self):
        return str(self)

class XiMalayaAlbumListType(Enum):
    SEARCH = 1
    CATGORY = 2

'''
description: 喜马拉雅专辑列表类，可以设置搜索或分类两种获取方式，不可以跳页
             这里是按页往下走
             原生page从1开始，内部从0开始，要处理一下
'''
class XiMalayaAlbumList:
    def __init__(self, keyword: str, listType: XiMalayaAlbumListType, xAPI: XiMalaya):
        self.keyword = keyword
        self.numsPerPage = 20
        self.totalPage = -1
        self.nowPage = 0
        # 用list来管理页面，可以逐步往后跳
        self.albums: list[list[XiMalayaAlbumInfo]] = []
        self.listType = listType
        if self.listType == XiMalayaAlbumListType.SEARCH:
            self.processDictFunc = self._processSearchDict
            self.getAlbumFunc = xAPI.searchAlbums
        else:
            # 当前其它方案还没给出，默认用搜索
            self.processDictFunc = self._processSearchDict
            self.getAlbumFunc = xAPI.searchAlbums

    '''
    description: 处理搜索得到的json数据
    param {int} page
    param {dict} result
    param {bool} vipOk
    return {*} None：获取失败
    return {*} List：获取到的信息列表
    '''
    def _processSearchDict(self, page: int, result: dict, vipOk: bool=False):
        if result is None:
            print(f"喜马拉雅API搜索返回None")
            return None
        self.totalPage: int = result.get('data', {}).get('result', {}).get('response', {}).get('totalPage', -1)
        if self.totalPage == -1:
            print(f"喜马拉雅API搜索结果totalPage获取失败")
            return None
        albumsJsons: dict = result.get('data', {}).get('result', {}).get('response', {}).get('docs')
        if not albumsJsons or len(albumsJsons) < 1:
            print(f"喜马拉雅API搜索结果为空")
            return None
        albums = []
        index = self.numsPerPage * page   # 从0开始
        for albumsJson in albumsJsons:
            index += 1
            if vipOk == False and (albumsJson['vipType'] >= 1 or albumsJson['is_paid'] == True):
                continue
            albums.append(XiMalayaAlbumInfo(albumsJson, index - 1))
        return albums if len(albums) > 0 else None
    
    '''
    description: 获取下一页内容，浏览时使用者屯着已经浏览过的内容，当需要更多内容时调用该函数
    param {int} page
    param {dict} result
    param {bool} vipOk
    return {*} None：获取失败
    return {*} List：获取到的信息列表
    '''    
    def getNextPage(self) -> list[XiMalayaAlbumInfo]:
        if self.nowPage < len(self.albums):
            return self.albums[self.nowPage]
        newPageJson = self.getAlbumFunc(self.keyword, self.nowPage + 1, self.numsPerPage)
        if newPageJson is None:
            return None
        newPage = self.processDictFunc(self.nowPage, newPageJson)
        self.albums.append(newPage)
        self.nowPage += 1
        return newPage
    
class XiMalayaTrackInfo:
    def __init__(self, trackJson: dict, index: int=0):
        self.title = trackJson['title']
        self.trackId = trackJson['trackId']
        self.trackRecordId = trackJson['trackRecordId']
        self.playUrl64 = trackJson['playUrl64']
        self.playUrl32 = trackJson['playUrl32']
        self.isPaid = trackJson['isPaid']
        self.isFree = trackJson['isFree']
        self.index = index
        self.createTime = datetime.datetime.fromtimestamp(trackJson['createdAt'] / 1000.0).strftime(f"%Y-%m-%d")
    
    def __str__(self):
        res = '======title: ' + self.title + '======\r\n'
        res += 'index: ' + str(self.index) + '\r\n'
        res += 'trackId: ' + str(self.trackId) + '\r\n'
        res += 'playUrl64: ' + self.playUrl64 + '\r\n'
        res += 'isPaid: ' + str(self.isPaid) + '\r\n'
        res += 'isFree: ' + str(self.isFree) + '\r\n'
        res += 'createTime: ' + self.createTime + '\r\n'
        return res

    def __repr__(self):
        return str(self)
    
'''
description: 喜马拉雅专辑类，外部可以按index获取album信息
'''
class XiMalayaAlbum:
    def __init__(self, albumID: int, xAPI: XiMalaya):
        self.albumID = albumID
        self.numsPerPage = 20
        self.totalPage = -1
        self.totalCnt = -1
        self.xAPI = xAPI
        # 用dict来管理页面，可以任意跳页
        self.tracks: dict[int, list[XiMalayaTrackInfo]] = {}

    '''
    description: 处理搜索得到的json数据
    param {int} page 页数
    param {dict} result xAPI getPlayList得到的结果
    return {*} None：获取失败
    return {*} List：获取到的信息列表
    '''
    def _processTrackDict(self, page: int, result: dict):
        if result is None:
            print(f"喜马拉雅API声音列表返回None")
            return []
        self.totalPage: int = result.get('maxPageId', -1)
        self.totalCnt: int = result.get('totalCount', -1)
        if self.totalPage <= 0 or self.totalCnt <= 0:
            print(f"喜马拉雅API搜索结果数据异常page:%d，cnt:%d"%(self.totalPage, self.totalCnt))
            return []
        trackJsons: dict = result.get('list', {})
        if not trackJsons or len(trackJsons) < 1:
            print(f"喜马拉雅API搜索计数正常但结果为空")
            return []
        tracks = []
        index = self.numsPerPage * (page - 1)   # index从0开始，page从1开始
        for trackJson in trackJsons:
            tracks.append(XiMalayaTrackInfo(trackJson, index))
            index += 1
        return tracks if len(tracks) > 0 else []
    
    '''
    description: 获取指定页内容
    param {int} page 指定页数
    return {*} None：获取失败
    return {*} List：获取到的信息列表
    '''    
    def _getPage(self, pageId: int=0) -> list[XiMalayaAlbumInfo]:
        # 如果该页存在且有内容，则直接返回
        if pageId in self.tracks and len(self.tracks[pageId]) > 0:
            return self.tracks[pageId]
        print('即将在线获取track列表')
        playListJson = self.xAPI.getPlaylist(self.albumID, pageId)
        tracks = self._processTrackDict(pageId, playListJson)
        print('track列表获取信息，页长度：%d、总数：%d、总页数：%d'%(len(tracks), self.totalCnt, self.totalPage))
        if self.totalCnt <= 0 or self.totalPage <= 0 or len(tracks) <= 0:
            return None
        self.tracks[pageId] = tracks
        return tracks
    
    '''
    description: 获取指定index内容
    param {int} page 指定index
    return {*} None：获取失败
    return {*} XiMalayaAlbumInfo：获取到的track信息
    '''  
    def getByIndex(self, trackIndex: int) -> XiMalayaTrackInfo:
        pageId = int(trackIndex / self.numsPerPage) + 1
        tracks = self._getPage(pageId)
        if trackIndex >= self.totalCnt:
            return None
        tmpIndex = trackIndex % self.numsPerPage
        if tmpIndex < len(tracks):
            return tracks[tmpIndex]
        else:
            return None

# 示例使用
if __name__ == "__main__":
    xAlbums = XiMalayaAlbumList('新闻', XiMalayaAlbumListType.SEARCH, XiMalaya())
    print(xAlbums.getNextPage())
    print(xAlbums.getNextPage())
    print(xAlbums.getNextPage())
    xAlbum = XiMalayaAlbum(51076156, XiMalaya())
    for i in range(73, 78):
        if i == 59:
            pass
        print(xAlbum.getByIndex(i))
