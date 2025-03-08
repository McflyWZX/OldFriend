'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-24 22:41:28
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-08 16:43:06
FilePath: \GitClone\OldFriend\main_test.py
Description: OldFriend技术测试场
'''
from SUI.Manager import SUI
# import pygame
# from pynput import keyboard
# import threading
# import time

# # ========== 配置区 ==========
# MAIN_MUSIC = "D:/GitClone/OldFriend/news.mp3"   # 主音乐文件路径
# SFX_FILE = "D:/GitClone/OldFriend/next.mp3"     # 插播音效文件路径
# TRIGGER_KEY = keyboard.Key.space  # 插播触发键
# FADE_DURATION = 500             # 主音乐淡出时间（毫秒）
# # ========== 全局区 ==========
# mian_music_pos_g = 0
# # ===========================

# # 初始化音频系统
# pygame.mixer.init()
# pygame.init()

# # 主音乐控制函数
# def play_main_music():
#     pygame.mixer.music.load(MAIN_MUSIC)
#     pygame.mixer.music.play(-1)  # -1 表示无限循环

# # 插播音效播放函数（带音量衰减）
# def play_sfx():
#     global mian_music_pos_g
#     try:
#         # 主音乐淡出
#         mian_music_pos_g += (pygame.mixer.music.get_pos() + FADE_DURATION / 5) / 1000.0
#         pygame.mixer.music.fadeout(FADE_DURATION)
        
#         # 加载并播放音效
#         sfx = pygame.mixer.Sound(SFX_FILE)
#         sfx.play()
        
#         # 等待音效播放完成
#         while sfx.get_num_channels() > 0:
#             time.sleep(0.1)
#     finally:
#         # 恢复主音乐播放
#         pygame.mixer.music.load(MAIN_MUSIC)
#         pygame.mixer.music.play(start=mian_music_pos_g, fade_ms=FADE_DURATION)


# # 按键监听回调
# def on_press(key):
#     if key == TRIGGER_KEY:
#         print("触发插播音效")
#         # 开启独立线程播放音效（避免阻塞监听）
#         threading.Thread(target=play_sfx).start()

# # 启动主音乐
# play_main_music()

# # 启动按键监听
# with keyboard.Listener(on_press=on_press) as listener:
#     print(f"程序运行中 | 主音乐循环中 | 按 {TRIGGER_KEY} 触发插播")
#     listener.join()

sui = SUI(None, None)