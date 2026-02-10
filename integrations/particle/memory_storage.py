#!/usr/bin/env python3
"""
Particle Memory Storage
========================

Stores particles with deduplication, Merkle chain, and layer assignment.

Features:
- SimHash64 deduplication (Hamming ≤ 3)
- Merge similar particle sources
- Merkle chain computation
- Layer assignment by similarity score
- Particle frequency calculation

Layer Assignment:
- ≥0.9 → L1
- ≥0.75 → L2
- ≥0.6 → L3
- ≥0.4 → L4
- <0.4 → L5

Author: MR.liou
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.simhash64 import simhash64, hamming_distance
from core.merkle import MerkleChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SCHUMANN = 7.83
PHI = 1.618033988749895

FREQ = {
    'L∞': SCHUMANN * PHI ** 7,
    'L7': SCHUMANN * PHI ** 6,
    'L6': SCHUMANN * PHI ** 5,
    'L5': SCHUMANN * PHI ** 4,
    'L4': SCHUMANN * PHI ** 3,
    'L3': SCHUMANN * PHI ** 2,
    'L2': SCHUMANN * PHI,
    'L1': SCHUMANN,
    'L0': SCHUMANN / PHI
}

@dataclass
class Particle:
    """Particle data structure"""
    id: str
    name: str
    type: str
    content: str
    simhash: str
    layer: str
    frequency: float
    sources: List[Dict]
    tags: List[str]
    merkle: str
    timestamp: str
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)


class ParticleMemoryStorage:
    """
    Particle Memory Storage System
    
    Manages particle storage with deduplication, Merkle verification,
    and intelligent layer assignment.
    """
    
    def __init__(self, storage_path: str = './particle_memory'):
        """
        Initialize particle memory storage
        
        Args:
            storage_path: Path to storage directory
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize components
        self.merkle_chain = MerkleChain(os.path.join(storage_path, 'merkle'))
        
        # Particle index
        self.particles = {}  # id -> Particle
        self.simhash_index = {}  # simhash -> particle_id
        
        # Load existing particles
        self._load_particles()
        
        logger.info(f"ParticleMemoryStorage initialized with {len(self.particles)} particles")
    
    def _load_particles(self):
        """Load existing particles from storage"""
        particles_file = os.path.join(self.storage_path, 'particles.jsonl')
        
        if os.path.exists(particles_file):
            with open(particles_file, 'r') as f:
                for line in f:
                    if line.strip():
                        particle_data = json.loads(line)
                        particle_id = particle_data['id']
                        self.particles[particle_id] = particle_data
                        self.simhash_index[particle_data['simhash']] = particle_id
            
            logger.info(f"Loaded {len(self.particles)} particles")
    
    def _save_particle(self, particle: Particle):
        """Save particle to storage"""
        particles_file = os.path.join(self.storage_path, 'particles.jsonl')
        
        with open(particles_file, 'a') as f:
            f.write(json.dumps(particle.to_dict(), ensure_ascii=False) + '\n')
    
    def _find_similar_particles(self, simhash: str, threshold: int = 3) -> List[str]:
        """
        Find similar particles using SimHash
        
        Args:
            simhash: Query SimHash
            threshold: Hamming distance threshold
            
        Returns:
            List of similar particle IDs
        """
        # Lazily build a simple LSH-style band index over the existing simhash_index
        # to avoid a full linear scan for every query.
        #
        # We split the 64-bit simhash (hex string) into 4 bands of 16 bits each and
        # index particles by these band keys. Candidates that share at least one band
        # with the query are then checked with exact Hamming distance.

        def _bands_from_simhash(hash_str: str, num_bands: int = 4) -> List[int]:
            """Convert hex simhash string into a list of integer band keys."""
            try:
                value = int(hash_str, 16)
            except (TypeError, ValueError):
                # Fallback: no bands if the simhash is malformed
                return []
            bits = 64
            band_size = bits // num_bands
            bands: List[int] = []
            for band in range(num_bands):
                shift = bits - (band + 1) * band_size
                mask = (1 << band_size) - 1
                bands.append((value >> shift) & mask)
            return bands

        # Rebuild the LSH index if it does not exist or if the underlying index size changed.
        index_size = len(self.simhash_index)
        if not hasattr(self, "_lsh_bands") or getattr(self, "_lsh_index_size", -1) != index_size:
            lsh_bands: Dict[Tuple[int, int], List[str]] = {}
            num_bands = 4
            for existing_hash, particle_id in self.simhash_index.items():
                for band_idx, band_val in enumerate(_bands_from_simhash(existing_hash, num_bands=num_bands)):
                    key = (band_idx, band_val)
                    bucket = lsh_bands.get(key)
                    if bucket is None:
                        bucket = []
                        lsh_bands[key] = bucket
                    bucket.append(particle_id)
            self._lsh_bands = lsh_bands
            self._lsh_index_size = index_size

        # Collect candidate particle IDs that share at least one band with the query.
        candidates: set = set()
        num_bands = 4
        for band_idx, band_val in enumerate(_bands_from_simhash(simhash, num_bands=num_bands)):
            key = (band_idx, band_val)
            bucket = self._lsh_bands.get(key)
            if bucket:
                candidates.update(bucket)

        # If no candidates found via LSH (e.g., malformed simhash or very small index),
        # fall back to checking all entries.
        if not candidates:
            candidate_items = self.simhash_index.items()
        else:
            # Build (simhash, particle_id) pairs only for the candidate IDs.
            candidate_items = [
                (sh, pid) for sh, pid in self.simhash_index.items() if pid in candidates
            ]

        similar: List[str] = []
        for existing_hash, particle_id in candidate_items:
            if hamming_distance(simhash, existing_hash) <= threshold:
                similar.append(particle_id)
        return similar
    
    def _calculate_similarity_score(self, hash_a: str, hash_b: str) -> float:
        """
        Calculate similarity score from Hamming distance
        
        Args:
            hash_a: First SimHash
            hash_b: Second SimHash
            
        Returns:
            Similarity score (0.0 to 1.0)
        """
        distance = hamming_distance(hash_a, hash_b)
        max_distance = 64  # 64-bit hash
        
        # Convert distance to similarity
        similarity = 1.0 - (distance / max_distance)
        
        return similarity
    
    def _assign_layer(self, similarity_score: float) -> str:
        """
        Assign layer based on similarity score
        
        Args:
            similarity_score: Similarity score (0.0 to 1.0)
            
        Returns:
            Layer designation (L1-L5)
        """
        if similarity_score >= 0.9:
            return 'L1'
        elif similarity_score >= 0.75:
            return 'L2'
        elif similarity_score >= 0.6:
            return 'L3'
        elif similarity_score >= 0.4:
            return 'L4'
        else:
            return 'L5'
    
    def _calculate_frequency(self, layer: str) -> float:
        """Calculate frequency for layer"""
        return FREQ.get(layer, FREQ['L5'])
    
    def _merge_sources(self, existing: Particle, new_source: Dict) -> Particle:
        """
        Merge new source into existing particle
        
        Args:
            existing: Existing particle
            new_source: New source to merge
            
        Returns:
            Updated particle
        """
        # Add new source if not duplicate
        source_urls = [s.get('url', '') for s in existing.sources]
        
        if new_source.get('url', '') not in source_urls:
            existing.sources.append(new_source)
            
            # Update metadata
            existing.metadata['source_count'] = len(existing.sources)
            existing.metadata['last_updated'] = datetime.now().isoformat()
            
            logger.info(f"Merged source into particle {existing.id} "
                       f"(now {len(existing.sources)} sources)")
        
        return existing
    
    def store(
        self,
        name: str,
        particle_type: str,
        content: str,
        source_info: Dict,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> Tuple[Particle, bool]:
        """
        Store particle with deduplication
        
        Args:
            name: Particle name
            particle_type: Particle type (fx.*)
            content: Particle content
            source_info: Source information (repo, url, etc.)
            tags: Tags
            metadata: Additional metadata
            
        Returns:
            (particle, is_new) tuple
        """
        import uuid
        
        # Compute SimHash
        content_hash = simhash64(content)
        
        # Check for similar particles
        similar_ids = self._find_similar_particles(content_hash, threshold=3)
        
        if similar_ids:
            # Merge with existing particle
            existing_id = similar_ids[0]
            existing = Particle(**self.particles[existing_id])
            
            # Calculate similarity
            similarity = self._calculate_similarity_score(
                content_hash,
                existing.simhash
            )
            
            logger.info(f"Found similar particle {existing_id} "
                       f"(similarity: {similarity:.2%})")
            
            # Merge sources
            updated = self._merge_sources(existing, source_info)
            
            # Update in memory
            self.particles[existing_id] = updated.to_dict()
            
            return updated, False
        
        else:
            # Create new particle
            particle_id = str(uuid.uuid4())
            
            # For new particles, assign layer based on content quality
            # Use a default high similarity for new content
            layer = self._assign_layer(0.8)  # Default to L2
            frequency = self._calculate_frequency(layer)
            
            # Compute Merkle hash
            merkle_entry = self.merkle_chain.commit(
                content=content,
                simhash=content_hash,
                tags=tags or [],
                layer=layer,
                meta={'particle_id': particle_id, 'name': name}
            )
            
            particle = Particle(
                id=particle_id,
                name=name,
                type=particle_type,
                content=content,
                simhash=content_hash,
                layer=layer,
                frequency=frequency,
                sources=[source_info],
                tags=tags or [],
                merkle=merkle_entry.merkle,
                timestamp=datetime.now().isoformat(),
                metadata={
                    'source_count': 1,
                    'created': datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
            
            # Store particle
            self.particles[particle_id] = particle.to_dict()
            self.simhash_index[content_hash] = particle_id
            self._save_particle(particle)
            
            logger.info(f"Created new particle {particle_id} ({name}) in {layer}")
            
            return particle, True
    
    def get(self, particle_id: str) -> Optional[Particle]:
        """Retrieve particle by ID"""
        if particle_id in self.particles:
            return Particle(**self.particles[particle_id])
        return None
    
    def search_by_layer(self, layer: str) -> List[Particle]:
        """Search particles by layer"""
        results = []
        
        for particle_data in self.particles.values():
            if particle_data['layer'] == layer:
                results.append(Particle(**particle_data))
        
        return results
    
    def search_by_tag(self, tag: str) -> List[Particle]:
        """Search particles by tag"""
        results = []
        
        for particle_data in self.particles.values():
            if tag in particle_data.get('tags', []):
                results.append(Particle(**particle_data))
        
        return results
    
    def search_by_type(self, particle_type: str) -> List[Particle]:
        """Search particles by type"""
        results = []
        
        for particle_data in self.particles.values():
            if particle_data['type'] == particle_type:
                results.append(Particle(**particle_data))
        
        return results
    
    def search_by_frequency(
        self,
        target_freq: float,
        tolerance: float = 0.5
    ) -> List[Particle]:
        """
        Search particles by frequency resonance
        
        Args:
            target_freq: Target frequency (Hz)
            tolerance: Frequency tolerance (±Hz)
            
        Returns:
            List of resonant particles
        """
        results = []
        
        for particle_data in self.particles.values():
            freq = particle_data['frequency']
            if abs(freq - target_freq) <= tolerance:
                results.append(Particle(**particle_data))
        
        return results
    
    def verify_merkle_chain(self) -> Tuple[bool, List[str]]:
        """Verify Merkle chain integrity"""
        return self.merkle_chain.verify()
    
    def get_statistics(self) -> Dict:
        """Get storage statistics"""
        stats = {
            'total_particles': len(self.particles),
            'by_layer': {},
            'by_type': {},
            'merkle_valid': False,
            'merkle_errors': []
        }
        
        # Count by layer
        for particle_data in self.particles.values():
            layer = particle_data['layer']
            stats['by_layer'][layer] = stats['by_layer'].get(layer, 0) + 1
            
            ptype = particle_data['type']
            stats['by_type'][ptype] = stats['by_type'].get(ptype, 0) + 1
        
        # Verify Merkle chain
        valid, errors = self.verify_merkle_chain()
        stats['merkle_valid'] = valid
        stats['merkle_errors'] = errors
        
        return stats
    
    def export_particles(self, output_path: str):
        """Export all particles to JSON"""
        export_data = {
            'total': len(self.particles),
            'timestamp': datetime.now().isoformat(),
            'particles': list(self.particles.values())
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(self.particles)} particles to {output_path}")


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Particle Memory Storage')
    parser.add_argument('--test', action='store_true', help='Run test')
    parser.add_argument('--stats', action='store_true', help='Show statistics')
    parser.add_argument('--export', help='Export particles to JSON')
    
    args = parser.parse_args()
    
    storage = ParticleMemoryStorage('./particle_storage_test')
    
    if args.test:
        print("=== Particle Memory Storage Test ===\n")
        
        # Test 1: Store new particle
        print("Test 1: Store new particle")
        particle1, is_new1 = storage.store(
            name='fx.pattern.attention.test',
            particle_type='fx.pattern.attention',
            content='Multi-head attention mechanism with query, key, value matrices',
            source_info={
                'repo': 'user/attention-lib',
                'url': 'https://github.com/user/attention-lib',
                'language': 'Python'
            },
            tags=['attention', 'neural', 'test']
        )
        print(f"Stored: {particle1.name}")
        print(f"ID: {particle1.id}")
        print(f"Layer: {particle1.layer}")
        print(f"New: {is_new1}\n")
        
        # Test 2: Store similar particle (should merge)
        print("Test 2: Store similar particle (should merge)")
        particle2, is_new2 = storage.store(
            name='fx.pattern.attention.test',
            particle_type='fx.pattern.attention',
            content='Multi-head attention mechanism with query, key, value vectors',
            source_info={
                'repo': 'user/another-lib',
                'url': 'https://github.com/user/another-lib',
                'language': 'TypeScript'
            },
            tags=['attention', 'test']
        )
        print(f"Stored: {particle2.name}")
        print(f"ID: {particle2.id}")
        print(f"Sources: {len(particle2.sources)}")
        print(f"New: {is_new2} (should be False)\n")
        
        # Test 3: Search by layer
        print("Test 3: Search by layer")
        l2_particles = storage.search_by_layer('L2')
        print(f"Found {len(l2_particles)} particles in L2\n")
        
        # Test 4: Search by tag
        print("Test 4: Search by tag")
        attention_particles = storage.search_by_tag('attention')
        print(f"Found {len(attention_particles)} particles with tag 'attention'\n")
        
        # Test 5: Frequency search
        print("Test 5: Frequency resonance")
        target_freq = FREQ['L2']
        resonant = storage.search_by_frequency(target_freq, tolerance=0.5)
        print(f"Found {len(resonant)} particles resonant with {target_freq:.2f}Hz\n")
    
    if args.stats:
        stats = storage.get_statistics()
        print("\n=== Storage Statistics ===")
        print(f"Total particles: {stats['total_particles']}")
        print(f"\nBy layer:")
        for layer, count in sorted(stats['by_layer'].items()):
            print(f"  {layer}: {count}")
        print(f"\nBy type:")
        for ptype, count in sorted(stats['by_type'].items()):
            print(f"  {ptype}: {count}")
        print(f"\nMerkle chain valid: {stats['merkle_valid']}")
        if stats['merkle_errors']:
            print(f"Errors:")
            for error in stats['merkle_errors']:
                print(f"  - {error}")
    
    if args.export:
        storage.export_particles(args.export)
        print(f"Particles exported to {args.export}")
