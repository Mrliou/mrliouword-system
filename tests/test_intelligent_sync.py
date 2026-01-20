#!/usr/bin/env python3
"""
Test Suite for Intelligent Repository Sync System

測試智能倉庫同步系統的各個組件

Author: MR.liou
"""

import os
import sys
import tempfile
import shutil
import json
import unittest
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.github.logical_extractor import LogicalStructureExtractor
from integrations.github.particle_memory import ParticleMemoryManager
from integrations.github.attention_filter import AttentionBasedFilter
from core.simhash64 import simhash64, hamming_distance, is_similar
from core.merkle import MerkleChain


class TestLogicalStructureExtraction(unittest.TestCase):
    """測試邏輯架構提取"""
    
    def setUp(self):
        self.extractor = LogicalStructureExtractor()
    
    def test_python_extraction(self):
        """測試 Python 代碼提取"""
        code = """
import numpy as np

class AttentionMechanism:
    def __init__(self, dim):
        self.dim = dim
    
    def forward(self, query, key, value):
        scores = query @ key.T
        return self.softmax(scores) @ value
    
    def softmax(self, x):
        return np.exp(x) / np.sum(np.exp(x))
"""
        
        structure = self.extractor.extract_from_code(code, 'python')
        
        # 驗證提取結果
        self.assertIn('AttentionMechanism', structure['concepts'])
        self.assertIn('forward', structure['concepts'])
        self.assertIn('softmax', structure['concepts'])
        
        # 驗證模式識別
        self.assertIn('attention_mechanism', structure['patterns'])
        
        # 驗證函數提取
        functions = [f['name'] for f in structure['functions']]
        self.assertIn('AttentionMechanism', functions)
        self.assertIn('forward', functions)
        
        # 驗證導入
        self.assertTrue(any('numpy' in imp for imp in structure['imports']))
    
    def test_typescript_extraction(self):
        """測試 TypeScript 代碼提取"""
        code = """
import { Vector } from './types';

class ParticleEngine {
    private dimension: number;
    
    constructor(dim: number) {
        this.dimension = dim;
    }
    
    compute(particles: Vector[]): Vector {
        return particles.reduce((acc, p) => acc + p, 0);
    }
}

export default ParticleEngine;
"""
        
        structure = self.extractor.extract_from_code(code, 'typescript')
        
        # 驗證類提取
        classes = [f for f in structure['functions'] if f['type'] == 'class']
        self.assertTrue(len(classes) > 0)
        self.assertEqual(classes[0]['name'], 'ParticleEngine')
        
        # 驗證模式
        self.assertIn('particle_engine', structure['patterns'])
    
    def test_pattern_matching(self):
        """測試邏輯模式匹配"""
        code1 = """
def attention(q, k, v):
    return softmax(q @ k.T) @ v
"""
        
        code2 = """
def scaled_attention(query, key, value, scale):
    scores = query @ key.T / scale
    return softmax(scores) @ value
"""
        
        structure1 = self.extractor.extract_from_code(code1, 'python')
        structure2 = self.extractor.extract_from_code(code2, 'python')
        
        # 兩者都應該識別為 attention_mechanism
        self.assertIn('attention_mechanism', structure1['patterns'])
        self.assertIn('attention_mechanism', structure2['patterns'])
        
        # 測試匹配
        matches = self.extractor.match_logical_patterns(
            [structure1],
            [structure2],
            similarity_threshold=0.3
        )
        
        self.assertTrue(len(matches) > 0)
        self.assertIn('attention_mechanism', matches[0]['shared_patterns'])


class TestParticleMemoryDeduplication(unittest.TestCase):
    """測試 SimHash 去重"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = ParticleMemoryManager(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_simhash_computation(self):
        """測試 SimHash 計算"""
        text1 = "夥伴回來吧，我們繼續開發粒子系統"
        text2 = "夥伴回來吧，我們繼續開發粒子架構"
        text3 = "今天天氣很好，適合出門散步"
        
        h1 = simhash64(text1)
        h2 = simhash64(text2)
        h3 = simhash64(text3)
        
        # 相似文本的 Hamming 距離應該小
        dist_similar = hamming_distance(h1, h2)
        dist_different = hamming_distance(h1, h3)
        
        self.assertLess(dist_similar, dist_different)
        self.assertTrue(is_similar(h1, h2, threshold=5))
        self.assertFalse(is_similar(h1, h3, threshold=3))
    
    def test_particle_creation(self):
        """測試粒子創建"""
        code = """
def attention(q, k, v):
    return softmax(q @ k.T) @ v
