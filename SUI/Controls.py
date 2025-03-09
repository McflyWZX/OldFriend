'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-09 22:02:01
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-09 22:27:33
FilePath: \OldFriend\SUI\Controls.py
Description: SUI模块内的具体控件实现模块
'''
from ..SoundManager import SoundManager
from ..TTS_manager import TTS_manager
from typing import Callable
from pynput.keyboard import Key
import Manager
import BaseControl

'''
description: 菜单，储存SoundContent或者子Menu
'''

DEFAULT_DESC = '这个内容没有介绍'

class Menu(BaseControl.ItemList):
    def __init__(self, UI_mgr, title: str, desc: str="", localMenu: list[BaseControl.Item]=[], remoteMenuUrl: str=None):
        super().__init__(UI_mgr, title)
        self.localMenu = localMenu
        self.remoteMenuUrl = remoteMenuUrl

    def getLocalMenu(self):
        return self.localMenu
    
    def getRemoteMenu(self):
        return []   # TODO: 获取在线内容菜单

'''
description: 声音集，包含具体的音源集ID，它
'''
class SoundAlbum(BaseControl.Item):
    def __init__(self, UI_mgr, title: str, ID:int, desc: str=""):
        super().__init__(UI_mgr, title)
        self.albumID = ID
        self.lastPlayIndex = 0

    def onSelect(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)

    def onEnter(self):
        pass

'''
description: 声音内容，包含具体的音源ID，当点击时替换主音乐并更新SoundAlbum状态
'''
class SoundContent(BaseControl.Item):
    def __init__(self, UI_mgr, title: str, ID:int):
        super().__init__(UI_mgr, title)
        self.contentID = ID
        self.playRecord = 0

    def onSelect(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)

    def onEnter(self):
        pass
