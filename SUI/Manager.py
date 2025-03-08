
'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:29
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-08 16:22:31
FilePath: \OldFriend\SUI\SUI.py
Description: SUI(Sound user interface)，是纯声音用户交互的实现。
             其基于可播报线性列表选项及快捷按键操作实现。
'''
from ..SoundManager import SoundManager
from ..TTS_manager import TTS_manager
from pynput import keyboard
from typing import Callable
from pynput.keyboard import Key
import copy
import BaseControl

'''
description: 提供SUI的创建和管理功能，负责SUI内部控件数据流传递.
             SUI有个正在浏览的对象，即activity，切换activity时，调用新浏览
             activity的按键功能挂接函数
'''
class SUI:
    def __init__(self, soundMgr:SoundManager, TTS_mgr:TTS_manager):
        self.soundMgr = soundMgr
        self.TTS_mgr = TTS_mgr
        self.__activity = None
        self.keyMap: dict[Key, Callable[[], None]] = {Key.right: self.aaa, Key.left: self.bbb}  # TODO: 按键初始状态

        # 启动按键监听
        with keyboard.Listener(on_press=self.onKeyPress) as keyListener:
            print(f"SUI 按键监控开始运行")
            keyListener.join()

    # 按键监听回调
    def onKeyPress(self, key):
        if key == keyboard.Key.space:
            print("触发插播音效")
            # 开启独立线程播放音效（避免阻塞监听）
            print(self)
        if key in self.keyMap.keys():
            self.keyMap[key]()
        print(key)

    def aaa(self):
        print('aaa')
        print(self)
        
    def bbb(self):
        print('bbb')
        print(self)

    def changeVisitTo(self, activity: BaseControl.Control):
        self.__activity = activity
        self.__setKeyMap(activity)

    def __setKeyMap(self, newKeyMap:dict[Key, Callable[[], None]]):
        # TODO: 这个地方储存旧的keyMap，并将新keyMap中有效的键位映射替换
        pass



if __name__ == '__main__':
    sui = SUI(None, None)