#!/usr/bin/env python3
"""
Sync Report Generator - 同步報告生成器
Generate comprehensive sync reports
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any


def generate_sync_report(source_repo: Path, target_repos: list, 
                        output_path: Path = None) -> Dict[str, Any]:
    """
    生成同步報告
    Generate comprehensive sync report
    """
    print("📊 Generating sync report...")
    
    report = {
        'timestamp': datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        'source': str(source_repo),
        'targets': [str(t) for t in target_repos],
        'summary': {},
        'details': {}
    }
    
    # Load health status if available
    health_path = source_repo / '.mrliou' / 'health.json'
    if health_path.exists():
        with open(health_path, 'r', encoding='utf-8') as f:
            health = json.load(f)
        report['health'] = health
    
    # Load consistency map if available
    consistency_path = source_repo / '.mrliou' / 'consistency.map.json'
    if consistency_path.exists():
        with open(consistency_path, 'r', encoding='utf-8') as f:
            consistency = json.load(f)
        report['consistency'] = consistency
    
    # Load Merkle tree if available
    merkle_path = source_repo / '.mrliou' / 'merkle.json'
    if merkle_path.exists():
        with open(merkle_path, 'r', encoding='utf-8') as f:
            merkle = json.load(f)
        report['merkle'] = {
            'root': merkle.get('merkle_root', ''),
            'leaf_count': merkle.get('leaf_count', 0),
            'tree_height': merkle.get('tree_height', 0)
        }
    
    # Count particles
    sync_patterns = [
        'core/particles/**/*.json',
        'docs/particle-dictionary/**/*.md'
    ]
    
    particle_count = 0
    for pattern in sync_patterns:
        particle_count += len(list(source_repo.glob(pattern)))
    
    report['summary'] = {
        'total_particles': particle_count,
        'total_repositories': 1 + len(target_repos),
        'source_repository': source_repo.name,
        'target_count': len(target_repos)
    }
    
    print(f"  ✅ Report generated")
    print(f"     Total particles: {particle_count}")
    print(f"     Repositories: {1 + len(target_repos)}")
    
    # Save report if output path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  📝 Report saved to: {output_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description='Generate sync report'
    )
    parser.add_argument('--source', default='.',
                        help='Source repository path')
    parser.add_argument('--targets',
                        help='Comma-separated target repository paths')
    parser.add_argument('--output', '-o',
                        help='Output JSON file path')
    
    args = parser.parse_args()
    
    source = Path(args.source)
    targets = []
    if args.targets:
        targets = [Path(t.strip()) for t in args.targets.split(',')]
    
    output_path = Path(args.output) if args.output else None
    
    report = generate_sync_report(source, targets, output_path)
    
    if not args.output:
        print("\n" + "="*60)
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
