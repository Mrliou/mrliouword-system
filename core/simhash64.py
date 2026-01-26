#!/usr/bin/env python3
"""
SimHash64 - MrLiouWord 語意指紋系統

64 位元語意指紋，用於：
- 去重檢測
- 相似度計算
- 記憶共振檢測

Author: MR.liou
"""

from typing import List, Set

def simhash64(text: str) -> str:
    """
    計算 64 位元 SimHash 指紋
    
    Args:
        text: 輸入文本
        
    Returns:
        16 字元十六進位字串
    """
    # 正規化
    normalizedText = text.lower().replace('\n', ' ').strip()
    if len(normalizedText) < 3:
        return '0' * 16
    
    # 生成 3-gram shingles
    shingles: List[str] = []
    for charIndex in range(len(normalizedText) - 2):
        shingles.append(normalizedText[charIndex:charIndex+3])
    
    # 初始化 64 維向量
    bitVector = [0] * 64
    
    # FNV-1a 雜湊每個 shingle
    FNV_PRIME = 1099511628211
    FNV_OFFSET = 14695981039346656037
    
    for shingle in shingles:
        hashValue = FNV_OFFSET
        for charByte in shingle.encode('utf-8'):
            hashValue ^= charByte
            hashValue = (hashValue * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
        
        # 更新向量
        for bitIndex in range(64):
            if (hashValue >> bitIndex) & 1:
                bitVector[bitIndex] += 1
            else:
                bitVector[bitIndex] -= 1
    
    # 生成指紋
    fingerprint = 0
    for bitIndex in range(64):
        if bitVector[bitIndex] > 0:
            fingerprint |= (1 << bitIndex)
    
    return format(fingerprint, '016x')


def hamming_distance(hashA: str, hashB: str) -> int:
    """
    計算兩個 SimHash 的 Hamming 距離
    
    Args:
        hashA: 第一個 SimHash (hex)
        hashB: 第二個 SimHash (hex)
        
    Returns:
        Hamming 距離（不同位元數）
    """
    xorResult = int(hashA, 16) ^ int(hashB, 16)
    distance = 0
    while xorResult:
        distance += xorResult & 1
        xorResult >>= 1
    return distance


def is_similar(hashA: str, hashB: str, threshold: int = 3) -> bool:
    """
    判斷兩個文本是否語意相似
    
    Args:
        hashA: 第一個 SimHash
        hashB: 第二個 SimHash
        threshold: Hamming 距離閾值（預設 3）
        
    Returns:
        是否相似
    """
    return hamming_distance(hashA, hashB) <= threshold


def find_similar(queryText: str, candidateTexts: List[str], threshold: int = 3) -> List[tuple]:
    """
    從候選列表中找出相似文本
    
    Args:
        queryText: 查詢文本
        candidateTexts: 候選文本列表
        threshold: 相似度閾值
        
    Returns:
        [(文本, SimHash, 距離), ...] 按距離排序
    """
    queryHash = simhash64(queryText)
    matchResults = []
    
    for candidateText in candidateTexts:
        candidateHash = simhash64(candidateText)
        distanceValue = hamming_distance(queryHash, candidateHash)
        if distanceValue <= threshold:
            matchResults.append((candidateText, candidateHash, distanceValue))
    
    return sorted(matchResults, key=lambda matchItem: matchItem[2])


def deduplicate(textList: List[str], threshold: int = 3) -> List[str]:
    """
    去除重複文本
    
    Args:
        textList: 文本列表
        threshold: 相似度閾值
        
    Returns:
        去重後的文本列表
    """
    seenHashes: Set[str] = set()
    uniqueTexts: List[str] = []
    
    for textItem in textList:
        textHash = simhash64(textItem)
        isDuplicate = False
        
        for seenHash in seenHashes:
            if hamming_distance(textHash, seenHash) <= threshold:
                isDuplicate = True
                break
        
        if not isDuplicate:
            seenHashes.add(textHash)
            uniqueTexts.append(textItem)
    
    return uniqueTexts


# 測試
if __name__ == '__main__':
    # 基本測試
    text1 = "夥伴回來吧，我們繼續開發粒子系統"
    text2 = "夥伴回來吧，我們繼續開發粒子架構"
    text3 = "今天天氣很好，適合出門散步"
    
    h1 = simhash64(text1)
    h2 = simhash64(text2)
    h3 = simhash64(text3)
    
    print(f"Text 1: {h1}")
    print(f"Text 2: {h2}")
    print(f"Text 3: {h3}")
    print()
    print(f"Distance 1-2: {hamming_distance(h1, h2)} (should be small)")
    print(f"Distance 1-3: {hamming_distance(h1, h3)} (should be large)")
    print()
    print(f"Similar 1-2: {is_similar(h1, h2)}")
    print(f"Similar 1-3: {is_similar(h1, h3)}")
