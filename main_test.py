'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-24 22:41:28
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-05-08 23:42:55
FilePath: \GitClone\OldFriend\main_test.py
Description: OldFriend技术测试场
'''
from SUI.SuiManager import SUI
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
    newsOneAddOne = SoundAlbum(sui, '新闻一加一', 33234782)
    morningCaffe = SoundAlbum(sui, '声动早咖啡', 51076156)
    morningNews = SoundAlbum(sui, '早啊！新闻来了', 31903470)

    bomb = SoundAlbum(sui, '596秘史，中国原子弹', 10668866)
    fourSister = SoundAlbum(sui, '陈忠实小说《四妹子》', 37209158)

    bookSanGuo = SoundAlbum(sui, '三国演义，袁阔成先生评书', 42551351)
    # movieSanGuo = SoundAlbum(sui, '八四年三国演义，电视剧原声', 49440302)

    books = Menu(sui, '听书', ximalayaTag='听书')
    news = Menu(sui, '新闻', localMenu=[newsReport, morningCaffe, morningNews, newsOneAddOne], ximalayaTag='新闻')
    chinaHistory = Menu(sui, '中国历史', localMenu=[bookSanGuo], ximalayaTag='中国历史')
    story = Menu(sui, '小说', localMenu=[fourSister, bomb], ximalayaTag='小说')
    home = Menu(sui, '主页', localMenu=[news, books, chinaHistory, story])
    
    sui.setHome(home)
    while True:
        time.sleep(1)
elif TEST_TYPE == 'SOUND':      # 测试混响系统
    soundManager = SoundManager()
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