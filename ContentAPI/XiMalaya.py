'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-25 23:06:09
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-26 15:21:56
FilePath: \OldFriend\ContentAPI\XiMalaya.py
Description: 喜马拉雅api实现
'''
import datetime
import time
import requests
from urllib.parse import quote

    
class XiMalayaTrackInfo:
    def __init__(self, trackJson: dict):
        self.title = trackJson['title']
        self.trackId = trackJson['trackId']
        self.trackRecordId = trackJson['trackRecordId']
        self.playUrl64 = trackJson['playUrl64']
        self.playUrl32 = trackJson['playUrl32']
        self.isPaid = trackJson['isPaid']
        self.isFree = trackJson['isFree']
        self.createTime = datetime.datetime.fromtimestamp(trackJson['createdAt'] / 1000.0).strftime(f"%Y-%m-%d")
    
    def __str__(self):
        res = '======title: ' + self.title + '======\r\n'
        res += 'trackId: ' + str(self.trackId) + '\r\n'
        res += 'playUrl64: ' + self.playUrl64 + '\r\n'
        res += 'isPaid: ' + str(self.isPaid) + '\r\n'
        res += 'isFree: ' + str(self.isFree) + '\r\n'
        res += 'createTime: ' + self.createTime + '\r\n'
        return res

    def __repr__(self):
        return str(self)

class XiMalayaAlbumInfo:
    def __init__(self, albumJson: dict):
        self.title = albumJson['title']
        self.customTitle = albumJson['custom_title'] if 'custom_title' in albumJson.keys() is not None else ''
        self.id = albumJson['id']
        self.intro = albumJson['intro']
        self.vip = albumJson['vipType']
        self.updateTime = datetime.datetime.fromtimestamp(albumJson['updated_at'] / 1000.0).strftime(f"%Y-%m-%d")
    
    def __str__(self):
        res = '======title: ' + self.title + '======\r\n'
        res += 'customTitle: ' + self.customTitle + '\r\n'
        res += 'id: ' + str(self.id) + '\r\n'
        res += 'intro: ' + self.intro + '\r\n'
        res += 'vip: ' + str(self.vip) + '\r\n'
        res += 'updateTime: ' + self.updateTime + '\r\n'
        return res

    def __repr__(self):
        return str(self)
        
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

    def _processTrackDict(self, result: dict):
        trackJsons: dict = result['list']
        if trackJsons is None or len(trackJsons) < 1:
            return None
        tracks = []
        for trackJson in trackJsons:
            tracks.append(XiMalayaTrackInfo(trackJson))
        return tracks if len(tracks) > 0 else None

        '''
    description: 
    param {str} keyword: 搜索关键词
    param {int} page: 页码(默认为1)
    param {int} rows: 每页数量(默认为20)
    return {dict}: 解析后的JSON结果
    '''
    def getPlaylist(self, albumId: int, page=1) -> list[XiMalayaTrackInfo]:
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
            return self._processTrackDict(response.json())
            
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

    def _processAlbumsDict(self, result: dict, vipOk: bool=False):
        albumsJsons: dict = result['data']['result']['response']['docs']
        if albumsJsons is None or len(albumsJsons) < 1:
            return None
        albums = []
        for albumsJson in albumsJsons:
            if vipOk and albumsJson['vipType'] >= 1:
                continue
            albums.append(XiMalayaAlbumInfo(albumsJson))
        return albums if len(albums) > 0 else None
            
    '''
    description: 
    param {str} keyword: 搜索关键词
    param {int} page: 页码(默认为1)
    param {int} rows: 每页数量(默认为20)
    return {dict}: 解析后的JSON结果
    '''
    def searchAlbums(self, keyword: str, page=1, rows=20, vipOk: bool=False) -> list[XiMalayaAlbumInfo]:
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
            return self._processAlbumsDict(response.json(), vipOk)
            # return response.json()
            
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

# 示例使用
if __name__ == "__main__":
    keyword = "新闻"  # 替换你的关键词
    xAPI = XiMalaya()
    result = xAPI.searchAlbums(keyword)
    playlist = xAPI.getPlaylist(result[2].id, 2)

    if result:
        print(playlist)
