
'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:29
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-02-28 01:56:24
FilePath: \GitClone\OldFriend\SUI.py
Description: SUI(Sound user interface)，是纯声音用户交互的实现。
             其基于可播报线性列表选项及快捷按键操作实现。还定义了
             列表、选项、快捷按钮三种交互控件及基础控件
'''
from SoundManager import SoundManager
from TTS_manager import TTS_manager

'''
description: 提供SUI的创建和管理功能，负责SUI内部控件数据流传递
'''
class SUI:
    def __init__(self, soundMgr:SoundManager, TTS_mgr:TTS_manager):
        self.soundMgr = soundMgr
        self.TTS_mgr = TTS_mgr
        self.__visitList = None

    def enterVisitList(self, itemList:"ItemList"):
        self.__visitList = itemList

'''
description: 交互式控件的基类
'''
class Control:
    def __init__(self, UI_mgr:SUI):
        self.UI_mgr = UI_mgr;

    def onSelect(self):
        pass

    def onEnter(self):
        pass

'''
description: 表项控件，当被选中时，默认播报标项名字
'''
class Item(Control):
    def __init__(self, UI_mgr:SUI, title='未知栏目'):
        super().__init__(UI_mgr)
        self.title = title

    def onSelect(self):
        audio = self.UI_mgr.TTS_mgr.tts()
        self.UI_mgr.soundMgr.insVoiceAnnc(audio)

    def onEnter(self):
        pass

'''
description: 表项列表控件，当被选中时，默认播报列表的名字，拥有一个管理标项的list
'''
class ItemList(Control):
    def __init__(self, UI_mgr:SUI, title='未知栏目'):
        super().__init__(UI_mgr)
        self.title = title
        self.items:list[Item] = []

    def onSelect(self):
        super().onSelect()

    def onEnter(self):
        if len(self.items) == 0:
            # TODO: 播放“当前分类无内容”
            return
        # 将SUI当前正在浏览的列表替换  
        self.UI_mgr.enterVisitList(self)
        self.items[0].onSelect()
