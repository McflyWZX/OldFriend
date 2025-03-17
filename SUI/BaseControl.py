'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-08 16:32:06
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-18 00:38:52
FilePath: \OldFriend\'SUI'\BaseControl.py
Description: SUI模块内的控件子模块，定义了
             列表、选项、快捷按钮三种交互控件及基础控件
'''
from typing import TYPE_CHECKING
from SoundManager import SoundManager
from TTS_manager import TTS_manager
from typing import Callable
from pynput.keyboard import Key
if TYPE_CHECKING:
    from SUI.Manager import SUI

'''
description: 交互式控件的基类
'''
class Control:
    def __init__(self, UI_mgr: 'SUI'):
        self.UI_mgr = UI_mgr;
        self.keyMap: dict[Key, Callable[[], None]] = None

    def onSelect(self):
        pass

    def onEnter(self):
        pass

    def getNewKeyMap(self):
        return self.keyMap

'''
description: 表项控件，当被选中时，默认播报标项名字
'''
class Item(Control):
    def __init__(self, UI_mgr: 'SUI', title='未知栏目'):
        super().__init__(UI_mgr)
        self.title = title

    def onSelect(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)

    def onEnter(self):
        pass

'''
description: 表项列表控件，当被选中时，默认播报列表的名字，拥有一个管理标项的list
'''
class ItemList(Control):
    def __init__(self, UI_mgr: 'SUI', title='未知栏目'):
        super().__init__(UI_mgr)
        self.title = title
        self.items:list[Item] = []
        self.index = 0
        # self.keyMap[Key.right]

    def onSelect(self):
        super().onSelect()

    def onEnter(self):
        if len(self.items) == 0:
            # TODO: 播放“当前分类无内容”
            return
        # 将SUI当前正在浏览的列表替换  
        self.UI_mgr.enterVisitList(self)
        self.items[0].onSelect()

    '''
    description: 获取自己的items，默认直接返回，上层可根据需要重构
    '''    
    def __getItems(self):
        return self.items

    def __keyNext(self):
        self.index += 1
        self.index %= len(self.__getItems())
        self.items[self.index].onSelect()

    def __keyLast(self):
        self.index += (-1 + len(self.__getItems()))
        self.index %= len(self.items)
        self.items[self.index].onSelect()


class QuickButton(Control):
    def __init__(self, UI_mgr: 'SUI', title='未知栏目'):
        super().__init__(UI_mgr)
        self.title = title

    def onEnter(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)