'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-08 16:32:06
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-10 22:19:52
FilePath: \OldFriend\'SUI'\BaseControl.py
Description: SUI模块内的控件子模块，定义了
             列表、选项、快捷按钮三种交互控件及基础控件
'''
from typing import TYPE_CHECKING
from SoundManager import SoundManager
from TTS_manager import TTS_manager
if TYPE_CHECKING:
    from SUI.SuiManager import SUI

'''
description: 交互式控件的基类
'''
class Control:
    def __init__(self, UI_mgr: 'SUI', title='未知栏目', father: 'Control'=None):
        self.UI_mgr = UI_mgr
        self.title = title
        self.father = father
        # 防止后续设置index时产生累积效应，记录原始标题
        self.rawTitle = title

    def onSelect(self):
        self.UI_mgr.insAnnc(self.title)

    def setIndex(self, index):
        if index != -1:
            self.title = str(index) + '，' + self.rawTitle

    '''
    description: 进入（浏览）到改控件时调用
    param {*} self
    return {*}
    '''    
    def onEnter(self):
        pass

    '''
    description: 浏览该控件时按下enter时调用
    param {*} self
    return {Control} 可能返回控件，让SUI进入该控件。也可能返回空，代表SUI无需操作
    '''    
    def onPressEnter(self) -> 'Control':
        pass

    '''
    description: 退出该控件时调用
    param {*} self
    return {*}
    '''    
    def onExit(self):
        pass

    '''
    description: 浏览该控件时按下next时调用
    param {*} self
    return {*}
    '''
    def onGoNext(self):
        pass

    '''
    description: 浏览该控件时按下last时调用
    param {*} self
    return {*}
    '''
    def onGoLast(self):
        pass
    

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

'''
description: 表项列表控件，当被选中时，默认播报列表的名字，拥有一个管理标项的list
'''
class ItemList(Control):
    def __init__(self, UI_mgr: 'SUI', title='未知栏目'):
        super().__init__(UI_mgr, title)
        self.items:list[Item] = []
        self.index = 0

    def onSelect(self):
        super().onSelect()
        print('选中了：%s'%self.title)

    def onPressEnter(self) -> Control:
        items = self._getItems()
        if len(items) == 0:
            # TODO: 播放“未选中任何内容”
            print('未选中任何内容')
            return None
        return items[self.index]

    def onEnter(self):
        print('进入了：%s'%self.title)
        items = self._getItems()
        if len(items) == 0:
            print('该分类无内容')
            self.UI_mgr.insAnnc('该分类无内容', needBlock=True)
            return -1
        items[self.index].onSelect()

    '''
    description: 获取自己的items，默认直接返回，上层可根据需要重构
    '''    
    def _getItems(self):
        return self.items
    
    def _getNextItem(self):
        items = self._getItems()
        if len(items) <= 0:
            return None
        self.index += 1
        self.index %= len(items)
        return items[self.index]
    
    def _getLastItem(self):
        items = self._getItems()
        if len(items) <= 0:
            return None
        self.index += (-1 + len(items))
        self.index %= len(items)
        return items[self.index]

    def onGoNext(self):
        item = self._getNextItem()
        if item is None:
            return
        item.onSelect()

    def onGoLast(self):
        item = self._getLastItem()
        if item is None:
            return
        item.onSelect()