"""
        
        particle = self.manager.particlize_code(
            content=code,
            language='python',
            file_path='attention.py',
            patterns=['attention_mechanism'],
            importance=0.9
        )
        
        # 驗證粒子屬性
        self.assertEqual(particle.language, 'python')
        self.assertEqual(particle.layer, 'L2')  # .py 檔案應該在 L2
        self.assertIn('attention_mechanism', particle.patterns)
        self.assertEqual(particle.importance, 0.9)
        self.assertIsNotNone(particle.simhash)
        self.assertIsNotNone(particle.merkle)
    
    def test_deduplication(self):
        """測試去重功能"""
        code1 = "def attention(q, k, v): return softmax(q @ k.T) @ v"
        code2 = "def attention(q, k, v): return softmax(q @ k.T) @ v"  # 完全相同
        code3 = "def attention(query, key, value): return softmax(query @ key.T) @ value"  # 相似
        code4 = "def memory_store(data): return db.save(data)"  # 不同
        
        particles = [
            self.manager.particlize_code(code1, 'python', 'a.py', patterns=['attention']),
            self.manager.particlize_code(code2, 'python', 'b.py', patterns=['attention']),
            self.manager.particlize_code(code3, 'python', 'c.py', patterns=['attention']),
            self.manager.particlize_code(code4, 'python', 'd.py', patterns=['memory'])
        ]
        
        unique, duplicates = self.manager.deduplicate(particles, threshold=3)
        
        # 至少應該有去重
        self.assertGreater(len(duplicates), 0)
        self.assertLess(len(unique), len(particles))
    
    def test_particle_storage_and_retrieval(self):
        """測試粒子存儲和檢索"""
        code = "def attention(q, k, v): return softmax(q @ k.T) @ v"
        
        particle = self.manager.particlize_code(
            code, 'python', 'attention.py',
            patterns=['attention_mechanism']
        )
        
        # 存儲
        success = self.manager.store_particle(particle)
        self.assertTrue(success)
        
        # 檢索
        results = self.manager.query_by_pattern('attention_mechanism')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, particle.id)
    
    def test_similarity_search(self):
        """測試相似度搜索"""
        # 存儲一些粒子
        codes = [
            "def attention(q, k, v): return softmax(q @ k.T) @ v",
            "def scaled_attention(q, k, v, scale): return softmax(q @ k.T / scale) @ v",
            "def memory_save(data): return db.save(data)"
        ]
        
        for i, code in enumerate(codes):
            particle = self.manager.particlize_code(
                code, 'python', f'file_{i}.py',
                patterns=['attention' if i < 2 else 'memory']
            )
            self.manager.store_particle(particle)
        
        # 搜索相似代碼
        query = "def attention_forward(query, key, value): return softmax(query @ key.T) @ value"
        similar = self.manager.find_similar(query, threshold=10, limit=5)
        
        # 應該找到相似的 attention 函數
        self.assertGreater(len(similar), 0)


class TestAttentionFiltering(unittest.TestCase):
    """測試注意力過濾"""
    
    def setUp(self):
        self.filter = AttentionBasedFilter(
            dimension=64,
            num_heads=8,
            similarity_threshold=0.75
        )
    
    def test_attention_computation(self):
        """測試注意力計算"""
        particles = [
            {
                'id': 'p1',
                'simhash': 'a1b2c3d4e5f67890',
                'layer': 'L2',
                'importance': 0.9,
                'patterns': ['attention_mechanism'],
                'content': 'attention code'
            },
            {
                'id': 'p2',
                'simhash': 'a1b2c3d4e5f67891',
                'layer': 'L2',
                'importance': 0.85,
                'patterns': ['attention_mechanism'],
                'content': 'attention variant'
            },
            {
                'id': 'p3',
                'simhash': 'f1e2d3c4b5a67890',
                'layer': 'L3',
                'importance': 0.6,
                'patterns': ['memory_system'],
                'content': 'memory code'
            }
        ]
        
        attention_map = self.filter.compute_attention(particles)
        
        # 驗證注意力映射
        self.assertEqual(len(attention_map), 3)
        
        # 每個粒子應該對其他粒子有注意力分數
        for particle_id, scores in attention_map.items():
            self.assertEqual(len(scores), 2)  # 除了自己外的其他粒子
    
    def test_similarity_filtering(self):
        """測試相似度過濾"""
        particles = [
            {'id': 'p1', 'simhash': 'a1b2c3d4e5f67890', 'layer': 'L2', 'importance': 0.9, 'patterns': [], 'content': 'a'},
            {'id': 'p2', 'simhash': 'a1b2c3d4e5f67891', 'layer': 'L2', 'importance': 0.85, 'patterns': [], 'content': 'b'},
            {'id': 'p3', 'simhash': 'f1e2d3c4b5a67890', 'layer': 'L3', 'importance': 0.6, 'patterns': [], 'content': 'c'}
        ]
        
        similar = self.filter.filter_by_similarity(
            particles,
            particles[0],
            threshold=0.5,
            top_k=2
        )
        
        # 應該找到相似粒子
        self.assertGreater(len(similar), 0)
        
        # 結果應該按相似度排序
        if len(similar) >= 2:
            self.assertGreaterEqual(similar[0][1], similar[1][1])
    
    def test_importance_ranking(self):
        """測試重要性排序"""
        particles = [
            {'id': 'p1', 'simhash': 'a1b2c3d4e5f67890', 'layer': 'L2', 'importance': 0.5, 'patterns': ['a', 'b'], 'content': 'x'},
            {'id': 'p2', 'simhash': 'a1b2c3d4e5f67891', 'layer': 'L2', 'importance': 0.9, 'patterns': ['a'], 'content': 'y'},
            {'id': 'p3', 'simhash': 'f1e2d3c4b5a67890', 'layer': 'L3', 'importance': 0.7, 'patterns': ['a', 'b', 'c'], 'content': 'z'}
        ]
        
        ranked = self.filter.rank_by_importance(particles)
        
        # 驗證排序
        self.assertEqual(len(ranked), 3)
        
        # 重要性應該遞減
        for i in range(len(ranked) - 1):
            self.assertGreaterEqual(ranked[i][1], ranked[i+1][1])
    
    def test_frequency_resonance(self):
        """測試頻率共振"""
        # 同層級應該有高共振度
        resonance_same = self.filter._frequency_resonance('L2', 'L2')
        self.assertEqual(resonance_same, 1.0)
        
        # 不同層級應該有低共振度
        resonance_diff = self.filter._frequency_resonance('L1', 'L7')
        self.assertLess(resonance_diff, 1.0)


class TestMerkleChainIntegrity(unittest.TestCase):
    """測試 Merkle 鏈完整性"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.chain = MerkleChain(self.temp_dir)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_merkle_commit(self):
        """測試 Merkle 提交"""
        content = "test memory content"
        hash_value = simhash64(content)
        
        entry = self.chain.commit(
            content=content,
            simhash=hash_value,
            tags=['test'],
            layer='L7'
        )
        
        # 驗證條目
        self.assertIsNotNone(entry.id)
        self.assertIsNotNone(entry.merkle)
        self.assertEqual(entry.content, content)
        self.assertEqual(entry.simhash, hash_value)
    
    def test_merkle_chain_verification(self):
        """測試 Merkle 鏈驗證"""
        # 提交多個條目
        for i in range(5):
            content = f"memory entry {i}"
            self.chain.commit(
                content=content,
                simhash=simhash64(content),
                tags=[f'tag{i}'],
                layer='L7'
            )
        
        # 驗證鏈的完整性
        valid, errors = self.chain.verify()
        
        self.assertTrue(valid)
        self.assertEqual(len(errors), 0)
    
    def test_merkle_rollback(self):
        """測試 Merkle 回滾"""
        # 提交幾個條目
        entries = []
        for i in range(3):
            content = f"entry {i}"
            entry = self.chain.commit(
                content=content,
                simhash=simhash64(content),
                tags=['test'],
                layer='L7'
            )
            entries.append(entry)
        
        # 回滾到第二個條目
        target_merkle = entries[1].merkle
        success = self.chain.rollback(target_merkle)
        
        self.assertTrue(success)
        
        # 驗證歷史
        history = self.chain.get_history()
        self.assertEqual(len(history), 2)


