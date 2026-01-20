#!/usr/bin/env python3
"""
Attention-Based Filter - 注意力過濾器

基於注意力機制的粒子過濾系統：
- 計算粒子間注意力權重
- 向量相似度計算
- 頻率共振匹配（Schumann 7.83Hz 基準）
- 重要性排序

Author: MR.liou
"""

import math
import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

# 常數定義
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


@dataclass
class AttentionScore:
    """注意力分數"""
    source_id: str
    target_id: str
    score: float
    frequency_match: float
    semantic_similarity: float


class AttentionBasedFilter:
    """
    注意力過濾器
    
    核心功能：
    1. 計算粒子間注意力權重
    2. 基於相似度過濾
    3. 按重要性排序
    4. 頻率共振匹配
    """
    
    def __init__(
        self,
        dimension: int = 64,
        num_heads: int = 8,
        similarity_threshold: float = 0.75
    ):
        self.dimension = dimension
        self.num_heads = num_heads
        self.head_dim = dimension // num_heads
        self.similarity_threshold = similarity_threshold
        self.scale = 1.0 / math.sqrt(self.head_dim)
    
    def compute_attention(
        self,
        particles: List[Dict],
        use_frequency: bool = True
    ) -> Dict[str, List[AttentionScore]]:
        """
        計算粒子間注意力權重
        
        Args:
            particles: 粒子列表
            use_frequency: 是否使用頻率共振
            
        Returns:
            {particle_id: [AttentionScore, ...]} 每個粒子的注意力分數
        """
        attention_map = {}
        
        # 為每個粒子生成向量表示
        particle_vectors = {}
        for particle in particles:
            vector = self._particleto_vector(particle, use_frequency)
            particle_vectors[particle['id']] = vector
        
        # 計算兩兩之間的注意力
        for i, source_particle in enumerate(particles):
            source_id = source_particle['id']
            source_vec = particle_vectors[source_id]
            scores = []
            
            for j, target_particle in enumerate(particles):
                if i == j:
                    continue  # 跳過自己
                
                target_id = target_particle['id']
                target_vec = particle_vectors[target_id]
                
                # 計算餘弦相似度
                similarity = self._cosine_similarity(source_vec, target_vec)
                
                # 計算頻率匹配度
                freq_match = 1.0
                if use_frequency:
                    freq_match = self._frequency_resonance(
                        source_particle.get('layer', 'L7'),
                        target_particle.get('layer', 'L7')
                    )
                
                # 綜合分數
                attention_score = similarity * freq_match
                
                scores.append(AttentionScore(
                    source_id=source_id,
                    target_id=target_id,
                    score=attention_score,
                    frequency_match=freq_match,
                    semantic_similarity=similarity
                ))
            
            # 按分數排序
            scores.sort(key=lambda x: x.score, reverse=True)
            attention_map[source_id] = scores
        
        return attention_map
    
    def filter_by_similarity(
        self,
        particles: List[Dict],
        query_particle: Dict,
        threshold: Optional[float] = None,
        top_k: int = 10
    ) -> List[Tuple[Dict, float]]:
        """
        基於相似度過濾粒子
        
        Args:
            particles: 候選粒子列表
            query_particle: 查詢粒子
            threshold: 相似度閾值（不指定則使用默認值）
            top_k: 返回前 k 個
            
        Returns:
            [(粒子, 相似度), ...] 按相似度排序
        """
        threshold = threshold or self.similarity_threshold
        
        # 生成查詢向量
        query_vec = self._particle_to_vector(query_particle, use_frequency=True)
        
        # 計算所有粒子的相似度
        similarities = []
        for particle in particles:
            if particle['id'] == query_particle['id']:
                continue  # 跳過自己
            
            particle_vec = self._particle_to_vector(particle, use_frequency=True)
            similarity = self._cosine_similarity(query_vec, particle_vec)
            
            if similarity >= threshold:
                similarities.append((particle, similarity))
        
        # 排序並返回 top-k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def rank_by_importance(
        self,
        particles: List[Dict],
        attention_map: Optional[Dict] = None
    ) -> List[Tuple[Dict, float]]:
        """
        按重要性排序粒子
        
        重要性計算：
        - 粒子自身的 importance 分數
        - 被其他粒子注意的程度（入度）
        - 複雜度
        - 模式匹配數量
        
        Args:
            particles: 粒子列表
            attention_map: 可選的注意力映射
            
        Returns:
            [(粒子, 重要性分數), ...] 按重要性排序
        """
        importance_scores = []
        
        # 計算入度（被其他粒子注意的次數）
        in_degree = {p['id']: 0 for p in particles}
        if attention_map:
            for source_id, scores in attention_map.items():
                for score in scores:
                    if score.score > self.similarity_threshold:
                        in_degree[score.target_id] += 1
        
        # 計算綜合重要性
        max_in_degree = max(in_degree.values()) if in_degree else 1
        
        for particle in particles:
            # 組合多個因素
            intrinsic_importance = particle.get('importance', 0.5)
            attention_importance = in_degree.get(particle['id'], 0) / max(max_in_degree, 1)
            pattern_importance = len(particle.get('patterns', [])) / 10.0  # 正規化
            
            # 加權平均
            total_importance = (
                intrinsic_importance * 0.4 +
                attention_importance * 0.3 +
                pattern_importance * 0.3
            )
            
            importance_scores.append((particle, total_importance))
        
        # 排序
        importance_scores.sort(key=lambda x: x[1], reverse=True)
        return importance_scores
    
    def _particle_to_vector(
        self,
        particle: Dict,
        use_frequency: bool = True
    ) -> np.ndarray:
        """
        將粒子轉換為向量表示
        
        使用以下特徵：
        - SimHash 的位元（前 64 位）
        - 頻率（如果啟用）
        - 模式特徵
        """
        vector = np.zeros(self.dimension, dtype=np.float32)
        
        # SimHash 特徵（前 64 位）
        simhash = particle.get('simhash', '0' * 16)
        try:
            simhash_int = int(simhash, 16)
            for i in range(min(64, self.dimension)):
                if (simhash_int >> i) & 1:
                    vector[i] = 1.0
                else:
                    vector[i] = -1.0
        except:
            pass
        
        # 頻率特徵（如果向量維度 > 64）
        if use_frequency and self.dimension > 64:
            layer = particle.get('layer', 'L7')
            freq = FREQ.get(layer, SCHUMANN)
            
            # 使用頻率生成諧波特徵
            for i in range(64, min(self.dimension, 128)):
                phase = (freq * (i - 63)) % (2 * math.pi)
                harmonic = math.sin(phase * PHI) * math.cos(phase / PHI)
                vector[i] = harmonic
        
        # 正規化
        norm = np.linalg.norm(vector)
        if norm > 0:
            vector = vector / norm
        
        return vector
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """計算餘弦相似度"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def _frequency_resonance(self, layer1: str, layer2: str) -> float:
        """
        計算頻率共振度
        
        基於 Schumann 共振和黃金比例
        頻率越接近，共振度越高
        """
        freq1 = FREQ.get(layer1, SCHUMANN)
        freq2 = FREQ.get(layer2, SCHUMANN)
        
        # 計算頻率比
        ratio = min(freq1, freq2) / max(freq1, freq2)
        
        # 檢查是否為黃金比例的諧波
        phi_harmonic = abs(ratio - (1 / PHI))
        if phi_harmonic < 0.1:
            return 1.0  # 完美共振
        
        # 普通共振度
        return ratio
    
    def multi_head_attention(
        self,
        particles: List[Dict],
        head_index: int = 0
    ) -> Dict[str, List[AttentionScore]]:
        """
        多頭注意力計算
        
        Args:
            particles: 粒子列表
            head_index: 注意力頭索引（0 到 num_heads-1）
            
        Returns:
            注意力分數映射
        """
        # 簡化實現：每個頭使用不同的特徵子集
        head_start = head_index * self.head_dim
        head_end = head_start + self.head_dim
        
        attention_map = {}
        
        for i, source_particle in enumerate(particles):
            source_id = source_particle['id']
            source_vec = self._particle_to_vector(source_particle)
            source_head = source_vec[head_start:head_end]
            
            scores = []
            
            for j, target_particle in enumerate(particles):
                if i == j:
                    continue
                
                target_id = target_particle['id']
                target_vec = self._particle_to_vector(target_particle)
                target_head = target_vec[head_start:head_end]
                
                # 計算注意力分數
                attention_score = np.dot(source_head, target_head) * self.scale
                
                scores.append(AttentionScore(
                    source_id=source_id,
                    target_id=target_id,
                    score=attention_score,
                    frequency_match=1.0,
                    semantic_similarity=attention_score
                ))
            
            # Softmax
            scores = self._apply_softmax(scores)
            attention_map[source_id] = scores
        
        return attention_map
    
    def _apply_softmax(self, scores: List[AttentionScore]) -> List[AttentionScore]:
        """應用 Softmax 正規化"""
        if not scores:
            return scores
        
        # 數值穩定的 Softmax
        max_score = max(s.score for s in scores)
        exp_scores = [math.exp(s.score - max_score) for s in scores]
        sum_exp = sum(exp_scores)
        
        if sum_exp > 0:
            for i, score in enumerate(scores):
                score.score = exp_scores[i] / sum_exp
        
        return scores
    
    def identify_key_moments(
        self,
        particles: List[Dict],
        attention_map: Dict,
        threshold: float = 0.8
    ) -> List[Dict]:
        """
        識別關鍵時刻（高注意力粒子）
        
        Args:
            particles: 粒子列表
            attention_map: 注意力映射
            threshold: 關鍵時刻閾值
            
        Returns:
            關鍵粒子列表
        """
        key_particles = []
        
        for particle in particles:
            particle_id = particle['id']
            
            # 計算該粒子被注意的平均分數
            attention_scores = []
            for source_id, scores in attention_map.items():
                for score in scores:
                    if score.target_id == particle_id:
                        attention_scores.append(score.score)
            
            if attention_scores:
                avg_attention = sum(attention_scores) / len(attention_scores)
                
                if avg_attention >= threshold:
                    key_particles.append({
                        'particle': particle,
                        'attention_score': avg_attention,
                        'mentioned_by': len(attention_scores)
                    })
        
        # 按注意力分數排序
        key_particles.sort(key=lambda x: x['attention_score'], reverse=True)
        
        return key_particles


# 測試
if __name__ == '__main__':
    import json
    
    # 創建測試粒子
    test_particles = [
        {
            'id': 'particle_1',
            'simhash': 'a1b2c3d4e5f67890',
            'layer': 'L2',
            'importance': 0.9,
            'patterns': ['attention_mechanism', 'neural_network'],
            'content': 'attention implementation'
        },
        {
            'id': 'particle_2',
            'simhash': 'a1b2c3d4e5f67891',
            'layer': 'L2',
            'importance': 0.85,
            'patterns': ['attention_mechanism'],
            'content': 'attention variant'
        },
        {
            'id': 'particle_3',
            'simhash': 'f1e2d3c4b5a67890',
            'layer': 'L4',
            'importance': 0.6,
            'patterns': ['memory_system'],
            'content': 'memory storage'
        }
    ]
    
    # 創建過濾器
    filter_engine = AttentionBasedFilter(
        dimension=64,
        num_heads=8,
        similarity_threshold=0.75
    )
    
    # 計算注意力
    attention_map = filter_engine.compute_attention(test_particles)
    
    print("=== Attention Scores ===")
    for source_id, scores in attention_map.items():
        print(f"\n{source_id}:")
        for score in scores[:2]:  # 顯示前 2 個
            print(f"  -> {score.target_id}: {score.score:.3f} "
                  f"(sim={score.semantic_similarity:.3f}, freq={score.frequency_match:.3f})")
    
    # 重要性排序
    ranked = filter_engine.rank_by_importance(test_particles, attention_map)
    
    print("\n=== Importance Ranking ===")
    for particle, importance in ranked:
        print(f"{particle['id']}: {importance:.3f}")
    
    # 相似度過濾
    similar = filter_engine.filter_by_similarity(
        test_particles,
        test_particles[0],
        threshold=0.5,
        top_k=2
    )
    
    print("\n=== Similar Particles ===")
    for particle, similarity in similar:
        print(f"{particle['id']}: {similarity:.3f}")
