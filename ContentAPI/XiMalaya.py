'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-25 23:06:09
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-26 00:12:50
FilePath: \OldFriend\ContentAPI\XiMalaya.py
Description: 喜马拉雅api实现
'''
import datetime
import requests
from urllib.parse import quote

class XiMalayaAlbum:
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
        pass

    def __processAlbumsDict(self, result: dict, vipOk: bool=False):
        albumsJsons: dict = result['data']['result']['response']['docs']
        if albumsJsons is None or len(albumsJsons) < 1:
            return None
        albums = []
        for albumsJson in albumsJsons:
            if vipOk and albumsJson['vipType'] == 1:
                continue
            albums.append(XiMalayaAlbum(albumsJson))
        return albums if len(albums) > 0 else None
            
    '''
    description: 
    param {str} keyword: 搜索关键词
    param {int} page: 页码(默认为1)
    param {int} rows: 每页数量(默认为20)
    return {dict}: 解析后的JSON结果
    '''
    def searchAlbums(self, keyword: str, page=1, rows=20, vipOk: bool=False):
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
        
        try:
            # 发送请求
            response = requests.get(
                base_url,
                params=params,
                headers=headers,
                timeout=10  # 10秒超时
            )
            # 状态检查
            response.raise_for_status()
            # 解析JSON
            return self.__processAlbumsDict(response.json())
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
    keyword = "科技"  # 替换你的关键词
    xAPI = XiMalaya()
    result = xAPI.searchAlbums(keyword)
    
    if result:
        print(result)
