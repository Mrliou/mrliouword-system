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
    normalized = text.lower().replace('\n', ' ').strip()
    if len(normalized) < 3:
        return '0' * 16
    
    # 生成 3-gram shingles
    shingles: List[str] = []
    for i in range(len(normalized) - 2):
        shingles.append(normalized[i:i+3])
    
    # 初始化 64 維向量
    v = [0] * 64
    
    # FNV-1a 雜湊每個 shingle
    FNV_PRIME = 1099511628211
    FNV_OFFSET = 14695981039346656037
    
    for shingle in shingles:
        h = FNV_OFFSET
        for char in shingle.encode('utf-8'):
            h ^= char
            h = (h * FNV_PRIME) & 0xFFFFFFFFFFFFFFFF
        
        # 更新向量
        for i in range(64):
            if (h >> i) & 1:
                v[i] += 1
            else:
                v[i] -= 1
    
    # 生成指紋
    fingerprint = 0
    for i in range(64):
        if v[i] > 0:
            fingerprint |= (1 << i)
    
    return format(fingerprint, '016x')


def hamming_distance(a: str, b: str) -> int:
    """
    計算兩個 SimHash 的 Hamming 距離
    
    Args:
        a: 第一個 SimHash (hex)
        b: 第二個 SimHash (hex)
        
    Returns:
        Hamming 距離（不同位元數）
    """
    x = int(a, 16) ^ int(b, 16)
    distance = 0
    while x:
        distance += x & 1
        x >>= 1
    return distance


def is_similar(a: str, b: str, threshold: int = 3) -> bool:
    """
    判斷兩個文本是否語意相似
    
    Args:
        a: 第一個 SimHash
        b: 第二個 SimHash
        threshold: Hamming 距離閾值（預設 3）
        
    Returns:
        是否相似
    """
    return hamming_distance(a, b) <= threshold


def find_similar(query: str, candidates: List[str], threshold: int = 3) -> List[tuple]:
    """
    從候選列表中找出相似文本
    
    Args:
        query: 查詢文本
        candidates: 候選文本列表
        threshold: 相似度閾值
        
    Returns:
        [(文本, SimHash, 距離), ...] 按距離排序
    """
    query_hash = simhash64(query)
    results = []
    
    for candidate in candidates:
        candidate_hash = simhash64(candidate)
        dist = hamming_distance(query_hash, candidate_hash)
        if dist <= threshold:
            results.append((candidate, candidate_hash, dist))
    
    return sorted(results, key=lambda x: x[2])


def deduplicate(texts: List[str], threshold: int = 3) -> List[str]:
    """
    去除重複文本
    
    Args:
        texts: 文本列表
        threshold: 相似度閾值
        
    Returns:
        去重後的文本列表
    """
    seen_hashes: Set[str] = set()
    unique_texts: List[str] = []
    
    for text in texts:
        text_hash = simhash64(text)
        is_dup = False
        
        for seen_hash in seen_hashes:
            if hamming_distance(text_hash, seen_hash) <= threshold:
                is_dup = True
                break
        
        if not is_dup:
            seen_hashes.add(text_hash)
            unique_texts.append(text)
    
    return unique_texts


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
