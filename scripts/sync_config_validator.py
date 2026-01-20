#!/usr/bin/env python3
"""
Sync Config Validator - 配置驗證器

驗證 intelligent_sync.yaml 配置檔案的正確性

Author: MR.liou
"""

import sys
import yaml
import argparse
from typing import Dict, List, Optional, Tuple


class SyncConfigValidator:
    """配置驗證器"""
    
    # 必需的頂層欄位
    REQUIRED_TOP_LEVEL = ['settings', 'repositories']
    
    # 有效的掃描模式
    VALID_SCAN_MODES = ['global', 'targeted']
    
    # 有效的同步策略
    VALID_SYNC_STRATEGIES = ['logical_pattern', 'file_based']
    
    # 有效的邏輯模式
    VALID_PATTERNS = [
        'attention_mechanism',
        'memory_system',
        'particle_engine',
        'frequency_resonance',
        'merkle_chain',
        'logical_reasoning'
    ]
    
    # 有效的層級
    VALID_LAYERS = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def validate(self, config_path: str) -> Tuple[bool, List[str], List[str]]:
        """
        驗證配置檔案
        
        Args:
            config_path: 配置檔案路徑
            
        Returns:
            (是否有效, 錯誤列表, 警告列表)
        """
        self.errors = []
        self.warnings = []
        
        # 載入 YAML
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
        except FileNotFoundError:
            self.errors.append(f"找不到配置檔案: {config_path}")
            return False, self.errors, self.warnings
        except yaml.YAMLError as e:
            self.errors.append(f"YAML 語法錯誤: {e}")
            return False, self.errors, self.warnings
        
        # 驗證頂層結構
        self._validate_top_level(config)
        
        # 驗證設定
        if 'settings' in config:
            self._validate_settings(config['settings'])
        
        # 驗證倉庫配置
        if 'repositories' in config:
            self._validate_repositories(config['repositories'])
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_top_level(self, config: Dict):
        """驗證頂層欄位"""
        for field in self.REQUIRED_TOP_LEVEL:
            if field not in config:
                self.errors.append(f"缺少必需欄位: {field}")
    
    def _validate_settings(self, settings: Dict):
        """驗證設定區塊"""
        # 掃描模式
        scan_mode = settings.get('scan_mode')
        if scan_mode and scan_mode not in self.VALID_SCAN_MODES:
            self.errors.append(
                f"無效的掃描模式: {scan_mode}, "
                f"必須是 {self.VALID_SCAN_MODES} 之一"
            )
        
        # 同步策略
        sync_strategy = settings.get('sync_strategy')
        if sync_strategy and sync_strategy not in self.VALID_SYNC_STRATEGIES:
            self.errors.append(
                f"無效的同步策略: {sync_strategy}, "
                f"必須是 {self.VALID_SYNC_STRATEGIES} 之一"
            )
        
        # 模式匹配設定
        if 'pattern_matching' in settings:
            self._validate_pattern_matching(settings['pattern_matching'])
        
        # 粒子記憶設定
        if 'particle_memory' in settings:
            self._validate_particle_memory(settings['particle_memory'])
        
        # 注意力機制設定
        if 'attention' in settings:
            self._validate_attention(settings['attention'])
    
    def _validate_pattern_matching(self, pattern_matching: Dict):
        """驗證模式匹配設定"""
        if not pattern_matching.get('enabled'):
            return
        
        patterns = pattern_matching.get('patterns', [])
        if not patterns:
            self.warnings.append("模式匹配已啟用但未指定任何模式")
        
        for pattern in patterns:
            if pattern not in self.VALID_PATTERNS:
                self.warnings.append(
                    f"未知的邏輯模式: {pattern}, "
                    f"建議使用 {self.VALID_PATTERNS}"
                )
    
    def _validate_particle_memory(self, particle_memory: Dict):
        """驗證粒子記憶設定"""
        if not particle_memory.get('enabled'):
            return
        
        # SimHash 閾值
        threshold = particle_memory.get('simhash_threshold')
        if threshold is not None:
            if not isinstance(threshold, int) or threshold < 0 or threshold > 64:
                self.errors.append(
                    f"無效的 SimHash 閾值: {threshold}, 必須是 0-64 之間的整數"
                )
        
        # 層級映射
        layer_mapping = particle_memory.get('layer_mapping', {})
        for key, layer in layer_mapping.items():
            if layer not in self.VALID_LAYERS:
                self.errors.append(
                    f"無效的層級: {layer} (在 layer_mapping.{key}), "
                    f"必須是 {self.VALID_LAYERS} 之一"
                )
    
    def _validate_attention(self, attention: Dict):
        """驗證注意力機制設定"""
        if not attention.get('enabled'):
            return
        
        # 維度
        dimension = attention.get('dimension')
        if dimension is not None:
            if not isinstance(dimension, int) or dimension <= 0:
                self.errors.append(f"無效的維度: {dimension}, 必須是正整數")
        
        # 注意力頭數
        num_heads = attention.get('num_heads')
        if num_heads is not None:
            if not isinstance(num_heads, int) or num_heads <= 0:
                self.errors.append(f"無效的注意力頭數: {num_heads}, 必須是正整數")
            
            # 檢查維度是否可被頭數整除
            if dimension and num_heads and dimension % num_heads != 0:
                self.errors.append(
                    f"維度 ({dimension}) 必須能被注意力頭數 ({num_heads}) 整除"
                )
        
        # 相似度閾值
        similarity_threshold = attention.get('similarity_threshold')
        if similarity_threshold is not None:
            if not isinstance(similarity_threshold, (int, float)) or \
               similarity_threshold < 0 or similarity_threshold > 1:
                self.errors.append(
                    f"無效的相似度閾值: {similarity_threshold}, 必須是 0-1 之間"
                )
    
    def _validate_repositories(self, repositories: List[Dict]):
        """驗證倉庫配置"""
        if not repositories:
            self.warnings.append("未配置任何倉庫")
            return
        
        for i, repo in enumerate(repositories):
            self._validate_repository(repo, i)
    
    def _validate_repository(self, repo: Dict, index: int):
        """驗證單個倉庫配置"""
        prefix = f"repositories[{index}]"
        
        # 必需欄位
        required_fields = ['name', 'url']
        for field in required_fields:
            if field not in repo:
                self.errors.append(f"{prefix}: 缺少必需欄位 '{field}'")
        
        # URL 格式
        url = repo.get('url', '')
        if url and not (url.startswith('http://') or url.startswith('https://') or url.startswith('git@')):
            self.errors.append(f"{prefix}: 無效的 URL 格式: {url}")
        
        # 邏輯模式配置
        logical_patterns = repo.get('logical_patterns', [])
        for j, pattern_config in enumerate(logical_patterns):
            self._validate_logical_pattern(pattern_config, f"{prefix}.logical_patterns[{j}]")
    
    def _validate_logical_pattern(self, pattern_config: Dict, prefix: str):
        """驗證邏輯模式配置"""
        # 必需欄位
        if 'pattern' not in pattern_config:
            self.errors.append(f"{prefix}: 缺少必需欄位 'pattern'")
        else:
            pattern = pattern_config['pattern']
            if pattern not in self.VALID_PATTERNS:
                self.warnings.append(
                    f"{prefix}: 未知的邏輯模式 '{pattern}', "
                    f"建議使用 {self.VALID_PATTERNS}"
                )
        
        # 目標層級
        target_layer = pattern_config.get('target_layer')
        if target_layer and target_layer not in self.VALID_LAYERS:
            self.errors.append(
                f"{prefix}: 無效的目標層級 '{target_layer}', "
                f"必須是 {self.VALID_LAYERS} 之一"
            )


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='驗證 intelligent_sync.yaml 配置檔案'
    )
    parser.add_argument(
        'config',
        nargs='?',
        default='intelligent_sync.yaml',
        help='配置檔案路徑 (預設: intelligent_sync.yaml)'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='嚴格模式（警告也視為錯誤）'
    )
    
    args = parser.parse_args()
    
    # 驗證
    validator = SyncConfigValidator()
    is_valid, errors, warnings = validator.validate(args.config)
    
    # 顯示結果
    print(f"驗證配置檔案: {args.config}")
    print("=" * 60)
    
    if errors:
        print(f"\n❌ 發現 {len(errors)} 個錯誤:")
        for error in errors:
            print(f"  • {error}")
    
    if warnings:
        print(f"\n⚠️  發現 {len(warnings)} 個警告:")
        for warning in warnings:
            print(f"  • {warning}")
    
    if not errors and not warnings:
        print("\n✅ 配置檔案驗證通過！")
    
    print("=" * 60)
    
    # 返回狀態碼
    if errors:
        return 1
    if args.strict and warnings:
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
