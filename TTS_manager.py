'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:47:14
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-04-10 22:22:42
FilePath: \GitClone\OldFriend\TTS_manager.py
Description: TTS管理模块，黑盒化文字键值转语音，内部基于记忆化搜索和TTS服务递归，仅在有需要时请求TTS服务，减小开销
'''
import sqlite3
import hashlib
import os
from TTS_service import TTS_service

TTS_PATH = 'ttsFile/'

class TTS_manager:
    def __init__(self, ttsService: TTS_service):
        self.ttsDbPath = 'tts.db'
        self._initTTSdb()
        self.ttsService = ttsService

    def tts(self, text: str):
        self.ttsDb = sqlite3.connect(self.ttsDbPath)
        txtHash = self._getHash(text)
        fileName = txtHash + '.mp3'
        # 如果文件不存在或数据库无记录，那无论如何都要创建文件的，同时更新数据库
        if (not os.path.isfile(TTS_PATH + fileName)) or (not self._isTxtHashExitst(text, txtHash)):
            self._saveTxtHash(text, txtHash)
            if os.path.isfile(fileName):
                os.remove(fileName)
            self.ttsService.tts(text, TTS_PATH, fileName)
        self.ttsDb.close()
        return TTS_PATH + fileName
    
    def _initTTSdb(self):
        # 数据库用于储存hash值与原文的对应关系
        self.ttsDb = sqlite3.connect(self.ttsDbPath)
        self.ttsDb.execute('''CREATE TABLE IF NOT EXISTS tts_files
                        (hash_id TEXT PRIMARY KEY,
                        original_text TEXT NOT NULL)''')
        self.ttsDb.close()
        
    def _getHash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def _isTxtHashExitst(self, text: str, txtHash: str) -> bool:
        cursor = self.ttsDb.cursor()
        cursor.execute("SELECT original_text FROM tts_files WHERE hash_id=?", (txtHash,))
        row = cursor.fetchone()
        if row:
            if row[0] != text:
                # 哈西冲突了，直接把源文件和db里的记录覆盖掉，这里返回不存在
                print(f"哈希冲突！'{text}' 与 '{row[0]}'")
                return False
            return True
    
    def _saveTxtHash(self, text: str, txtHash: str):
        self.ttsDb.execute(
            "INSERT OR REPLACE INTO tts_files VALUES (?, ?)",
            (txtHash, text)
        )
        self.ttsDb.commit()