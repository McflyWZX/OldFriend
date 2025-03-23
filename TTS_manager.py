'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:47:14
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-23 17:45:20
FilePath: \GitClone\OldFriend\TTS_manager.py
Description: TTS管理模块，黑盒化文字键值转语音，内部基于记忆化搜索和TTS服务递归，仅在有需要时请求TTS服务，减小开销
'''
import sqlite3
import hashlib
import os

TTS_PATH = 'tts/'

class TTS_manager:
    def __init__(self):
        pass

    def tts(self, txt):
        return '播报：' + txt
    
    def __initTTSdb(self, ttsDbPath):
        # 数据库用于储存hash值与原文的对应关系
        self.ttsDb = sqlite3.connect(ttsDbPath)
        self.ttsDb.execute('''CREATE TABLE IF NOT EXISTS tts_files
                        (hash_id TEXT PRIMARY KEY,
                        original_text TEXT NOT NULL)''')
        
    def __getHash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
    
    def saveTxtHash(self, text: str, txtHash: str):
        cursor = self.ttsDb.cursor()
        cursor.execute("SELECT original_text FROM tts_files WHERE hash_id=?", (txtHash,))
        row = cursor.fetchone()
        if row:
            if row[0] != text:
                raise Exception(f"哈希冲突！'{text}' 与 '{row[0]}'")
            return  # 已存在
        cursor.execute("INSERT INTO tts_files VALUES (?, ?)",
                    (txtHash, text))
        self.ttsDb.commit()

    def isTxtHashExitst(self, text: str, txtHash: str) -> bool:
        cursor = self.ttsDb.cursor()
        cursor.execute("SELECT original_text FROM tts_files WHERE hash_id=?", (txtHash,))
        row = cursor.fetchone()
        if row:
            if row[0] != text:
                # 哈西冲突了，直接把源文件和db里的记录覆盖掉，这里返回不存在
                print(f"哈希冲突！'{text}' 与 '{row[0]}'")
                return False
            return True
    
    def saveTxtHash(self, text: str):
        txtHash = self.__getHash(text)
        self.ttsDb.execute(
            "INSERT OR REPLACE INTO tts_files VALUES (?, ?)",
            (txtHash, text)
        )
        self.ttsDb.commit()