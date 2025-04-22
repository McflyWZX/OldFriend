'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:02
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-22 22:59:02
FilePath: \GitClone\OldFriend\SoundManager.py
Description: 声音播放管理系统，实现了主声音的播放暂停和连续播功能及操作声插播功能
'''
import pygame
import time
import threading
from typing import Callable

MAIN_MUSIC_END = pygame.USEREVENT + 20
MAIN_MUSIC_END = pygame.USEREVENT + 20

class SoundManager:
    def __init__(self):
        self.mainMusicPath = None
        self.pauseFlag = True
        self.pauseOutter = True
        self.playPos = 0
        self.anncVolume = 0.6
        self.mainVolume = 1
        pygame.mixer.init()
        pygame.init()
        self.endEventHandler = None
        endEventCaptureThread = threading.Thread(
            target=self._endEventCapture,
            daemon=True  # 跟随主线程退出
        )
        endEventCaptureThread.start()

    def playMainMusic(self, musicPath: str = None):
        self.mainMusicPath = musicPath or self.mainMusicPath
        if self.mainMusicPath is None:
            print('Info: 尝试在没指定路径的情况下播放音乐')
            return
        pygame.mixer.music.load(self.mainMusicPath)
        pygame.mixer.music.set_endevent(MAIN_MUSIC_END)
        pygame.mixer.music.set_volume(self.mainVolume)
        pygame.mixer.music.play(loops=0)
        self.pauseFlag = False
        self.pauseOutter = False

    def _endEventCapture(self):
        while True:
            for event in pygame.event.get():
                if event.type == MAIN_MUSIC_END:
                    print('Info: 主音乐播放完毕')
                    if self.endEventHandler is not None:
                        self.endEventHandler()
            pygame.time.wait(1000)

    def setEndEventHandler(self, handler: Callable):
        self.endEventHandler = handler

    def toggleOutterPause(self) -> str:
        self.pauseOutter = not self.pauseOutter
        if self.pauseOutter == True:
            print('暂停')
            self._pause()
            return '暂停'
        else:
            print('恢复')
            self._resume()
            return '恢复'
        
    def outterPause(self) -> str:
        self.pauseOutter = True
        print('暂停')
        self._pause()
        return '暂停'
    
    def outterResume(self) -> str:
        self.pauseOutter = True
        print('恢复')
        self._resume()
        return '恢复'

    def _pause(self):
        if self.mainMusicPath is None or self.pauseFlag is True:
            return
        # 手动控制暂停位置的方法，这里我们直接调用库函数
        # mian_music_pos_g += (pygame.mixer.music.get_pos() + FADE_DURATION / 5) / 1000.0
        # pygame.mixer.music.fadeout(FADE_DURATION)
        self.playPos = pygame.mixer.music.get_pos() / 1000.0
        pygame.mixer.music.pause()
        self.pauseFlag = True

    def _resume(self):
        if self.mainMusicPath is None or self.pauseFlag is False:
            return
        # 恢复时需检查此时外部是否要求暂停
        if self.pauseOutter == True:
            return
        # pygame.mixer.music.load(MAIN_MUSIC)
        # pygame.mixer.music.play(start=mian_music_pos_g, fade_ms=FADE_DURATION)
        pygame.mixer.music.unpause()
        self.pauseFlag = False

    '''
    description: 插入一条语音播报，立即播放、阻塞式
    param {*} self、annc：语音播报音频文件
    return {*}
    '''
    def insVoiceAnncBlock(self, anncPath: str):
        # 启动语音管理的守护线程
        voice_thread = threading.Thread(
            target=self._asyncPlayAnnc,
            args=(anncPath,),
            daemon=True  # 跟随主线程退出
        )
        voice_thread.start()
        voice_thread.join()

    '''
    description: 插入一条语音播报，立即播放、非阻塞式
    param {*} self、annc：语音播报音频文件
    return {*}
    '''
    def insVoiceAnnc(self, anncPath: str):
        # 启动语音管理的守护线程
        voice_thread = threading.Thread(
            target=self._asyncPlayAnnc,
            args=(anncPath,),
            daemon=True  # 跟随主线程退出
        )
        voice_thread.start()

    '''
    description: 异步语音播报处理函数，会打断先前的播报
    param {*} self、annc：语音播报音频文件
    return {*}
    '''
    def _asyncPlayAnnc(self, annc_path: str):
        self._pause()
        # 立刻打断之前的播报，不混音
        pygame.mixer.stop()
        annc = pygame.mixer.Sound(annc_path)
        annc.set_volume(self.anncVolume)
        channel = annc.play()
        
        # 更精准的播完检测（使用Channel对象）
        while channel and channel.get_busy():
            pygame.time.wait(50)  # 改用pygame时钟等待
        self._resume()
            
