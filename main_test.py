'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-24 22:41:28
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-24 23:45:50
FilePath: \GitClone\OldFriend\main_test.py
Description: OldFriend技术测试场
'''
from SUI.Manager import SUI
from SUI.Controls import *
from ContentAPI.XiMalaya import XiMalaya
from XunFeiTTS import XunFeiTTS
import time

TTS_PATH = 'ttsFile/'
TEST_TYPE = 'TOTAL'
TEST_ANNC_FILES = ['a79bc714302bbad9561e9e2f3a7da5885ce2a8a588dcf8ca194f4a815ca6d584.mp3', 'a79bc714302bbad9561e9e2f3a7da5885ce2a8a588dcf8ca194f4a815ca6d584.mp3', 'be66fbb6cab564a893b566855bf2cca340a1b354ed42939d81cab4d0242708b2.mp3']

if TEST_TYPE == 'TOTAL':
    xunTTS = XunFeiTTS()
    ttsManager = TTS_manager(xunTTS)
    soundManager = SoundManager()
    xAPI = XiMalaya()

    sui = SUI(soundManager, ttsManager, xAPI)
    
    newsReport = SoundAlbum(sui, '新闻联播', 31923706)
    morningCaffe = SoundAlbum(sui, '声动早咖啡', 51076156)


    books = Menu(sui, '听书', ximalayaTag='听书')
    news = Menu(sui, '新闻', localMenu=[newsReport, morningCaffe], ximalayaTag='新闻')
    home = Menu(sui, '主页', localMenu=[news, books])
    
    sui.changeVisitTo(home)
    while True:
        time.sleep(1)
elif TEST_TYPE == 'SOUND':      # 测试混响系统
    soundManager = SoundManager()
    # soundManager.insVoiceAnnc(TTS_PATH + 'test.mp3')
    # time.sleep(2)
    # soundManager.insVoiceAnnc(TTS_PATH + 'test.mp3')
    # time.sleep(2)
    # soundManager.insVoiceAnnc(TTS_PATH + 'test.mp3')
    for annc in TEST_ANNC_FILES:
        soundManager.insVoiceAnnc(TTS_PATH + annc)
        time.sleep(2)
elif TEST_TYPE == 'TTS':        # 测试TTS系统
    xunTTS = XunFeiTTS()
    ttsManager = TTS_manager(xunTTS)
    audio = ttsManager.tts('新闻联播')
    print(audio)
    audio = ttsManager.tts('新闻联播')
    print(audio)
    audio = ttsManager.tts('声动早咖啡')
    print(audio)