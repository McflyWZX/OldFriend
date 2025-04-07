
'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:29
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-07 17:27:03
FilePath: \OldFriend\SUI\SUI.py
Description: SUI(Sound user interface)，是纯声音用户交互的实现。
             其基于可播报线性列表选项及快捷按键操作实现。
'''
from SoundManager import SoundManager
from TTS_manager import TTS_manager
from pynput import keyboard
from typing import Callable
from pynput.keyboard import Key
import copy
from SUI.BaseControl import Control
from SUI.Controls import *
from ContentAPI.XiMalaya import XiMalaya
from urllib import request
import os

SOUNDS_PATH = './sounds'

'''
description: 提供SUI的创建和管理功能，负责SUI内部控件数据流传递.
             SUI有个正在浏览的对象，即activity，切换activity时，调用新浏览
             activity的按键功能挂接函数
'''
class SUI:
    def __init__(self, soundMgr:SoundManager, TTS_mgr: TTS_manager, xAPI: XiMalaya):
        self.soundMgr = soundMgr
        self.TTS_mgr = TTS_mgr
        self.xAPI = xAPI
        self.keyMap: dict[Key, Callable[[], None]] = {}
        self.qButtons = set()
        self.__visitStack: list[Control] = []   # 浏览栈
        self.__home: Control = []   # 主页
        self.__album: SoundAlbum = None     # 主加载的专辑

        if not os.path.isdir(SOUNDS_PATH):
                os.mkdir(SOUNDS_PATH)

        self.addQuickButton(QuickButton(self, Key.esc, title='返回', action=self.__onPressBack))

        # 启动按键监听
        keyboard.Listener(on_press=self.onKeyPress).start()
        print(f"SUI 按键监控开始运行")

    def onSoundPlayEnd(self):
        pass

    def playSound(self, path: str=None, url: str=None):
        # url有效，说明需要下载
        if url is not None:
            path = path or SOUNDS_PATH + '/' + str(self.__album.albumID)
            if not os.path.isdir(path):
                os.mkdir(path)
            path += '/' + url.split('/')[-1]
            if os.path.isfile(path):
                self.soundMgr.playMainMusic(path)
                return
            request.urlretrieve(url, path)
            if os.path.isfile(path):
                self.soundMgr.playMainMusic(path)
                return
            else:
                print('加载失败: ' + url)
        else:
            print('无url: ' + url)
            
    def setAlbum(self, album: SoundAlbum):
        self.__album = album

    def addQuickButton(self, qButton: QuickButton):
        if qButton in self.qButtons:
            print("Err: 该快捷按键已在SUI内")
        self.qButtons.add(qButton)
        self.__setKeyMap(qButton.getNewKeyMap())

    # 按键监听回调
    def onKeyPress(self, key):
        if key in self.keyMap.keys():
            # print('key mapped!')
            self.keyMap[key]()
        print(key)

    def __onPressPause(self):
        if self.__album is not None:
            pass

    def __onPressBack(self):
        self.__exitActivity()

    def __exitActivity(self):
        if len(self.__visitStack) <= 1:
            self.__visitStack.clear()
            self.changeVisitTo(self.home)
            # TODO：还要恢复按键设置到默认
            return
        delKeys = self.__visitStack[-1].onBack()
        self.__delKeyMap(delKeys)
        self.__visitStack.pop()
        self.__setKeyMap(self.__visitStack[-1].getNewKeyMap())
        # self.__setKeyMap(activity.getNewKeyMap())
        print('切换到了%s'%self.__visitStack[-1])

    def changeVisitTo(self, activity: Control):
        self.__visitStack.append(activity)
        self.__setKeyMap(activity.getNewKeyMap())
        print('切换到了%s'%activity)

    def setHome(self, activity: Control):
        self.__home = activity
        self.changeVisitTo(self.__home)

    def __setKeyMap(self, newKeyMap:dict[Key, Callable[[], None]]):
        for key in newKeyMap.keys():
            self.keyMap[key] = newKeyMap[key]

    def __delKeyMap(self, delKeys:list[Key]):
        for key in delKeys:
            self.keyMap.pop(key)

if __name__ == '__main__':
    sui = SUI(None, None)