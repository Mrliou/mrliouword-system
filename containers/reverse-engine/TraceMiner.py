"""
Trace Miner - 追蹤挖掘器
分析 trace_fs.csv 和 trace_ops.csv 產生規則和通道地圖
"""

import pandas as pd
import yaml
from typing import Dict, List

class TraceMiner:
    def __init__(self):
        self.rules = []
        self.channel_map = {}
    
    def mine(self, trace_fs_path: str, trace_ops_path: str) -> Dict:
        """分析 trace 產生規則"""
        print(f"[TraceMiner] Loading traces...")
        
        df_fs = pd.read_csv(trace_fs_path)
        df_ops = pd.read_csv(trace_ops_path)
        
        # 提取模式
        patterns = self.extract_patterns(df_fs, df_ops)
        
        # 建構規則
        self.rules = self.build_rules(patterns)
        
        # 建構通道地圖
        self.channel_map = self.build_channel_map(df_fs, df_ops)
        
        return {
            'rules': self.rules,
            'channel_map': self.channel_map
        }
    
    def extract_patterns(self, df_fs: pd.DataFrame, df_ops: pd.DataFrame) -> List[Dict]:
        """提取操作模式"""
        patterns = []
        
        # 分析 VirtualStore 重導向
        virtual_store_ops = df_fs[df_fs['fullpath'].str.contains('VirtualStore', na=False)]
        if not virtual_store_ops.empty:
            patterns.append({
                'type': 'virtualstore_redirect',
                'count': len(virtual_store_ops),
                'paths': virtual_store_ops['fullpath'].tolist()
            })
        
        # 分析 AppData 操作
        appdata_ops = df_fs[df_fs['fullpath'].str.contains('AppData', na=False)]
        if not appdata_ops.empty:
            patterns.append({
                'type': 'appdata_usage',
                'count': len(appdata_ops),
                'paths': appdata_ops['fullpath'].tolist()
            })
        
        return patterns
    
    def build_rules(self, patterns: List[Dict]) -> List[Dict]:
        """建構規則"""
        rules = []
        
        for pattern in patterns:
            if pattern['type'] == 'virtualstore_redirect':
                rules.append({
                    'name': 'VirtualStore Redirect Detection',
                    'condition': 'path contains VirtualStore',
                    'action': 'map to real location'
                })
            elif pattern['type'] == 'appdata_usage':
                rules.append({
                    'name': 'AppData Usage Pattern',
                    'condition': 'path contains AppData',
                    'action': 'track and document'
                })
        
        return rules
    
    def build_channel_map(self, df_fs: pd.DataFrame, df_ops: pd.DataFrame) -> Dict:
        """建構通道地圖"""
        import os
        channel_map = {}
        
        # 分析真實路徑映射
        for idx, row in df_fs.iterrows():
            path = row['fullpath']
            if 'VirtualStore' in path:
                # 提取原始路徑 - 使用 os.path.sep 以支援跨平台
                original = path.replace(f'VirtualStore{os.path.sep}', '')
                channel_map[original] = path
        
        return channel_map
    
    def export_yaml(self, output_path: str):
        """匯出 YAML 格式"""
        data = {
            'rules': self.rules,
            'channel_map': self.channel_map,
            'metadata': {
                'origin_signature': 'MrLiouWord',
                'generated_at': pd.Timestamp.now().isoformat()
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"[TraceMiner] Exported to {output_path}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) != 3:
        print("Usage: python TraceMiner.py <trace_fs.csv> <trace_ops.csv>")
        sys.exit(1)
    
    miner = TraceMiner()
    result = miner.mine(sys.argv[1], sys.argv[2])
    miner.export_yaml('rules_output.yaml')
    
    print(f"\n[TraceMiner] Found {len(result['rules'])} rules")
    print(f"[TraceMiner] Found {len(result['channel_map'])} channel mappings")
