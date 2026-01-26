#!/usr/bin/env python3
"""
Merkle Chain - MrLiouWord 完整性驗證系統

核心理念：怎麼過去，就怎麼回來
- 每筆記憶都有 prev 指向前一狀態
- merkle_root 可驗證整體完整性
- 支援完整回溯與還原

Author: MR.liou
"""

import os
import json
import time
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict

def sha256(data: bytes) -> str:
    """計算 SHA256 雜湊"""
    return hashlib.sha256(data).hexdigest()

def sha256_str(s: str) -> str:
    """字串 SHA256"""
    return sha256(s.encode('utf-8'))

def sha256_file(path: str) -> str:
    """檔案 SHA256"""
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def merkle_fold(leaves: List[str]) -> str:
    """
    Merkle Tree 折疊
    
    將葉子節點折疊成單一根節點
    
    Args:
        leaves: 葉子雜湊列表（hex）
        
    Returns:
        Merkle 根雜湊
    """
    if not leaves:
        return sha256(b'')
    
    # 轉換為 bytes
    layer = [bytes.fromhex(x) for x in leaves]
    
    # 逐層折疊
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else a  # 奇數時自己配對
            combined = hashlib.sha256(a + b).digest()
            next_layer.append(combined)
        layer = next_layer
    
    return layer[0].hex()


@dataclass
class MemoryEntry:
    """記憶條目"""
    id: str
    content: str
    simhash: str
    timestamp: int
    merkle: str
    prev: str
    tags: List[str]
    layer: str
    meta: Dict


class MerkleChain:
    """
    Merkle Chain 記憶鏈
    
    每筆記憶都連結到前一筆，形成可驗證的鏈條
    """
    
    def __init__(self, storage_path: str = './memory_chain'):
        self.storage_path = storage_path
        self.entries_file = os.path.join(storage_path, 'entries.jsonl')
        self.head_file = os.path.join(storage_path, 'head.txt')
        
        os.makedirs(storage_path, exist_ok=True)
        
        # 載入當前頭部
        self.head = self._load_head()
    
    def _load_head(self) -> str:
        """載入鏈頭"""
        if os.path.exists(self.head_file):
            with open(self.head_file, 'r') as f:
                return f.read().strip()
        return '0' * 64  # 創世區塊的 prev
    
    def _save_head(self, merkle: str):
        """保存鏈頭"""
        with open(self.head_file, 'w') as f:
            f.write(merkle)
        self.head = merkle
    
    def commit(
        self,
        content: str,
        simhash: str,
        tags: List[str] = None,
        layer: str = 'L7',
        meta: Dict = None
    ) -> MemoryEntry:
        """
        提交新記憶
        
        Args:
            content: 內容
            simhash: SimHash64 指紋
            tags: 標籤
            layer: 層級
            meta: 元資料
            
        Returns:
            新記憶條目
        """
        import uuid
        
        entry_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        prev = self.head
        
        # 計算 Merkle 雜湊
        merkle_input = f"{content}{simhash}{timestamp}{prev}"
        merkle = sha256_str(merkle_input)
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            simhash=simhash,
            timestamp=timestamp,
            merkle=merkle,
            prev=prev,
            tags=tags or [],
            layer=layer,
            meta=meta or {}
        )
        
        # 寫入檔案
        with open(self.entries_file, 'a') as f:
            f.write(json.dumps(asdict(entry), ensure_ascii=False) + '\n')
        
        # 更新頭部
        self._save_head(merkle)
        
        return entry
    
    def verify(self) -> Tuple[bool, List[str]]:
        """
        驗證整條鏈的完整性
        
        Returns:
            (是否有效, 錯誤列表)
        """
        errors = []
        
        if not os.path.exists(self.entries_file):
            return True, []
        
        entries = []
        with open(self.entries_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        # 按時間排序
        entries.sort(key=lambda x: x['timestamp'])
        
        prev = '0' * 64  # 創世區塊
        
        for entry in entries:
            # 檢查 prev 連結
            if entry['prev'] != prev:
                errors.append(f"Chain broken at {entry['id']}: expected prev={prev}, got {entry['prev']}")
            
            # 重新計算 merkle
            merkle_input = f"{entry['content']}{entry['simhash']}{entry['timestamp']}{entry['prev']}"
            computed_merkle = sha256_str(merkle_input)
            
            if computed_merkle != entry['merkle']:
                errors.append(f"Merkle mismatch at {entry['id']}: computed={computed_merkle}, stored={entry['merkle']}")
            
            prev = entry['merkle']
        
        return len(errors) == 0, errors
    
    def rollback(self, target_merkle: str) -> bool:
        """
        回滾到指定狀態
        
        Args:
            target_merkle: 目標 Merkle 根
            
        Returns:
            是否成功
        """
        if not os.path.exists(self.entries_file):
            return False
        
        entries = []
        with open(self.entries_file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    entries.append(entry)
                    if entry['merkle'] == target_merkle:
                        break
            else:
                return False  # 找不到目標
        
        # 重寫檔案
        with open(self.entries_file, 'w') as f:
            for entry in entries:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
        
        # 更新頭部
        self._save_head(target_merkle)
        
        return True
    
    def get_history(self, limit: int = 100) -> List[Dict]:
        """取得歷史記錄"""
        if not os.path.exists(self.entries_file):
            return []
        
        entries = []
        with open(self.entries_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        return sorted(entries, key=lambda x: x['timestamp'], reverse=True)[:limit]
    
    def build_merkle_root(self) -> str:
        """建立整體 Merkle 根"""
        if not os.path.exists(self.entries_file):
            return sha256(b'')
        
        leaves = []
        with open(self.entries_file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    leaves.append(entry['merkle'])
        
        return merkle_fold(sorted(leaves))


def build_bundle_merkle(bundle_dir: str, file_list: List[str]) -> Dict:
    """
    為 bundle 目錄建立 Merkle 驗證
    
    Args:
        bundle_dir: bundle 目錄路徑
        file_list: 要驗證的檔案列表
        
    Returns:
        包含 merkle_root 和檔案資訊的字典
    """
    leaves = []
    file_meta = {}
    
    for fn in file_list:
        fp = os.path.join(bundle_dir, fn)
        if os.path.exists(fp):
            h = sha256_file(fp)
            leaves.append(h)
            file_meta[fn] = {
                'sha256': h,
                'bytes': os.path.getsize(fp)
            }
    
    root = merkle_fold(sorted(leaves))
    
    return {
        'merkle_root': root,
        'leaves': sorted(leaves),
        'files': file_meta
    }


# 測試
if __name__ == '__main__':
    from simhash64 import simhash64
    
    # 建立鏈
    chain = MerkleChain('./test_chain')
    
    # 提交記憶
    texts = [
        "夥伴回來吧，我們繼續開發",
        "粒子系統架構已完成",
        "怎麼過去，就怎麼回來"
    ]
    
    for text in texts:
        entry = chain.commit(
            content=text,
            simhash=simhash64(text),
            tags=['test'],
            layer='L7'
        )
        print(f"Committed: {entry.id[:8]}... merkle={entry.merkle[:16]}...")
    
    # 驗證
    valid, errors = chain.verify()
    print(f"\nChain valid: {valid}")
    if errors:
        for e in errors:
            print(f"  Error: {e}")
    
    # 整體 Merkle 根
    root = chain.build_merkle_root()
    print(f"\nOverall Merkle root: {root}")
