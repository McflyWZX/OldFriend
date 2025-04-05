'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:02
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-25 01:41:05
FilePath: \GitClone\OldFriend\SoundManager.py
Description: 声音播放管理系统，实现了主声音的播放暂停和连续播功能及操作声插播功能
'''
import pygame
import time
import threading

class SoundManager:
    def __init__(self):
        self.mainMusicPath = None
        self.pauseFlag = True
        self.playPos = 0
        pygame.mixer.init()
        pygame.init()

    def playMainMusic(self, musicPath: str = None):
        self.mainMusicPath = musicPath or self.mainMusicPath
        if self.mainMusicPath is None:
            print('Info: 尝试在没指定路径的情况下播放音乐')
            return
        pygame.mixer.music.load(self.mainMusicPath)
        pygame.mixer.music.play(loops=0)

    def pause(self):
        if self.mainMusicPath is None or self.pauseFlag is True:
            return
        # 手动控制暂停位置的方法，这里我们直接调用库函数
        # mian_music_pos_g += (pygame.mixer.music.get_pos() + FADE_DURATION / 5) / 1000.0
        # pygame.mixer.music.fadeout(FADE_DURATION)
        self.playPos = pygame.mixer.music.get_pos() / 1000.0
        pygame.mixer.music.pause()
        self.pauseFlag = True

    def resume(self):
        if self.mainMusicPath is None or self.pauseFlag is False:
            return
        # pygame.mixer.music.load(MAIN_MUSIC)
        # pygame.mixer.music.play(start=mian_music_pos_g, fade_ms=FADE_DURATION)
        pygame.mixer.music.unpause()
        self.pauseFlag = False

    '''
    description: 插入一条语音播报，立即播放、非阻塞式
    param {*} self、annc：语音播报音频文件
    return {*}
    '''
    def insVoiceAnnc(self, anncPath: str):
        # 启动语音管理的守护线程
        voice_thread = threading.Thread(
            target=self.__asyncPlayAnnc,
            args=(anncPath,),
            daemon=True  # 跟随主线程退出
        )
        voice_thread.start()

    '''
    description: 异步语音播报处理函数，会打断先前的播报
    param {*} self、annc：语音播报音频文件
    return {*}
    '''
    def __asyncPlayAnnc(self, annc_path: str):
        self.pause()
        # 立刻打断之前的播报，不混音
        pygame.mixer.stop()
        annc = pygame.mixer.Sound(annc_path)
        channel = annc.play()
        
        # 更精准的播完检测（使用Channel对象）
        while channel and channel.get_busy():
            pygame.time.wait(50)  # 改用pygame时钟等待
        self.resume()
            
