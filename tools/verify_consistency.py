#!/usr/bin/env python3
"""
Consistency Verifier - 一致性驗證器
Verify Merkle consistency across repositories
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any
from merkle_builder import ParticleMerkleTree


def verify_consistency(repos: list, output_path: Path = None) -> Dict[str, Any]:
    """
    驗證多個倉庫的 Merkle 一致性
    Verify Merkle consistency across multiple repositories
    """
    print("🔍 Verifying consistency across repositories...")
    
    result = {
        'consistent': False,
        'repositories': {},
        'reference_root': None,
        'mismatches': []
    }
    
    # Build Merkle tree for each repository
    for repo_path in repos:
        repo = Path(repo_path)
        
        if not repo.exists():
            print(f"  ⚠️  Repository not found: {repo}")
            result['repositories'][str(repo)] = {
                'status': 'not_found',
                'merkle_root': None
            }
            continue
        
        # Find particle files
        sync_patterns = [
            'core/particles/**/*.json',
            'docs/particle-dictionary/**/*.md',
            '.mrliou/**/*.json'
        ]
        
        files = []
        for pattern in sync_patterns:
            files.extend(list(repo.glob(pattern)))
        
        # Build Merkle tree
        tree = ParticleMerkleTree()
        tree.build_from_particles(files)
        
        repo_result = {
            'status': 'verified',
            'merkle_root': tree.merkle_root,
            'particle_count': len(files),
            'tree_height': max([node.get('level', 0) for node in tree.nodes]) + 1 if tree.nodes else 0
        }
        
        result['repositories'][str(repo)] = repo_result
        
        # Set reference root from first repo
        if result['reference_root'] is None:
            result['reference_root'] = tree.merkle_root
        
        # Check consistency
        if tree.merkle_root != result['reference_root']:
            result['mismatches'].append({
                'repository': str(repo),
                'expected': result['reference_root'],
                'actual': tree.merkle_root
            })
        
        print(f"  📊 {repo.name}: {tree.merkle_root[:16] if tree.merkle_root else 'empty'}... ({len(files)} files)")
    
    # Determine overall consistency
    result['consistent'] = len(result['mismatches']) == 0
    
    if result['consistent']:
        print(f"\n  ✅ All repositories are consistent!")
        print(f"     Merkle Root: {result['reference_root'][:32] if result['reference_root'] else 'empty'}...")
    else:
        print(f"\n  ❌ Inconsistencies detected:")
        for mismatch in result['mismatches']:
            print(f"     - {Path(mismatch['repository']).name}")
    
    # Save result if output path provided
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n  📝 Results saved to: {output_path}")
    
    return result


def main():
    parser = argparse.ArgumentParser(
        description='Verify Merkle consistency across repositories'
    )
    parser.add_argument('repos', nargs='+',
                        help='Repository paths to verify')
    parser.add_argument('--output', '-o',
                        help='Output JSON file path')
    parser.add_argument('--check-merkle', action='store_true',
                        help='Perform Merkle tree verification')
    parser.add_argument('--cross-repo', action='store_true',
                        help='Cross-repository consistency check')
    
    args = parser.parse_args()
    
    output_path = Path(args.output) if args.output else None
    
    result = verify_consistency(args.repos, output_path)
    
    # Exit with error code if inconsistent
    if not result['consistent']:
        sys.exit(1)


if __name__ == '__main__':
    main()
