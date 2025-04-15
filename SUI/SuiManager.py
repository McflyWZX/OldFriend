
'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:29
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-10 22:20:28
FilePath: \OldFriend\SUI\SUI.py
Description: SUI(Sound user interface)，是纯声音用户交互的实现。
             其基于可播报线性列表选项及快捷按键操作实现。
'''
from SoundManager import SoundManager
from TTS_manager import TTS_manager
from pynput import keyboard
from typing import Callable
import keyboard
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
        self.keyMap: dict[str, Callable[[], None]] = {}
        self._setKeyMap()
        self.qButtons = set()
        self._visitStack: list[Control] = []   # 浏览栈
        self._home: Control = []   # 主页
        self._album: SoundAlbum = None     # 主加载的专辑

        if not os.path.isdir(SOUNDS_PATH):
                os.mkdir(SOUNDS_PATH)

        # 启动按键监听
        keyboard.hook(self.onKeyPress)
        print(f"SUI 按键监控开始运行")

    def _setKeyMap(self):
        self.keyMap['right'] = self._onPressNext
        self.keyMap['left'] = self._onPressLast
        self.keyMap['enter'] = self._onPressEnter
        self.keyMap['esc'] = self._onPressBack
        self.keyMap['space'] = self._onPressPause


    def onSoundPlayEnd(self):
        pass

    def insAnnc(self, txt: str, needBlock=False):
        audio = self.TTS_mgr.tts(txt)
        if needBlock:
            self.soundMgr.insVoiceAnncBlock(audio)
        else:
            self.soundMgr.insVoiceAnnc(audio)

    def playSound(self, path: str=None, url: str=None):
        # url有效，说明需要下载
        if url is not None:
            path = path or SOUNDS_PATH + '/' + str(self._album.albumID)
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
        self._album = album

    # 按键监听回调
    def onKeyPress(self, event):
        if self._home is None:
            self.insAnnc('系统未初始化')
            print('未设置home')
            return
        if event.event_type == keyboard.KEY_DOWN:
            print(f"Key pressed: {event.name}")
            if event.name in self.keyMap.keys():
                # print('key mapped!')
                self.keyMap[event.name]()

    def _onPressPause(self):
        if self._album is not None:
            pass

    def _onPressBack(self):
        self._visitStack[-1].onExit()
        self._exitActivity()

    def _onPressNext(self):
        self._visitStack[-1].onGoNext()

    def _onPressLast(self):
        self._visitStack[-1].onGoLast()

    def _onPressEnter(self):
        activity = self._visitStack[-1].onPressEnter()
        if activity is not None:
            self.goVisitTo(activity)

    def _exitActivity(self):
        if len(self._visitStack) <= 1:
            self.setHome(self.home)
            return
        self._visitStack[-1].onExit()
        self._visitStack.pop()
        self._visitStack[-1].onEnter()
        # self.__setKeyMap(activity.getNewKeyMap())
        print('返回到了%s'%self._visitStack[-1])

    def goVisitTo(self, activity: Control):
        self._visitStack.append(activity)
        self._visitStack[-1].onEnter()
        print('切换到了%s'%activity)

    def setHome(self, activity: Control):
        self._home = activity
        self._visitStack.clear()
        self.goVisitTo(self._home)

if __name__ == '__main__':
    sui = SUI(None, None)