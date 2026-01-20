#!/usr/bin/env python3
"""
Particle Memory Manager - MrLiouWord 粒子化記憶管理

整合 SimHash64 和 Merkle Chain 的粒子記憶系統

Features:
- 代碼片段轉換為粒子
- SimHash64 語意指紋去重
- Merkle Chain 完整性驗證
- 七層記憶存儲（L1-L7）
- 粒子型態分類

Author: MR.liou
"""

import os
import sys
import json
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# 導入核心模組
sys.path.append(os.path.join(os.path.dirname(__file__), '../../core'))
from simhash64 import simhash64, hamming_distance, is_similar
from merkle import MerkleChain, sha256_str

# 常數定義 - 與 index.ts 對應
PHI = 1.618033988749895
SCHUMANN = 7.83

FREQ = {
    "L∞": SCHUMANN * PHI ** 7,
    "L7": SCHUMANN * PHI ** 6,
    "L6": SCHUMANN * PHI ** 5,
    "L5": SCHUMANN * PHI ** 4,
    "L4": SCHUMANN * PHI ** 3,
    "L3": SCHUMANN * PHI ** 2,
    "L2": SCHUMANN * PHI,
    "L1": SCHUMANN,
    "L0": SCHUMANN / PHI
}

# 副檔名對應層級
EXT_LAYER = {
    ".txt": "L1", ".md": "L1", ".json": "L1", ".csv": "L1",
    ".py": "L2", ".ts": "L2", ".js": "L2", ".jsx": "L2", ".tsx": "L2", 
    ".rs": "L2", ".go": "L2",
    ".zip": "L3", ".tar": "L3", ".gz": "L3", ".tgz": "L3",
    ".yaml": "L4", ".yml": "L4", ".toml": "L4", ".ini": "L4",
    ".persona": "L5", ".profile": "L5", ".policy": "L5",
    ".image": "L6", ".boot": "L6", ".dockerfile": "L6",
    ".pdf": "L7", ".docx": "L7", ".doc": "L7", ".pptx": "L7"
}


@dataclass
class CodeParticle:
    """代碼粒子"""
    id: str                      # 粒子 ID
    content: str                 # 內容
    simhash: str                 # SimHash64 指紋
    layer: str                   # 層級 (L1-L7)
    particle_type: str           # 粒子類型 (fx.adj, fx.noun, etc.)
    language: str                # 語言 (Python, TypeScript, etc.)
    file_path: str               # 檔案路徑
    line_start: int              # 起始行
    line_end: int                # 結束行
    patterns: List[str]          # 邏輯模式標籤
    importance: float            # 重要性分數 (0-1)
    timestamp: int               # 時間戳
    merkle: str                  # Merkle 雜湊
    prev: str                    # 前一粒子 Merkle
    meta: Dict                   # 元資料


