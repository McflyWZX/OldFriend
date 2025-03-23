'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:09:02
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-23 16:34:58
FilePath: \GitClone\OldFriend\SoundManager.py
Description: 声音播放管理系统，实现了主声音的播放暂停和连续播功能及操作声插播功能
'''
import pygame
import time

class SoundManager:
    def __init__(self):
        self.mainMusicPath = None
        self.pause = True
        self.playPos = 0
        pygame.mixer.init()
        pygame.init()

    def playMainMusic(self, musicPath: str = None):
        self.mainMusicPath = musicPath if musicPath is not None else self.mainMusicPath
        if self.mainMusicPath is None:
            print('Info: 尝试在没指定路径的情况下播放音乐')
            return
        pygame.mixer.music.load(self.mainMusicPath)
        pygame.mixer.music.play(-1)  # -1 表示无限循环

    def pause(self):
        if self.mainMusicPath is None or self.pause is True:
            return
        # 手动控制暂停位置的方法，这里我们直接调用库函数
        # mian_music_pos_g += (pygame.mixer.music.get_pos() + FADE_DURATION / 5) / 1000.0
        # pygame.mixer.music.fadeout(FADE_DURATION)
        self.playPos = pygame.mixer.music.get_pos() / 1000.0
        pygame.mixer.music.pause()
        self.pause = True

    def resume(self):
        if self.mainMusicPath is None or self.pause is False:
            return
        # pygame.mixer.music.load(MAIN_MUSIC)
        # pygame.mixer.music.play(start=mian_music_pos_g, fade_ms=FADE_DURATION)
        pygame.mixer.music.unpause()
        self.pause = False

    '''
    description: 插入一条语音播报，立即播放
    param {*} self、annc：语音播报音频文件
    return {*}
    '''    
    def insVoiceAnnc(self, anncPath: str):
        self.pause()
        # 加载并播放音效
        annc = pygame.mixer.Sound(anncPath)
        annc.play()
        
        # 等待音效播放完成
        while annc.get_num_channels() > 0:
            time.sleep(0.01)
        self.resume
