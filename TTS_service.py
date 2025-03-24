'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-03-24 23:06:49
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-24 23:07:40
FilePath: \OldFriend\TTS_service.py
Description: TTS服务的基类
'''

class TTS_service:
    def tts(self, text: str, ttsPath: str, fileName: str):
        self.ttsPath = ttsPath
        self.fileName = fileName