class ParticleMemoryManager:
    """
    粒子化記憶管理器
    
    核心功能：
    1. 將代碼片段轉換為粒子
    2. SimHash64 去重
    3. Merkle Chain 完整性驗證
    4. 層級分類存儲
    """
    
    def __init__(self, storage_path: str = './particle_memory'):
        self.storage_path = storage_path
        self.merkle_chain = MerkleChain(os.path.join(storage_path, 'chain'))
        
        # 為每個層級創建存儲目錄
        for layer in ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]:
            layer_path = os.path.join(storage_path, layer)
            os.makedirs(layer_path, exist_ok=True)
        
        # 載入現有粒子索引
        self.index_file = os.path.join(storage_path, 'particle_index.json')
        self.particles_by_hash = self._load_index()
    
    def _load_index(self) -> Dict[str, str]:
        """載入粒子索引 (SimHash -> Particle ID)"""
        if os.path.exists(self.index_file):
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_index(self):
        """保存粒子索引"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.particles_by_hash, f, indent=2, ensure_ascii=False)
    
    def particlize_code(
        self,
        content: str,
        language: str,
        file_path: str,
        line_start: int = 1,
        line_end: int = 1,
        patterns: List[str] = None,
        particle_type: str = "fx.noun",
        importance: float = 0.5
    ) -> CodeParticle:
        """
        將代碼片段轉換為粒子
        
        Args:
            content: 代碼內容
            language: 編程語言
            file_path: 檔案路徑
            line_start: 起始行號
            line_end: 結束行號
            patterns: 邏輯模式標籤
            particle_type: 粒子類型
            importance: 重要性分數
            
        Returns:
            CodeParticle 粒子對象
        """
        import uuid
        import time
        
        # 計算 SimHash
        content_hash = simhash64(content)
        
        # 確定層級
        ext = os.path.splitext(file_path)[1]
        layer = EXT_LAYER.get(ext, "L7")
        
        # 生成粒子 ID
        particle_id = str(uuid.uuid4())
        timestamp = int(time.time() * 1000)
        
        # 獲取前一粒子的 Merkle
        prev = self.merkle_chain.head
        
        # 計算 Merkle 雜湊
        merkle_input = f"{content}{content_hash}{timestamp}{prev}"
        merkle = sha256_str(merkle_input)
        
        particle = CodeParticle(
            id=particle_id,
            content=content,
            simhash=content_hash,
            layer=layer,
            particle_type=particle_type,
            language=language,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            patterns=patterns or [],
            importance=importance,
            timestamp=timestamp,
            merkle=merkle,
            prev=prev,
            meta={
                'frequency': FREQ[layer],
                'source': 'intelligent_repo_sync'
            }
        )
        
        return particle
    
    def deduplicate(
        self,
        particles: List[CodeParticle],
        threshold: int = 3
    ) -> Tuple[List[CodeParticle], List[CodeParticle]]:
        """
        基於 SimHash 去重
        
        Args:
            particles: 粒子列表
            threshold: Hamming 距離閾值（預設 3）
            
        Returns:
            (唯一粒子列表, 重複粒子列表)
        """
        unique = []
        duplicates = []
        
        for particle in particles:
            is_dup = False
            
            # 檢查是否與已存在粒子相似
            for existing_hash in self.particles_by_hash.keys():
                if hamming_distance(particle.simhash, existing_hash) <= threshold:
                    is_dup = True
                    duplicates.append(particle)
                    break
            
            # 檢查是否與本批次中的粒子相似
            if not is_dup:
                for unique_particle in unique:
                    if hamming_distance(particle.simhash, unique_particle.simhash) <= threshold:
                        is_dup = True
                        duplicates.append(particle)
                        break
            
            if not is_dup:
                unique.append(particle)
        
        return unique, duplicates
    
    def store_particle(self, particle: CodeParticle) -> bool:
        """
        存儲粒子到對應層級
        
        Args:
            particle: 粒子對象
            
        Returns:
            是否成功
        """
        try:
            # 保存到層級目錄
            layer_path = os.path.join(self.storage_path, particle.layer)
            particle_file = os.path.join(layer_path, f"{particle.id}.json")
            
            with open(particle_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(particle), f, indent=2, ensure_ascii=False)
            
            # 更新索引
            self.particles_by_hash[particle.simhash] = particle.id
            self._save_index()
            
            # 提交到 Merkle Chain
            self.merkle_chain.commit(
                content=particle.content,
                simhash=particle.simhash,
                tags=particle.patterns,
                layer=particle.layer,
                meta={
                    'particle_id': particle.id,
                    'file_path': particle.file_path,
                    'language': particle.language,
                    'particle_type': particle.particle_type
                }
            )
            
            return True
            
        except Exception as e:
            print(f"存儲粒子失敗: {e}")
            return False
    
    def query_by_pattern(
        self,
        pattern: str,
        layer: Optional[str] = None,
        limit: int = 100
    ) -> List[CodeParticle]:
        """
        根據邏輯模式查詢粒子
        
        Args:
            pattern: 模式標籤
            layer: 可選層級過濾
            limit: 結果數量限制
            
        Returns:
            匹配的粒子列表
        """
        results = []
        
        # 確定搜索目錄
        search_dirs = [os.path.join(self.storage_path, layer)] if layer else \
                      [os.path.join(self.storage_path, f"L{i}") for i in range(1, 8)]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            for filename in os.listdir(search_dir):
                if not filename.endswith('.json'):
                    continue
                
                particle_file = os.path.join(search_dir, filename)
                try:
                    with open(particle_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    # 檢查模式匹配
                    if pattern in data.get('patterns', []):
                        particle = CodeParticle(**data)
                        results.append(particle)
                        
                        if len(results) >= limit:
                            return results
                            
                except Exception as e:
                    print(f"讀取粒子失敗 {particle_file}: {e}")
        
        return results
    
    def find_similar(
        self,
        query_content: str,
        threshold: int = 3,
        layer: Optional[str] = None,
        limit: int = 10
    ) -> List[Tuple[CodeParticle, int]]:
        """
        查找相似粒子
        
        Args:
            query_content: 查詢內容
            threshold: 相似度閾值
            layer: 可選層級過濾
            limit: 結果數量限制
            
        Returns:
            [(粒子, Hamming距離), ...] 按距離排序
        """
        query_hash = simhash64(query_content)
        results = []
        
        # 確定搜索目錄
        search_dirs = [os.path.join(self.storage_path, layer)] if layer else \
                      [os.path.join(self.storage_path, f"L{i}") for i in range(1, 8)]
        
        for search_dir in search_dirs:
            if not os.path.exists(search_dir):
                continue
            
            for filename in os.listdir(search_dir):
                if not filename.endswith('.json'):
                    continue
                
                particle_file = os.path.join(search_dir, filename)
                try:
                    with open(particle_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 計算 Hamming 距離
                    dist = hamming_distance(query_hash, data['simhash'])
                    
                    if dist <= threshold:
                        particle = CodeParticle(**data)
                        results.append((particle, dist))
                        
                except Exception as e:
                    print(f"讀取粒子失敗 {particle_file}: {e}")
        
        # 按距離排序
        results.sort(key=lambda x: x[1])
        return results[:limit]
    
    def verify_integrity(self) -> Tuple[bool, List[str]]:
        """
        驗證粒子記憶鏈的完整性
        
        Returns:
            (是否有效, 錯誤列表)
        """
        return self.merkle_chain.verify()
    
    def get_stats(self) -> Dict:
        """
        獲取粒子記憶統計
        
        Returns:
            統計資訊字典
        """
        stats = {
            'total_particles': len(self.particles_by_hash),
            'by_layer': {},
            'merkle_valid': self.verify_integrity()[0]
        }
        
        for layer in ["L1", "L2", "L3", "L4", "L5", "L6", "L7"]:
            layer_path = os.path.join(self.storage_path, layer)
            if os.path.exists(layer_path):
                count = len([f for f in os.listdir(layer_path) if f.endswith('.json')])
                stats['by_layer'][layer] = count
        
        return stats


# 測試
if __name__ == '__main__':
    # 建立記憶管理器
    manager = ParticleMemoryManager('./test_particle_memory')
    
    # 創建測試粒子
    test_code = """
def attention_mechanism(query, key, value):
    # 計算注意力權重
    scores = query @ key.T
    weights = softmax(scores)
    return weights @ value
"""
    
    particle = manager.particlize_code(
        content=test_code,
        language="Python",
        file_path="test/attention.py",
        line_start=1,
        line_end=6,
        patterns=["attention_mechanism", "neural_network"],
        particle_type="fx.flow",
        importance=0.9
    )
    
    print(f"Created particle: {particle.id}")
    print(f"SimHash: {particle.simhash}")
    print(f"Layer: {particle.layer}")
    print(f"Frequency: {particle.meta['frequency']:.2f} Hz")
    
    # 存儲粒子
    success = manager.store_particle(particle)
    print(f"\nStored: {success}")
    
    # 查詢
    results = manager.query_by_pattern("attention_mechanism")
    print(f"\nQuery results: {len(results)}")
    
    # 統計
    stats = manager.get_stats()
    print(f"\nStats: {json.dumps(stats, indent=2)}")
