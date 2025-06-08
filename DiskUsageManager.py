'''
Author: Mcfly coolmcfly@qq.com
Date: 2025-06-06 20:52:23
LastEditors: Mcfly coolmcfly@qq.com
LastEditTime: 2025-06-08 10:04:48
FilePath: \OldFriend\DiskUsageManager.py
Description: 检查文件系统大小，按时间先后顺序删除缓存文件
'''
import os
import shutil
import time
from typing import List, Tuple

# 配置参数
SOUNDS_DIR = "sounds"  # 替换为实际的sounds目录路径
MINIMAL_USAGE_SPACE = int(0.3*1024*1024*1024)  # 触发清理的磁盘使用百分比
TARGET_FREE_SPACE = int(0.6*1024*1024*1024)  # 目标清理到的使用百分比
CHECK_PARTITION = "/"  # 监控的挂载点

def getDiskUsage() -> int:
    """获取根分区的磁盘使用百分比"""
    usage = shutil.disk_usage(CHECK_PARTITION)
    return usage.free

def getAllSoundFiles() -> List[Tuple[str, float]]:
    """获取所有MP3文件及其创建时间（按时间排序）"""
    fileList = []
    
    for root, dirs, files in os.walk(SOUNDS_DIR):
        for file in files:
            if file.lower().endswith(".mp3"):
                filePath = os.path.join(root, file)
                # 使用创建时间（ctime），Linux没有真正的创建时间，这里用inode变更时间
                ctime = os.path.getctime(filePath)  
                fileList.append((filePath, ctime))
    
    # 按创建时间升序排列（最旧的文件在前）
    return sorted(fileList, key=lambda x: x[1])

def deleteSoundsUntilThreshold():
    """执行删除操作直到满足磁盘空间要求"""
    deletedSize = 0
    
    # 获取所有文件（已排序）
    files = getAllSoundFiles()
    
    for filePath, _ in files:
        if getDiskUsage() >= TARGET_FREE_SPACE:
            break
        
        try:
            # 计算文件大小并删除
            fileSize = os.path.getsize(filePath)
            os.remove(filePath)
            deletedSize += fileSize
            print(f"已删除：{filePath} ({fileSize/1024/1024:.2f} MB)")
            
            # 清理空目录
            deleteEmptyDirs(os.path.dirname(filePath))
            
        except Exception as e:
            print(f"删除失败 {filePath}: {str(e)}")
            
    print(f"共释放空间：{deletedSize/1024/1024:.2f} MB")

def deleteEmptyDirs(start_dir: str):
    """递归删除空目录"""
    currentDir = start_dir
    
    while currentDir != SOUNDS_DIR:
        if os.path.exists(currentDir) and not os.listdir(currentDir):
            try:
                os.rmdir(currentDir)
                print(f"已删除空目录：{currentDir}")
                currentDir = os.path.dirname(currentDir)  # 向上级检查
            except OSError:
                break  # 目录非空或没有权限
        else:
            break

def checkDiskUsageAndClean():
    currentUsage = getDiskUsage()
    
    if currentUsage <= MINIMAL_USAGE_SPACE:
        print(f"当前磁盘空闲剩余：{currentUsage / 1024.0 / 1024.0:.1f}M，开始清理...")
        deleteSoundsUntilThreshold()
    else:
        print(f"当前磁盘空闲剩余：{currentUsage / 1024.0 / 1024.0:.1f}M.，无需清理")
        

if __name__ == "__main__":
    checkDiskUsageAndClean()