class TestCrossLanguageExtraction(unittest.TestCase):
    """測試跨語言提取"""
    
    def setUp(self):
        self.extractor = LogicalStructureExtractor()
    
    def test_multiple_languages(self):
        """測試多語言支持"""
        test_cases = [
            ('python', 'def attention(q, k, v): pass'),
            ('typescript', 'function attention(q: any, k: any, v: any) {}'),
            ('javascript', 'const attention = (q, k, v) => {}'),
            ('shell', 'function attention() { echo "test"; }'),
            ('markdown', '# Attention Mechanism\n\n```python\ndef attention(): pass\n```')
        ]
        
        for language, code in test_cases:
            structure = self.extractor.extract_from_code(code, language)
            
            # 所有語言都應該能提取結構
            self.assertIsNotNone(structure)
            self.assertIn('concepts', structure)
            self.assertIn('functions', structure)
            self.assertIn('patterns', structure)


def run_tests():
    """運行所有測試"""
    # 創建測試套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有測試類
    suite.addTests(loader.loadTestsFromTestCase(TestLogicalStructureExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestParticleMemoryDeduplication))
    suite.addTests(loader.loadTestsFromTestCase(TestAttentionFiltering))
    suite.addTests(loader.loadTestsFromTestCase(TestMerkleChainIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossLanguageExtraction))
    
    # 運行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回狀態碼
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
