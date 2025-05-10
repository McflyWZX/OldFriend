'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-09 22:02:01
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-05-08 23:32:39
FilePath: \OldFriend\SUI\Controls.py
Description: SUI模块内的具体控件实现模块
'''
from SoundManager import SoundManager
from TTS_manager import TTS_manager
from SUI.BaseControl import *
from ContentAPI.XiMalaya import *

DEFAULT_DESC = '这个内容没有介绍'

'''
description: 菜单，储存SoundContent或者子Menu
'''
class Menu(ItemList):
    def __init__(self, UI_mgr, title: str, desc: str="", father: Control=None, localMenu: list[Item]=[], ximalayaTag: str=None):
        super().__init__(UI_mgr, title)
        self.localMenu = localMenu
        self._setLocalMenuIndex()
        if ximalayaTag is None:
            self.xAlbumList = None
        else:
            self.xAlbumList = XiMalayaAlbumList(ximalayaTag, XiMalayaAlbumListType.SEARCH, UI_mgr.xAPI)
        self.ximalayaTag = ximalayaTag
        self.items = self._getLocalMenu()

    def _setLocalMenuIndex(self):
        i = 1
        for item in self.localMenu:
            item.setIndex(i)
            i += 1

    def _extendRemoteMenu(self):
        print('开始拓展列表')
        if self.xAlbumList is None:
            return
        newAlbumInfos = self.xAlbumList.getNextPage()
        if newAlbumInfos is None or len(newAlbumInfos) == 0:
            return
        startIndex = self.items[-1].index + 1 if len(self.items) > 0 else 1
        # 设置序号以播报时更能够了解自身位置
        i = startIndex
        for albumInfo in newAlbumInfos:
            albumControl = SoundAlbum(self.UI_mgr, albumInfo.title, albumInfo.id)
            if albumControl not in self._getLocalMenu():
                albumControl.setIndex(i)
                i += 1
                self.items.append(albumControl)
        print('获取到了%d个专辑'%(i - startIndex))
        
    def _getItems(self):
        if len(self.items) <= 0:
            self._extendRemoteMenu()
        return self.items

    def _getLocalMenu(self):
        return self.localMenu
    
    def _getNextItem(self):
        items = self._getItems()
        if len(items) <= 0:
            return None
        if self.visitIndex + 1 >= len(items):
            self._extendRemoteMenu()
        self.visitIndex += 1
        self.visitIndex = min(self.visitIndex, len(items) - 1)    # 防止意外
        return items[self.visitIndex]
    
    def _getLastItem(self):
        items = self._getItems()
        if len(items) <= 0:
            return None
        self.visitIndex -= 1
        self.visitIndex = max(0, self.visitIndex)
        return items[self.visitIndex]
    
    def _getRemoteMenu(self):
        res = []
        if self.ximalayaTag is None:
            return res
        self.remoteAlbum = self.UI_mgr.xAPI.searchAlbums(self.title)
        if self.remoteAlbum is None or len(self.remoteAlbum) == 0:
            return res
        for album in self.remoteAlbum:
            albumControl = SoundAlbum(self.UI_mgr, album.title, album.id)
            if albumControl not in self._getLocalMenu():
                res.append(albumControl)

        return res

'''
description: 声音集，包含具体的音源集ID，它
'''
class SoundAlbum(Item):
    def __init__(self, UI_mgr, title: str, ID:int, desc: str=""):
        super().__init__(UI_mgr, title)
        self.albumID = ID
        self.xAlbum = XiMalayaAlbum(ID, UI_mgr.xAPI)
        self.lastPlayIndex = 0
        self.playAt = 0
        self.inBug = False

    def onSelect(self):
        super().onSelect()
        print('ID：%s'%self.albumID)

    def onEnter(self):
        super().onEnter()
        xTrackInfo = self.xAlbum.getByIndex(self.lastPlayIndex)
        if xTrackInfo is None:
            self.UI_mgr.insAnnc('第%d集信息加载失败，从第一集重新播放'%self.lastPlayIndex, needBlock=True)
            print('第%d集信息加载失败，从第一集重新播放'%self.lastPlayIndex)
            self.lastPlayIndex = 0
            xTrackInfo = self.xAlbum.getByIndex(self.lastPlayIndex)
            if xTrackInfo is None:
                self.UI_mgr.insAnnc('第一集也加载失败', needBlock=True)
                print('第一集也加载失败')
                return -1
        self.sound = SoundContent(self.UI_mgr, xTrackInfo.title, xTrackInfo.trackId, xTrackInfo.playUrl64)
        # 暂停主声音的播放，防止播报完还在加载时又播放主声音
        self.UI_mgr.soundMgr.outterPause()
        # 这里会播报音频的标题，需要阻塞住，防止播报和主声音同时播放
        self.UI_mgr.insAnnc('共有%d集。'%self.xAlbum.totalCnt, needBlock=True)
        self.sound.onSelect(needBlock=True)
        print('进入了：%s'%self.title)
        self.UI_mgr.setAlbum(self)
        self.UI_mgr.playSound(url=self.sound.playUrl)

    def onTrackPlayFinish(self):
        self.onGoNext()

    def onGoNext(self):
        if self.lastPlayIndex >= self.xAlbum.totalCnt:
            self.UI_mgr.insAnnc('当前为第%d集，是最后一集了'%self.lastPlayIndex)
            self.UI_mgr.soundMgr.outterPause()
            return
        xTrackInfo = self.xAlbum.getByIndex(self.lastPlayIndex + 1)
        if xTrackInfo is None:
            self.UI_mgr.insAnnc('第%d集信息加载失败，已暂停'%self.lastPlayIndex, needBlock=True)
            print('第%d集信息加载失败，已暂停'%self.lastPlayIndex)
            return
        # 确定能往前再加1
        self.lastPlayIndex += 1
        self.sound = SoundContent(self.UI_mgr, xTrackInfo.title, xTrackInfo.trackId, xTrackInfo.playUrl64)
        # 暂停主声音的播放，防止播报完还在加载时又播放主声音
        self.UI_mgr.soundMgr.outterPause()
        # 这里会播报音频的标题，需要阻塞住，防止播报和主声音同时播放
        self.sound.onSelect(needBlock=True)
        self.UI_mgr.playSound(url=self.sound.playUrl)

    def onGoLast(self):
        self.lastPlayIndex -= 1
        if self.lastPlayIndex <= 0:
            self.lastPlayIndex = 0
        xTrackInfo = self.xAlbum.getByIndex(self.lastPlayIndex)
        if xTrackInfo is None:
            self.UI_mgr.insAnnc('第%d集信息加载失败，已暂停'%self.lastPlayIndex, needBlock=True)
            print('第%d集信息加载失败，已暂停'%self.lastPlayIndex)
            return
        self.sound = SoundContent(self.UI_mgr, xTrackInfo.title, xTrackInfo.trackId, xTrackInfo.playUrl64)
        # 暂停主声音的播放，防止播报完还在加载时又播放主声音
        self.UI_mgr.soundMgr.outterPause()
        # 这里会播报音频的标题，需要阻塞住，防止播报和主声音同时播放
        self.sound.onSelect(needBlock=True)
        self.UI_mgr.playSound(url=self.sound.playUrl)

    def __eq__(self:'SoundAlbum', other:'SoundAlbum'):
        return isinstance(other, SoundAlbum) and self.albumID == other.albumID

'''
description: 声音内容，包含具体的音源ID，当点击时替换主音乐并更新SoundAlbum状态
'''
class SoundContent(Item):
    def __init__(self, UI_mgr, title: str, ID:int, playUrl: str):
        super().__init__(UI_mgr, title)
        self.contentID = ID
        self.playRecord = 0
        self.playUrl = playUrl

    def onSelect(self, needBlock=False):
        print('开始播放：%s'%self.title)
        self.UI_mgr.insAnnc('开始播放——' + self.title, needBlock)

    def onEnter(self):
        pass