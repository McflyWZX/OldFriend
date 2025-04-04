'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-09 22:02:01
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-05 17:10:44
FilePath: \OldFriend\SUI\Controls.py
Description: SUI模块内的具体控件实现模块
'''
from SoundManager import SoundManager
from TTS_manager import TTS_manager
from typing import Callable
from pynput.keyboard import Key
from SUI.BaseControl import *
from ContentAPI.XiMalaya import *

'''
description: 菜单，储存SoundContent或者子Menu
'''

DEFAULT_DESC = '这个内容没有介绍'

class Menu(ItemList):
    def __init__(self, UI_mgr, title: str, desc: str="", father: Control=None, localMenu: list[Item]=[], ximalayaTag: str=None):
        super().__init__(UI_mgr, title)
        self.localMenu = localMenu
        self.ximalayaTag = ximalayaTag
        self.items += self.__getLocalMenu()
        self.items += self.__getRemoteMenu()

    def __getLocalMenu(self):
        return self.localMenu
    
    def __getRemoteMenu(self):
        if self.ximalayaTag is None:
            return []
        self.remoteAlbum = self.UI_mgr.xAPI.searchAlbums(self.title)
        return [SoundAlbum(self.UI_mgr, album.title, album.id) for album in self.remoteAlbum]

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
        self.keyMap[Key.right] = self.__keyNext
        self.keyMap[Key.left] = self.__keyLast

    def onSelect(self):
        super().onSelect()

    def onEnter(self):
        super().onEnter()
        self.remoteContent = self.UI_mgr.xAPI.getPlaylist(self.albumID)
        self.sounds = [SoundContent(self.UI_mgr, track.title, track.trackId, track.playUrl64) for track in self.remoteContent]
        if len(self.sounds) == 0:
            # TODO: 播放“专辑加载失败”
            print('专辑加载失败')
            return
        # 将SUI当前正在浏览的列表替换  
        self.UI_mgr.changeVisitTo(self)
        self.sounds[self.lastPlayIndex].onSelect()
        print('进入了：%s'%self.title)
        self.UI_mgr.setAlbum(self)
        self.UI_mgr.playSound(url=self.sounds[self.lastPlayIndex].playUrl)

    def onTrackPlayFinish(self):
        self.__keyNext()

    def __keyNext(self):
        self.lastPlayIndex += 1
        self.lastPlayIndex %= len(self.sounds)
        self.sounds[self.lastPlayIndex].onSelect()
        self.UI_mgr.playSound(url=self.sounds[self.lastPlayIndex].playUrl)

    def __keyLast(self):
        self.lastPlayIndex += (-1 + len(self.sounds))
        self.lastPlayIndex %= len(self.sounds)
        self.sounds[self.lastPlayIndex].onSelect()
        self.UI_mgr.playSound(url=self.sounds[self.lastPlayIndex].playUrl)

'''
description: 声音内容，包含具体的音源ID，当点击时替换主音乐并更新SoundAlbum状态
'''
class SoundContent(Item):
    def __init__(self, UI_mgr, title: str, ID:int, playUrl: str):
        super().__init__(UI_mgr, title)
        self.contentID = ID
        self.playRecord = 0
        self.playUrl = playUrl

    def onSelect(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)

    def onEnter(self):
        pass

class QuickButton(Control):
    def __init__(self, UI_mgr: 'SUI', key: KeyCode, title='未知栏目', control: Control=None, action: Callable[['SUI'], bool]=None):
        super().__init__(UI_mgr)
        self.title = title
        self.control = control
        self.action = action
        self.keyMap[key] = self.__onAction

    def __onAction(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)
        if self.action is not None:
            self.action(self.UI_mgr)
        if self.control is not None:
            self.control.onEnter()