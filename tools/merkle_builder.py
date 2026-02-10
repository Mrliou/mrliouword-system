#!/usr/bin/env python3
"""
Merkle Tree Builder for Particle System
Based on Liou Closure Law - 怎麼過去，就怎麼回來
"""

import hashlib
import json
import os
from typing import List, Dict, Any, Tuple
from pathlib import Path


class ParticleMerkleTree:
    """粒子系統 Merkle Tree - Particle System Merkle Tree"""
    
    def __init__(self, hash_algorithm: str = 'sha256'):
        self.hash_algorithm = hash_algorithm
        self.nodes = []
        self.merkle_root = ""
        self.leaf_count = 0
        
    def _hash(self, data: str) -> str:
        """Generate hash for data"""
        hasher = hashlib.new(self.hash_algorithm)
        hasher.update(data.encode('utf-8'))
        return hasher.hexdigest()
    
    def _hash_file(self, file_path: Path) -> str:
        """Generate hash for file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._hash(content)
        except Exception as e:
            print(f"Error hashing file {file_path}: {e}")
            return ""
    
    def build_from_particles(self, particle_files: List[Path]) -> str:
        """
        從粒子文件構建 Merkle tree
        Build Merkle tree from particle files
        """
        if not particle_files:
            self.merkle_root = ""
            self.leaf_count = 0
            return ""
        
        # Sort files for consistency
        particle_files = sorted(particle_files)
        
        # Create leaf nodes (hash of each file)
        leaves = []
        for file_path in particle_files:
            file_hash = self._hash_file(file_path)
            if file_hash:
                leaves.append({
                    'file': str(file_path),
                    'hash': file_hash,
                    'level': 0
                })
        
        if not leaves:
            self.merkle_root = ""
            self.leaf_count = 0
            return ""
        
        self.leaf_count = len(leaves)
        self.nodes = leaves.copy()
        
        # Build tree bottom-up
        current_level = leaves
        level = 1
        
        while len(current_level) > 1:
            next_level = []
            
            # Process pairs
            for i in range(0, len(current_level), 2):
                left = current_level[i]
                
                if i + 1 < len(current_level):
                    right = current_level[i + 1]
                    # Combine hashes
                    combined = left['hash'] + right['hash']
                    parent_hash = self._hash(combined)
                else:
                    # Odd number of nodes, promote single node
                    parent_hash = left['hash']
                
                parent_node = {
                    'hash': parent_hash,
                    'level': level,
                    'left': left.get('hash'),
                    'right': current_level[i + 1].get('hash') if i + 1 < len(current_level) else None
                }
                next_level.append(parent_node)
                self.nodes.append(parent_node)
            
            current_level = next_level
            level += 1
        
        # Root is the last remaining node
        self.merkle_root = current_level[0]['hash']
        return self.merkle_root
    
    def verify_integrity(self, expected_root: str) -> bool:
        """
        驗證完整性
        Verify integrity against expected root
        """
        return self.merkle_root == expected_root
    
    def find_missing_nodes(self, other_tree: 'ParticleMerkleTree') -> List[Dict[str, Any]]:
        """
        找出缺失節點
        Find missing nodes compared to another tree
        """
        missing = []
        
        # Get leaf hashes from both trees
        my_leaves = {node['hash']: node for node in self.nodes if node.get('level') == 0}
        other_leaves = {node['hash']: node for node in other_tree.nodes if node.get('level') == 0}
        
        # Find nodes in other tree but not in this tree
        for hash_val, node in other_leaves.items():
            if hash_val not in my_leaves:
                missing.append(node)
        
        return missing
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tree to dictionary for serialization"""
        return {
            'version': 'v1.0',
            'merkle_root': self.merkle_root,
            'tree_height': max([node.get('level', 0) for node in self.nodes]) + 1 if self.nodes else 0,
            'leaf_count': self.leaf_count,
            'hash_algorithm': self.hash_algorithm,
            'nodes': self.nodes
        }
    
    def save(self, output_path: Path):
        """Save Merkle tree to JSON file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, input_path: Path) -> 'ParticleMerkleTree':
        """Load Merkle tree from JSON file"""
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tree = cls(hash_algorithm=data.get('hash_algorithm', 'sha256'))
        tree.merkle_root = data.get('merkle_root', '')
        tree.leaf_count = data.get('leaf_count', 0)
        tree.nodes = data.get('nodes', [])
        
        return tree


def build_particle_merkle_tree(repo_path: Path, output_path: Path = None) -> ParticleMerkleTree:
    """
    Build Merkle tree for all particles in repository
    
    Args:
        repo_path: Path to repository root
        output_path: Optional path to save tree JSON
    
    Returns:
        ParticleMerkleTree object
    """
    # Find all particle files
    particle_patterns = [
        'core/particles/**/*.json',
        'docs/particle-dictionary/**/*.md',
        '.mrliou/**/*.json'
    ]
    
    particle_files = []
    for pattern in particle_patterns:
        particle_files.extend(repo_path.glob(pattern))
    
    # Build tree
    tree = ParticleMerkleTree()
    tree.build_from_particles(particle_files)
    
    # Save if output path provided
    if output_path:
        tree.save(output_path)
    
    return tree


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python merkle_builder.py <repo_path> [output_path]")
        sys.exit(1)
    
    repo_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else repo_path / '.mrliou' / 'merkle.json'
    
    tree = build_particle_merkle_tree(repo_path, output_path)
    
    print(f"✅ Merkle tree built successfully")
    print(f"   Root: {tree.merkle_root}")
    print(f"   Leaves: {tree.leaf_count}")
    print(f"   Height: {max([node.get('level', 0) for node in tree.nodes]) + 1 if tree.nodes else 0}")
    print(f"   Saved to: {output_path}")
