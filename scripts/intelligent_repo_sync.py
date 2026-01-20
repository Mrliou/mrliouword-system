#!/usr/bin/env python3
"""
Intelligent Repository Sync - 智能倉庫同步引擎

基於邏輯架構原理的全域智能同步系統

Features:
- 全域語意掃描（不限於指定檔案）
- 邏輯架構模式匹配
- 粒子化記憶存儲
- 注意力機制過濾
- SimHash64 去重
- Merkle Chain 完整性驗證

Author: MR.liou
"""

import os
import sys
import yaml
import argparse
import subprocess
import tempfile
import shutil
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime

# 添加項目根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.github.logical_extractor import LogicalStructureExtractor
from integrations.github.particle_memory import ParticleMemoryManager
from integrations.github.attention_filter import AttentionBasedFilter


class IntelligentRepoSync:
    """
    智能倉庫同步管理器
    
    核心流程：
    1. 克隆遠端倉庫
    2. 全域掃描提取邏輯架構
    3. 與本地架構匹配
    4. 轉換為粒子並去重
    5. 通過注意力過濾
    6. 存儲到粒子記憶
    """
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: 配置檔案路徑
        """
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 初始化組件
        self.extractor = LogicalStructureExtractor()
        
        settings = self.config.get('settings', {})
        particle_config = settings.get('particle_memory', {})
        attention_config = settings.get('attention', {})
        
        memory_path = particle_config.get('storage_path', './particle_memory')
        self.memory = ParticleMemoryManager(memory_path)
        
        self.attention = AttentionBasedFilter(
            dimension=attention_config.get('dimension', 64),
            num_heads=attention_config.get('num_heads', 8),
            similarity_threshold=attention_config.get('similarity_threshold', 0.75)
        )
        
        self.scan_mode = settings.get('scan_mode', 'global')
        self.sync_strategy = settings.get('sync_strategy', 'logical_pattern')
        
        # 語言擴展名映射
        self.lang_extensions = {
            'python': ['.py'],
            'typescript': ['.ts', '.tsx'],
            'javascript': ['.js', '.jsx'],
            'shell': ['.sh', '.bash'],
            'markdown': ['.md']
        }
    
    def scan_repository(
        self,
        repo_url: str,
        branch: str = 'main',
        patterns: Optional[List[str]] = None
    ) -> Dict:
        """
        全域掃描倉庫
        
        Args:
            repo_url: 倉庫 URL
            branch: 分支名稱
            patterns: 可選的邏輯模式過濾
            
        Returns:
            掃描結果字典
        """
        print(f"🔍 開始掃描倉庫: {repo_url}")
        
        # 創建臨時目錄
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = os.path.join(temp_dir, 'repo')
            
            # 克隆倉庫
            print(f"📥 克隆倉庫到: {repo_path}")
            self._clone_repo(repo_url, repo_path, branch)
            
            # 掃描所有代碼檔案
            structures = []
            file_count = 0
            
            for root, dirs, files in os.walk(repo_path):
                # 跳過 .git 目錄
                if '.git' in root:
                    continue
                
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    # 判斷語言
                    language = self._detect_language(file)
                    if not language:
                        continue
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                            code = f.read()
                        
                        # 提取邏輯架構
                        structure = self.extractor.extract_from_code(
                            code,
                            language,
                            rel_path
                        )
                        
                        structure['file_path'] = rel_path
                        structure['language'] = language
                        structure['repo_url'] = repo_url
                        
                        # 模式過濾
                        if patterns:
                            structure_patterns = set(structure.get('patterns', {}).keys())
                            if not any(p in structure_patterns for p in patterns):
                                continue
                        
                        structures.append(structure)
                        file_count += 1
                        
                    except Exception as e:
                        print(f"  ⚠️  處理檔案失敗 {rel_path}: {e}")
            
            print(f"✅ 掃描完成: {file_count} 個檔案")
            
            return {
                'repo_url': repo_url,
                'branch': branch,
                'file_count': file_count,
                'structures': structures,
                'timestamp': datetime.now().isoformat()
            }
    
    def match_logical_patterns(
        self,
        local_structures: List[Dict],
        remote_structures: List[Dict]
    ) -> List[Dict]:
        """
        匹配邏輯架構模式
        
        Args:
            local_structures: 本地代碼結構
            remote_structures: 遠端代碼結構
            
        Returns:
            匹配結果列表
        """
        print(f"🔗 開始匹配邏輯模式...")
        
        pattern_config = self.config.get('settings', {}).get('pattern_matching', {})
        enabled_patterns = pattern_config.get('patterns', [])
        
        # 過濾只包含目標模式的結構
        filtered_remote = []
        for structure in remote_structures:
            structure_patterns = set(structure.get('patterns', {}).keys())
            if any(p in structure_patterns for p in enabled_patterns):
                filtered_remote.append(structure)
        
        print(f"  找到 {len(filtered_remote)} 個包含目標模式的遠端結構")
        
        # 使用 extractor 進行匹配
        matches = self.extractor.match_logical_patterns(
            local_structures,
            filtered_remote,
            similarity_threshold=0.5
        )
        
        print(f"✅ 匹配完成: {len(matches)} 個匹配")
        
        return matches
    
    def sync_with_memory(
        self,
        matches: List[Dict],
        repo_name: str
    ) -> Dict:
        """
        執行同步並記錄到粒子記憶
        
        Args:
            matches: 匹配結果
            repo_name: 倉庫名稱
            
        Returns:
            同步結果統計
        """
        print(f"💾 開始同步到粒子記憶...")
        
        synced = 0
        duplicated = 0
        filtered = 0
        
        # 將匹配結果轉換為粒子
        particles = []
        for match in matches:
            remote = match['remote']
            
            # 讀取代碼內容
            # 注意：這裡簡化處理，實際應該重新讀取檔案
            content = f"# 邏輯架構粒子\n# 來源: {repo_name}\n# 模式: {match['shared_patterns']}"
            
            # 轉換為粒子
            particle = self.memory.particlize_code(
                content=content,
                language=remote.get('language', 'unknown'),
                file_path=remote.get('file_path', ''),
                patterns=match['shared_patterns'],
                particle_type='fx.noun',
                importance=match['similarity']
            )
            
            particles.append(particle)
        
        # 去重
        unique_particles, dup_particles = self.memory.deduplicate(particles)
        duplicated = len(dup_particles)
        
        print(f"  去重: {len(unique_particles)} 唯一, {duplicated} 重複")
        
        # 注意力過濾
        if self.config.get('settings', {}).get('attention', {}).get('enabled', True):
            # 轉換粒子為字典格式
            particle_dicts = [
                {
                    'id': p.id,
                    'simhash': p.simhash,
                    'layer': p.layer,
                    'importance': p.importance,
                    'patterns': p.patterns,
                    'content': p.content
                }
                for p in unique_particles
            ]
            
            # 計算注意力
            attention_map = self.attention.compute_attention(particle_dicts)
            
            # 按重要性排序
            ranked = self.attention.rank_by_importance(particle_dicts, attention_map)
            
            # 只保留高重要性的粒子
            threshold = self.config.get('settings', {}).get('attention', {}).get('similarity_threshold', 0.75)
            high_importance = [p for p, score in ranked if score >= threshold]
            
            filtered = len(unique_particles) - len(high_importance)
            
            # 更新唯一粒子列表（匹配回原始粒子對象）
            high_importance_ids = {p['id'] for p in high_importance}
            unique_particles = [p for p in unique_particles if p.id in high_importance_ids]
            
            print(f"  注意力過濾: 保留 {len(unique_particles)}, 過濾 {filtered}")
        
        # 存儲粒子
        for particle in unique_particles:
            if self.memory.store_particle(particle):
                synced += 1
        
        print(f"✅ 同步完成: {synced} 個粒子")
        
        return {
            'synced': synced,
            'duplicated': duplicated,
            'filtered': filtered,
            'total_matches': len(matches)
        }
    
    def run_sync(
        self,
        repo_filter: Optional[str] = None,
        pattern_filter: Optional[str] = None
    ) -> Dict:
        """
        執行完整同步流程
        
        Args:
            repo_filter: 可選的倉庫名稱過濾
            pattern_filter: 可選的模式過濾
            
        Returns:
            同步結果統計
        """
        print("=" * 60)
        print("🌀 MrLiouWord Intelligent Repository Sync")
        print("=" * 60)
        
        total_synced = 0
        total_duplicated = 0
        total_filtered = 0
        
        # 獲取本地結構（可選）
        local_structures = []
        
        # 處理每個倉庫
        repositories = self.config.get('repositories', [])
        
        for repo in repositories:
            if not repo.get('enabled', True):
                continue
            
            repo_name = repo['name']
            
            # 倉庫過濾
            if repo_filter and repo_filter != repo_name:
                continue
            
            print(f"\n📦 處理倉庫: {repo_name}")
            
            # 獲取邏輯模式
            logical_patterns = repo.get('logical_patterns', [])
            pattern_names = [p['pattern'] for p in logical_patterns]
            
            # 模式過濾
            if pattern_filter and pattern_filter not in pattern_names:
                print(f"  ⏭️  跳過（模式不匹配）")
                continue
            
            # 掃描遠端倉庫
            try:
                scan_result = self.scan_repository(
                    repo['url'],
                    repo.get('branch', 'main'),
                    pattern_names if pattern_filter else None
                )
                
                # 匹配模式
                matches = self.match_logical_patterns(
                    local_structures,
                    scan_result['structures']
                )
                
                # 同步到記憶
                sync_result = self.sync_with_memory(matches, repo_name)
                
                total_synced += sync_result['synced']
                total_duplicated += sync_result['duplicated']
                total_filtered += sync_result['filtered']
                
            except Exception as e:
                print(f"  ❌ 同步失敗: {e}")
                import traceback
                traceback.print_exc()
        
        # 驗證 Merkle 鏈
        print("\n🔐 驗證 Merkle 鏈完整性...")
        valid, errors = self.memory.verify_integrity()
        
        if valid:
            print("  ✅ Merkle 鏈完整性驗證通過")
        else:
            print(f"  ❌ Merkle 鏈驗證失敗:")
            for error in errors:
                print(f"    - {error}")
        
        # 統計
        stats = self.memory.get_stats()
        
        print("\n" + "=" * 60)
        print("📊 同步統計")
        print("=" * 60)
        print(f"  新增粒子: {total_synced}")
        print(f"  去重粒子: {total_duplicated}")
        print(f"  過濾粒子: {total_filtered}")
        print(f"  總粒子數: {stats['total_particles']}")
        print(f"  各層分布:")
        for layer, count in sorted(stats['by_layer'].items()):
            print(f"    {layer}: {count}")
        print(f"  Merkle 完整性: {'✅' if stats['merkle_valid'] else '❌'}")
        print("=" * 60)
        
        return {
            'synced': total_synced,
            'duplicated': total_duplicated,
            'filtered': total_filtered,
            'stats': stats
        }
    
    def _clone_repo(self, repo_url: str, target_path: str, branch: str):
        """克隆 Git 倉庫"""
        cmd = [
            'git', 'clone',
            '--depth', '1',
            '--branch', branch,
            repo_url,
            target_path
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"克隆失敗: {result.stderr}")
    
    def _detect_language(self, filename: str) -> Optional[str]:
        """根據副檔名檢測語言"""
        ext = os.path.splitext(filename)[1].lower()
        
        for lang, extensions in self.lang_extensions.items():
            if ext in extensions:
                return lang
        
        return None


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='MrLiouWord Intelligent Repository Sync',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 同步所有倉庫
  python intelligent_repo_sync.py --config intelligent_sync.yaml
  
  # 同步特定倉庫
  python intelligent_repo_sync.py --config intelligent_sync.yaml --repo flow-tasks-particle-core
  
  # 同步特定模式
  python intelligent_repo_sync.py --config intelligent_sync.yaml --pattern attention_mechanism
        """
    )
    
    parser.add_argument(
        '--config',
        default='intelligent_sync.yaml',
        help='配置檔案路徑 (預設: intelligent_sync.yaml)'
    )
    parser.add_argument(
        '--repo',
        help='只同步指定的倉庫'
    )
    parser.add_argument(
        '--pattern',
        help='只同步包含指定模式的代碼'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='只顯示統計資訊'
    )
    
    args = parser.parse_args()
    
    # 檢查配置檔案
    if not os.path.exists(args.config):
        print(f"❌ 找不到配置檔案: {args.config}")
        return 1
    
    # 創建同步器
    syncer = IntelligentRepoSync(args.config)
    
    # 只顯示統計
    if args.stats:
        stats = syncer.memory.get_stats()
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return 0
    
    # 執行同步
    try:
        result = syncer.run_sync(
            repo_filter=args.repo,
            pattern_filter=args.pattern
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  同步被中斷")
        return 130
    except Exception as e:
        print(f"\n❌ 同步失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
