'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-08 16:32:06
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-30 15:04:42
FilePath: \OldFriend\'SUI'\BaseControl.py
Description: SUI模块内的控件子模块，定义了
             列表、选项、快捷按钮三种交互控件及基础控件
'''
from typing import TYPE_CHECKING
from SoundManager import SoundManager
from TTS_manager import TTS_manager
from typing import Callable
from pynput.keyboard import Key, KeyCode
if TYPE_CHECKING:
    from SUI.Manager import SUI

'''
description: 交互式控件的基类
'''
class Control:
    def __init__(self, UI_mgr: 'SUI', title='未知栏目', father: 'Control'=None):
        self.UI_mgr = UI_mgr
        self.title = title
        self.father = father
        self.keyMap: dict[KeyCode, Callable[[], None]] = {}

    def onSelect(self):
        audio = self.UI_mgr.TTS_mgr.tts(self.title)
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)

    def onEnter(self):
        pass

    def onBack(self):
        return [key for key in self.keyMap.keys()]

    def getNewKeyMap(self):
        return self.keyMap
    

'''
description: 表项控件，当被选中时，默认播报标项名字
'''
class Item(Control):
    def __init__(self, UI_mgr: 'SUI', title='未知栏目'):
        super().__init__(UI_mgr, title)

    def onSelect(self):
        super().onSelect()
        print('选中了：%s'%self.title)

    def onEnter(self):
        print('进入了：%s'%self.title)
        pass

'''
description: 表项列表控件，当被选中时，默认播报列表的名字，拥有一个管理标项的list
'''
class ItemList(Control):
    def __init__(self, UI_mgr: 'SUI', title='未知栏目'):
        super().__init__(UI_mgr, title)
        self.items:list[Item] = []
        self.index = 0
        self.keyMap[Key.right] = self.__keyNext
        self.keyMap[Key.left] = self.__keyLast
        self.keyMap[Key.enter] = self.__keyEnter

    def onSelect(self):
        super().onSelect()
        print('选中了：%s'%self.title)

    def onEnter(self):
        if len(self.items) == 0:
            # TODO: 播放“当前分类无内容”
            print('当前分类无内容')
            return
        # 将SUI当前正在浏览的列表替换  
        self.UI_mgr.changeVisitTo(self)
        self.items[0].onSelect()
        print('进入了：%s'%self.title)

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

    def __keyEnter(self):
        self.items[self.index].onEnter()

