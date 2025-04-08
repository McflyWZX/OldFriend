
'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:29
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-08 22:18:54
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
        self.__setKeyMap()
        self.qButtons = set()
        self.__visitStack: list[Control] = []   # 浏览栈
        self.__home: Control = []   # 主页
        self.__album: SoundAlbum = None     # 主加载的专辑

        if not os.path.isdir(SOUNDS_PATH):
                os.mkdir(SOUNDS_PATH)

        # 启动按键监听
        keyboard.Listener(on_press=self.onKeyPress).start()
        print(f"SUI 按键监控开始运行")

    def __setKeyMap(self):
        self.keyMap[Key.right] = self.__onPressNext
        self.keyMap[Key.left] = self.__onPressLast
        self.keyMap[Key.enter] = self.__onPressEnter
        self.keyMap[Key.esc] = self.__onPressBack
        self.keyMap[Key.space] = self.__onPressPause


    def onSoundPlayEnd(self):
        pass

    def insAnnc(self, txt: str):
        audio = self.TTS_mgr.tts(txt)
        self.soundMgr.insVoiceAnnc(audio)

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

    # 按键监听回调
    def onKeyPress(self, key):
        if self.__home is None:
            self.insAnnc('系统未初始化')
            print('未设置home')
            return
        if key in self.keyMap.keys():
            # print('key mapped!')
            self.keyMap[key]()
        print(key)

    def __onPressPause(self):
        if self.__album is not None:
            pass

    def __onPressBack(self):
        self.__visitStack[-1].onExit()
        self.__exitActivity()

    def __onPressNext(self):
        self.__visitStack[-1].onGoNext()

    def __onPressLast(self):
        self.__visitStack[-1].onGoLast()

    def __onPressEnter(self):
        activity = self.__visitStack[-1].onPressEnter()
        if activity is not None:
            self.goVisitTo(activity)

    def __exitActivity(self):
        if len(self.__visitStack) <= 1:
            self.__setHome(self.home)
            return
        self.__visitStack[-1].onExit()
        self.__visitStack.pop()
        self.__visitStack[-1].onEnter()
        # self.__setKeyMap(activity.getNewKeyMap())
        print('返回到了%s'%self.__visitStack[-1])

    def goVisitTo(self, activity: Control):
        self.__visitStack.append(activity)
        self.__visitStack[-1].onEnter()
        print('切换到了%s'%activity)

    def setHome(self, activity: Control):
        self.__home = activity
        self.__visitStack.clear()
        self.goVisitTo(self.__home)

if __name__ == '__main__':
    sui = SUI(None, None)