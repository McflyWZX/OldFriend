
'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:29
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-19 16:37:48
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
import json
import time

SOUNDS_PATH = './sounds'
STARTUP_INTFO_PATH = './startUpInfo.json'
KEY_MAP_JSON = './keyMap.json'

'''
description: 提供SUI的创建和管理功能，负责SUI内部控件数据流传递.
             SUI有个正在浏览的对象，即activity，切换activity时，调用新浏览
             activity的按键功能挂接函数
'''

class SUI:
    def __init__(self, soundMgr:SoundManager, TTS_mgr: TTS_manager, xAPI: XiMalaya):
        self.soundMgr = soundMgr
        self.soundMgr.setEndEventHandler(self.onSoundPlayEnd)
        self.TTS_mgr = TTS_mgr
        self.xAPI = xAPI
        self.keyMap: dict[str, Callable[[], None]] = {}
        if self._parseAndSetKeyMap() != 0:
            return
        self.qButtons = set()
        self._visitStack: list[Control] = []   # 浏览栈
        self._home: Control = None   # 主页
        self._album: SoundAlbum = None     # 主加载的专辑

        if not os.path.isdir(SOUNDS_PATH):
                os.mkdir(SOUNDS_PATH)

        # 启动信息
        startUpMessage = self._parseStartupInfo()
        if startUpMessage != '':
            self.insAnnc(startUpMessage, needBlock=True)
            time.sleep(0.5)

        # 启动按键监听
        keyboard.hook(self.onKeyPress)
        print(f"SUI 按键监控开始运行")

    '''
    description: 将启动信息解析为字典，并转化为启动提示欢迎语句
    param {*} self
    '''
    def _parseStartupInfo(self) -> str:
        startUpMessage = ''
        if not os.path.isfile(STARTUP_INTFO_PATH):
            print("启动信息文件不存在")
            return startUpMessage
        try:
            with open(STARTUP_INTFO_PATH, 'r', encoding='utf-8') as f:
                startupInfo = json.load(f)
            # 如果更新信息已经播报过了，则不再播报
            if startupInfo['annced'] == 'True':
                startUpMessage = startupInfo["welcomeMessage"]
            else:
                welcomeMessage: str = startupInfo["welcomeMessage"]
                version: str = startupInfo["version"]
                updatedTime: str = startupInfo["updatedTime"]
                changes: list[str] = startupInfo["changes"]
                startUpMessage = f"{welcomeMessage}，当前版本为：{version}，更新时间为{updatedTime}。"
                startUpMessage += "更新内容有："
                for change in changes:
                    startUpMessage += change + '，'
                startUpMessage += "请享用本程序。"
            print(f"启动信息加载成功: {startUpMessage}")
            # 是否播报过更新为True
            startupInfo['annced'] = 'True'
            with open(STARTUP_INTFO_PATH, 'w', encoding='utf-8') as f:
                json.dump(startupInfo, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"启动信息加载失败: {e}")
        return startUpMessage

    '''
    description: 根据环境变量'OLD_FRIEND_KEY_MAP_TYPE'，选择KEY_MAP_JSON中的按键映射
    param {*} self
    '''    
    def _parseAndSetKeyMap(self):
        if not os.path.isfile(KEY_MAP_JSON):
            print("Keymap file not found.")
            return -1

        try:
            with open(KEY_MAP_JSON, 'r', encoding='utf-8') as f:
                keyMapStrs: dict = json.load(f)
                keyMapType = os.getenv('OLD_FRIEND_KEY_MAP_TYPE', 'default')
                if keyMapType in keyMapStrs.keys():
                    keyMapStr = keyMapStrs[keyMapType]
                    print(f"Loaded keymap for type: {keyMapType}")
                    self._setKeyMap(keyMapStr)
                    return 0
                    
        except Exception as e:
            print(f"Failed to load keymap: {e}")
        return -1

    '''
    description: 根据按键映射表设置按键映射
    param {*} self
    param {dict} keyMapStr: 储存有 按键功能: 按键名称映射
    '''    
    def _setKeyMap(self, keyMapStr: dict):
        self.keyMap[keyMapStr['keyNext']] = self._onPressNext
        self.keyMap[keyMapStr['keyLast']] = self._onPressLast
        self.keyMap[keyMapStr['keyEnter']] = self._onPressEnter
        self.keyMap[keyMapStr['keyEsc']] = self._onPressBack
        self.keyMap[keyMapStr['keyPause']] = self._onPressPause

    def onSoundPlayEnd(self):
        if self._album is not None:
            self._album.onTrackPlayFinish()

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
            opStr = self.soundMgr.toggleOutterPause()
            self.insAnnc(opStr)

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
            self.setHome(self._home)
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