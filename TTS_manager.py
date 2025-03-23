'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-02-26 21:47:14
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-03-23 21:54:07
FilePath: \GitClone\OldFriend\TTS_manager.py
Description: TTS管理模块，黑盒化文字键值转语音，内部基于记忆化搜索和TTS服务递归，仅在有需要时请求TTS服务，减小开销
'''
import sqlite3
import hashlib
import os

TTS_PATH = 'tts/'

class TTS_manager:
    def __init__(self):
        self.__initTTSdb('tts.db')

    def tts(self, text: str):
        txtHash = self.__getHash(text)
        fileName = TTS_PATH + txtHash + '.mp3'
        # 如果文件不存在或数据库无记录，那无论如何都要创建文件的，同时更新数据库
        if (not os.path.isfile(fileName)) or (not self.__isTxtHashExitst(text, txtHash)):
            self.__saveTxtHash(text, txtHash)
            # TODO: 生成文件
            if os.path.isfile(fileName):
                os.remove(fileName)
        return fileName
    
    def __initTTSdb(self, ttsDbPath: str):
        # 数据库用于储存hash值与原文的对应关系
        self.ttsDb = sqlite3.connect(ttsDbPath)
        self.ttsDb.execute('''CREATE TABLE IF NOT EXISTS tts_files
                        (hash_id TEXT PRIMARY KEY,
                        original_text TEXT NOT NULL)''')
        
    def __getHash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def __isTxtHashExitst(self, text: str, txtHash: str) -> bool:
        cursor = self.ttsDb.cursor()
        cursor.execute("SELECT original_text FROM tts_files WHERE hash_id=?", (txtHash,))
        row = cursor.fetchone()
        if row:
            if row[0] != text:
                # 哈西冲突了，直接把源文件和db里的记录覆盖掉，这里返回不存在
                print(f"哈希冲突！'{text}' 与 '{row[0]}'")
                return False
            return True
    
    def __saveTxtHash(self, text: str, txtHash: str):
        self.ttsDb.execute(
            "INSERT OR REPLACE INTO tts_files VALUES (?, ?)",
            (txtHash, text)
        )
        self.ttsDb.commit()