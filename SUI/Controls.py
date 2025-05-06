'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-09 22:02:01
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-05-06 22:38:11
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
        self.ximalayaTag = ximalayaTag
        self.items = []

    def _getItems(self):
        if len(self.items) <= 0:
            self.items = self._getLocalMenu() + self._getRemoteMenu()
            # 设置序号以播报时更能够了解自身位置
            i = 1
            for item in self.items:
                item.setIndex(i)
                i += 1
        return self.items

    def _getLocalMenu(self):
        return self.localMenu
    
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
        self.lastPlayIndex = 0
        self.playAt = 0
        # 此处不加载音频列表，在onEnter处加载
        self.remoteContent = None
        self.sounds = []

    def onSelect(self):
        super().onSelect()
        print('ID：%s'%self.albumID)

    def onEnter(self):
        super().onEnter()
        self.remoteContent = self.UI_mgr.xAPI.getPlaylist(self.albumID)
        if self.remoteContent is None or len(self.remoteContent) == 0:
            self.UI_mgr.insAnnc('专辑加载失败，请稍后再试', needBlock=True)
            print('专辑加载失败')
            return -1
        self.sounds = [SoundContent(self.UI_mgr, track.title, track.trackId, track.playUrl64) for track in self.remoteContent]
        # 暂停主声音的播放，防止播报完还在加载时又播放主声音
        self.UI_mgr.soundMgr.outterPause()
        # 这里会播报音频的标题，需要阻塞住，防止播报和主声音同时播放
        self.sounds[self.lastPlayIndex].onSelect(needBlock=True)
        print('进入了：%s'%self.title)
        self.UI_mgr.setAlbum(self)
        self.UI_mgr.playSound(url=self.sounds[self.lastPlayIndex].playUrl)

    def onTrackPlayFinish(self):
        self.onGoNext()

    def onGoNext(self):
        self.lastPlayIndex += 1
        self.lastPlayIndex %= len(self.sounds)
        # 暂停主声音的播放，防止播报完还在加载时又播放主声音
        self.UI_mgr.soundMgr.outterPause()
        # 这里会播报音频的标题，需要阻塞住，防止播报和主声音同时播放
        self.sounds[self.lastPlayIndex].onSelect(needBlock=True)
        self.UI_mgr.playSound(url=self.sounds[self.lastPlayIndex].playUrl)

    def onGoLast(self):
        self.lastPlayIndex += (-1 + len(self.sounds))
        self.lastPlayIndex %= len(self.sounds)
        # 暂停主声音的播放，防止播报完还在加载时又播放主声音
        self.UI_mgr.soundMgr.outterPause()
        # 这里会播报音频的标题，需要阻塞住，防止播报和主声音同时播放
        self.sounds[self.lastPlayIndex].onSelect(needBlock=True)
        self.UI_mgr.playSound(url=self.sounds[self.lastPlayIndex].playUrl)

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
        self.UI_mgr.insAnnc(self.title, needBlock)

    def onEnter(self):
        pass