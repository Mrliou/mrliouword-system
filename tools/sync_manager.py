#!/usr/bin/env python3
"""
Closure Sync Manager - 閉環同步管理器
Based on Liou Closure Law: 怎麼過去，就怎麼回來 (How it goes out, is how it comes back)

Implements the 5 phases of closure:
1. Observe (可觀測) - Collect state from all repositories
2. Resolve (可整合) - Resolve conflicts and generate unified state
3. Mirror (可回寫) - Write unified state back to all repositories
4. Verify (可驗證) - Verify Merkle root consistency
5. Loop (可重複) - Continuous monitoring and sync
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import hashlib

from merkle_builder import ParticleMerkleTree


class ClosureSyncManager:
    """
    閉環同步管理器 - Closure Sync Manager
    
    Core Principle: 怎麼過去，就怎麼回來
    """
    
    def __init__(self, source_repo: Path, target_repos: List[Path] = None):
        self.source = Path(source_repo)
        self.targets = [Path(r) for r in target_repos] if target_repos else []
        self.merkle_trees = {}
        self.state = {
            'phase': 'init',
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'source': str(self.source),
            'targets': [str(t) for t in self.targets]
        }
        
        # Load metadata
        self._load_metadata()
    
    def _load_metadata(self):
        """Load .mrliou/meta.json from source repository"""
        meta_path = self.source / '.mrliou' / 'meta.json'
        if meta_path.exists():
            with open(meta_path, 'r', encoding='utf-8') as f:
                self.meta = json.load(f)
        else:
            self.meta = {}
    
    def observe(self) -> Dict[str, Any]:
        """
        Phase 1: 可觀測 - Observe
        Collect state from all repositories
        """
        print("🔍 Phase 1: Observe - Collecting repository states...")
        self.state['phase'] = 'observe'
        
        observations = {}
        
        # Observe source repository
        print(f"  📊 Observing source: {self.source}")
        observations['source'] = self._observe_repo(self.source)
        
        # Observe target repositories
        observations['targets'] = {}
        for target in self.targets:
            print(f"  📊 Observing target: {target}")
            observations['targets'][str(target)] = self._observe_repo(target)
        
        self.observations = observations
        return observations
    
    def _observe_repo(self, repo_path: Path) -> Dict[str, Any]:
        """Observe a single repository and return its state"""
        state = {
            'path': str(repo_path),
            'exists': repo_path.exists(),
            'particles': [],
            'merkle_tree': None
        }
        
        if not repo_path.exists():
            return state
        
        # Find particle files
        sync_paths = [
            'core/particles/**/*.json',
            'docs/particle-dictionary/**/*.md',
            '.mrliou/**/*.json'
        ]
        
        particles = []
        for pattern in sync_paths:
            particles.extend(list(repo_path.glob(pattern)))
        
        state['particles'] = [str(p.relative_to(repo_path)) for p in particles]
        state['particle_count'] = len(particles)
        
        # Build Merkle tree
        tree = ParticleMerkleTree()
        if particles:
            tree.build_from_particles(particles)
            state['merkle_root'] = tree.merkle_root
            state['merkle_tree'] = tree
            self.merkle_trees[str(repo_path)] = tree
        
        return state
    
    def resolve(self) -> Dict[str, Any]:
        """
        Phase 2: 可整合 - Resolve
        Resolve conflicts and generate unified state
        """
        print("🔧 Phase 2: Resolve - Resolving conflicts...")
        self.state['phase'] = 'resolve'
        
        if not hasattr(self, 'observations'):
            raise RuntimeError("Must run observe() before resolve()")
        
        resolution = {
            'conflicts': [],
            'missing_in_source': [],
            'missing_in_targets': {},
            'action_plan': []
        }
        
        source_state = self.observations['source']
        source_particles = set(source_state.get('particles', []))
        
        # Compare with each target
        for target_path, target_state in self.observations['targets'].items():
            target_particles = set(target_state.get('particles', []))
            
            # Find particles missing in source
            missing_in_source = target_particles - source_particles
            if missing_in_source:
                resolution['missing_in_source'].extend([
                    {'file': f, 'source': target_path} for f in missing_in_source
                ])
            
            # Find particles missing in target
            missing_in_target = source_particles - target_particles
            if missing_in_target:
                resolution['missing_in_targets'][target_path] = list(missing_in_target)
                resolution['action_plan'].append({
                    'action': 'copy_to_target',
                    'files': list(missing_in_target),
                    'target': target_path
                })
        
        self.resolution = resolution
        return resolution
    
    def mirror(self, dry_run: bool = False) -> Dict[str, Any]:
        """
        Phase 3: 可回寫 - Mirror
        Write unified state back to all repositories
        """
        print(f"🔄 Phase 3: Mirror - Syncing changes {'(DRY RUN)' if dry_run else ''}...")
        self.state['phase'] = 'mirror'
        
        if not hasattr(self, 'resolution'):
            raise RuntimeError("Must run resolve() before mirror()")
        
        mirror_result = {
            'files_copied': 0,
            'operations': []
        }
        
        # Execute action plan
        for action in self.resolution.get('action_plan', []):
            if action['action'] == 'copy_to_target':
                target_path = Path(action['target'])
                
                for file_rel in action['files']:
                    src_file = self.source / file_rel
                    dst_file = target_path / file_rel
                    
                    if not src_file.exists():
                        print(f"  ⚠️  Source file not found: {src_file}")
                        continue
                    
                    # Create parent directory
                    if not dry_run:
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(src_file, dst_file)
                    
                    print(f"  {'[DRY]' if dry_run else '✓'} Copied: {file_rel} -> {target_path.name}")
                    mirror_result['files_copied'] += 1
                    mirror_result['operations'].append({
                        'type': 'copy',
                        'source': str(src_file),
                        'destination': str(dst_file),
                        'dry_run': dry_run
                    })
        
        self.mirror_result = mirror_result
        return mirror_result
    
    def verify(self) -> Dict[str, Any]:
        """
        Phase 4: 可驗證 - Verify
        Verify Merkle root consistency across repositories
        """
        print("✅ Phase 4: Verify - Verifying Merkle consistency...")
        self.state['phase'] = 'verify'
        
        verification = {
            'consistent': False,
            'merkle_roots': {},
            'mismatches': []
        }
        
        # Re-observe to get updated state
        updated_obs = self.observe()
        
        # Collect merkle roots
        source_root = updated_obs['source'].get('merkle_root', '')
        verification['merkle_roots']['source'] = source_root
        
        all_match = True
        for target_path, target_state in updated_obs['targets'].items():
            target_root = target_state.get('merkle_root', '')
            verification['merkle_roots'][target_path] = target_root
            
            if target_root != source_root:
                all_match = False
                verification['mismatches'].append({
                    'repository': target_path,
                    'expected': source_root,
                    'actual': target_root
                })
        
        verification['consistent'] = all_match
        
        if all_match:
            print(f"  ✅ All repositories consistent! Root: {source_root[:16]}...")
        else:
            print(f"  ⚠️  Inconsistencies detected:")
            for mismatch in verification['mismatches']:
                print(f"     - {Path(mismatch['repository']).name}")
        
        self.verification = verification
        return verification
    
    def loop(self, iterations: int = 1, auto_heal: bool = True):
        """
        Phase 5: 可重複 - Loop
        Continuous monitoring and sync
        """
        print(f"🔁 Phase 5: Loop - Running {iterations} iteration(s)...")
        self.state['phase'] = 'loop'
        
        for i in range(iterations):
            print(f"\n--- Iteration {i + 1}/{iterations} ---")
            
            # Run full cycle
            self.observe()
            self.resolve()
            
            if auto_heal:
                self.mirror(dry_run=False)
            
            verification = self.verify()
            
            if verification['consistent']:
                print(f"✅ Iteration {i + 1} complete - All consistent!")
            else:
                print(f"⚠️  Iteration {i + 1} complete - Inconsistencies remain")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive sync report"""
        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'state': self.state,
            'observations': getattr(self, 'observations', {}),
            'resolution': getattr(self, 'resolution', {}),
            'mirror_result': getattr(self, 'mirror_result', {}),
            'verification': getattr(self, 'verification', {})
        }
        return report
    
    def save_report(self, output_path: Path):
        """Save sync report to JSON file"""
        report = self.generate_report()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📝 Report saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Closure Sync Manager - 閉環同步管理器'
    )
    parser.add_argument('--source', default='.',
                        help='Source repository path (default: current directory)')
    parser.add_argument('--targets', required=False,
                        help='Comma-separated target repository paths')
    parser.add_argument('--mode', choices=['full', 'observe', 'verify'],
                        default='full', help='Sync mode')
    parser.add_argument('--verify', choices=['merkle', 'content'],
                        default='merkle', help='Verification method')
    parser.add_argument('--auto-heal', action='store_true',
                        help='Automatically heal inconsistencies')
    parser.add_argument('--dry-run', action='store_true',
                        help='Dry run mode (no actual changes)')
    parser.add_argument('--report', help='Output report path')
    
    args = parser.parse_args()
    
    # Parse targets
    targets = []
    if args.targets:
        targets = [t.strip() for t in args.targets.split(',')]
    
    # Create sync manager
    manager = ClosureSyncManager(args.source, targets)
    
    # Run sync based on mode
    if args.mode == 'observe':
        manager.observe()
    elif args.mode == 'verify':
        manager.observe()
        manager.verify()
    else:  # full
        manager.observe()
        manager.resolve()
        manager.mirror(dry_run=args.dry_run)
        manager.verify()
    
    # Generate report
    if args.report:
        manager.save_report(Path(args.report))
    else:
        print("\n" + "="*60)
        print("📊 Sync Summary:")
        print("="*60)
        report = manager.generate_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
