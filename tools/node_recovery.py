#!/usr/bin/env python3
"""
Node Recovery System - 節點丟失恢復系統
Implements multi-source restoration based on Liou Closure Law
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from merkle_builder import ParticleMerkleTree


class NodeRecoverySystem:
    """節點丟失恢復系統 - Node Recovery System"""
    
    def __init__(self, repos: List[Path]):
        self.repos = [Path(r) for r in repos]
        self.trees = {}
        self.file_hashes = {}
    
    def detect_missing_nodes(self) -> Dict[str, List[str]]:
        """
        檢測三個倉庫中的缺失節點
        Detect missing nodes across repositories
        
        Returns:
            Dictionary mapping repo path to list of missing files
        """
        print("🔍 Detecting missing nodes across repositories...")
        
        # Build trees for all repos
        all_files = set()
        repo_files = {}
        
        for repo in self.repos:
            if not repo.exists():
                print(f"  ⚠️  Repository not found: {repo}")
                repo_files[str(repo)] = set()
                continue
            
            # Find particle files
            sync_patterns = [
                'core/particles/**/*.json',
                'docs/particle-dictionary/**/*.md',
                '.mrliou/**/*.json'
            ]
            
            files = set()
            for pattern in sync_patterns:
                for file_path in repo.glob(pattern):
                    rel_path = str(file_path.relative_to(repo))
                    files.add(rel_path)
                    all_files.add(rel_path)
            
            repo_files[str(repo)] = files
        
        # Find missing files in each repo
        missing = {}
        for repo_path, files in repo_files.items():
            missing_in_repo = all_files - files
            if missing_in_repo:
                missing[repo_path] = list(missing_in_repo)
                print(f"  ⚠️  {len(missing_in_repo)} files missing in {Path(repo_path).name}")
        
        if not missing:
            print("  ✅ No missing nodes detected")
        
        return missing
    
    def find_valid_source(self, node_path: str, repos: List[Path]) -> Optional[Path]:
        """
        從其他倉庫找到有效源
        Find valid source for a missing node from other repositories
        
        Args:
            node_path: Relative path to the missing file
            repos: List of repository paths to search
        
        Returns:
            Path to valid source file, or None if not found
        """
        for repo in repos:
            candidate = repo / node_path
            if candidate.exists():
                return candidate
        
        return None
    
    def restore_node(self, node_path: str, source_repo: Path, target_repo: Path, 
                     dry_run: bool = False) -> bool:
        """
        從源頭恢復節點到目標倉庫
        Restore node from source repository to target repository
        
        Args:
            node_path: Relative path to the file
            source_repo: Repository containing the valid file
            target_repo: Repository missing the file
            dry_run: If True, don't actually copy files
        
        Returns:
            True if restoration successful, False otherwise
        """
        src_file = source_repo / node_path
        dst_file = target_repo / node_path
        
        if not src_file.exists():
            print(f"  ❌ Source file not found: {src_file}")
            return False
        
        if dst_file.exists():
            print(f"  ℹ️  File already exists in target: {dst_file}")
            return True
        
        try:
            if not dry_run:
                # Create parent directories
                dst_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(src_file, dst_file)
            
            print(f"  {'[DRY]' if dry_run else '✓'} Restored: {node_path}")
            return True
            
        except Exception as e:
            print(f"  ❌ Error restoring {node_path}: {e}")
            return False
    
    def restore_from_sources(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        從多個源頭恢復所有缺失節點
        Restore all missing nodes from multiple sources
        
        Args:
            dry_run: If True, don't actually copy files
        
        Returns:
            Recovery report
        """
        print("🔧 Starting node recovery process...")
        
        # Detect missing nodes
        missing = self.detect_missing_nodes()
        
        recovery_report = {
            'total_missing': sum(len(files) for files in missing.values()),
            'restored': 0,
            'failed': 0,
            'details': []
        }
        
        # Restore each missing file
        for repo_path, missing_files in missing.items():
            target_repo = Path(repo_path)
            
            for file_path in missing_files:
                # Find valid source
                source_repo = self.find_valid_source(file_path, self.repos)
                
                if source_repo is None:
                    print(f"  ❌ No valid source found for: {file_path}")
                    recovery_report['failed'] += 1
                    recovery_report['details'].append({
                        'file': file_path,
                        'target': repo_path,
                        'status': 'no_source_found'
                    })
                    continue
                
                # Restore node
                success = self.restore_node(file_path, source_repo, target_repo, dry_run)
                
                if success:
                    recovery_report['restored'] += 1
                    recovery_report['details'].append({
                        'file': file_path,
                        'source': str(source_repo),
                        'target': repo_path,
                        'status': 'restored'
                    })
                else:
                    recovery_report['failed'] += 1
                    recovery_report['details'].append({
                        'file': file_path,
                        'target': repo_path,
                        'status': 'restore_failed'
                    })
        
        print(f"\n📊 Recovery Summary:")
        print(f"  Total missing: {recovery_report['total_missing']}")
        print(f"  Restored: {recovery_report['restored']}")
        print(f"  Failed: {recovery_report['failed']}")
        
        return recovery_report
    
    def verify_restoration(self) -> Dict[str, bool]:
        """
        驗證恢復後的一致性
        Verify consistency after restoration
        
        Returns:
            Dictionary mapping repo path to consistency status
        """
        print("✅ Verifying restoration consistency...")
        
        # Build Merkle trees for all repos
        trees = {}
        for repo in self.repos:
            if not repo.exists():
                continue
            
            sync_patterns = [
                'core/particles/**/*.json',
                'docs/particle-dictionary/**/*.md',
                '.mrliou/**/*.json'
            ]
            
            files = []
            for pattern in sync_patterns:
                files.extend(list(repo.glob(pattern)))
            
            tree = ParticleMerkleTree()
            tree.build_from_particles(files)
            trees[str(repo)] = tree
        
        # Compare merkle roots
        if not trees:
            return {}
        
        reference_root = None
        consistency = {}
        
        for repo_path, tree in trees.items():
            if reference_root is None:
                reference_root = tree.merkle_root
            
            is_consistent = (tree.merkle_root == reference_root)
            consistency[repo_path] = is_consistent
            
            status = "✅" if is_consistent else "❌"
            print(f"  {status} {Path(repo_path).name}: {tree.merkle_root[:16]}...")
        
        return consistency


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python node_recovery.py <repo1> [repo2] [repo3] ...")
        print("       python node_recovery.py --source <source> --targets <target1,target2>")
        sys.exit(1)
    
    # Parse arguments
    if '--source' in sys.argv:
        source_idx = sys.argv.index('--source')
        source = sys.argv[source_idx + 1]
        
        targets_idx = sys.argv.index('--targets')
        targets = sys.argv[targets_idx + 1].split(',')
        
        repos = [Path(source)] + [Path(t.strip()) for t in targets]
    else:
        repos = [Path(r) for r in sys.argv[1:]]
    
    # Run recovery
    recovery = NodeRecoverySystem(repos)
    report = recovery.restore_from_sources(dry_run='--dry-run' in sys.argv)
    
    print("\n" + "="*60)
    recovery.verify_restoration()
