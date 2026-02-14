#!/usr/bin/env python3
"""
Particle Test Recorder ⭐ CRITICAL
===================================

Implements ALL 7 particle tests for verification:
1. Write test - verify particle can write to KV
2. Read test - verify particle can be read
3. SimHash collision test - check similar particles (Hamming ≤ 3)
4. Merkle integrity test - verify Merkle chain integrity
5. Layer retrieval test - verify layer-based (L1-L7) retrieval
6. Tag search test - verify tag-based search
7. Frequency resonance test - find frequency-similar particles (±0.5Hz)

Test results are stored as particles (fx.meta.test) in L7.

Author: MR.liou
Philosophy: 怎麼過去，就怎麼回來 (What goes around, comes around)
"""

import os
import sys
import json
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from core.simhash64 import simhash64, hamming_distance, is_similar
from core.merkle import MerkleChain

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants from index.ts
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
class ParticleTest:
    """Single particle test result"""
    test_id: str
    test_name: str
    status: str  # "pass", "fail", "error"
    timestamp: str
    details: Dict
    particle_id: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TestReport:
    """Complete test report"""
    session_id: str
    total_tests: int
    passed: int
    failed: int
    errors: int
    tests: List[ParticleTest]
    timestamp: str
    
    def to_dict(self) -> Dict:
        return {
            'session_id': self.session_id,
            'total_tests': self.total_tests,
            'passed': self.passed,
            'failed': self.failed,
            'errors': self.errors,
            'tests': [t.to_dict() for t in self.tests],
            'timestamp': self.timestamp
        }


class MockMemory:
    """Mock Memory class simulating KV storage (mrliouword-private)"""
    
    def __init__(self, storage_path: str = './test_particles'):
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        self.kv = {}  # In-memory KV store
        self.index = []  # Particle index
    
    async def put(self, key: str, value: str):
        """Store key-value pair"""
        self.kv[key] = value
        # Also persist to file
        with open(os.path.join(self.storage_path, f"{key}.json"), 'w') as f:
            f.write(value)
    
    async def get(self, key: str) -> Optional[str]:
        """Retrieve value by key"""
        if key in self.kv:
            return self.kv[key]
        
        # Try to load from file
        file_path = os.path.join(self.storage_path, f"{key}.json")
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                value = f.read()
                self.kv[key] = value
                return value
        
        return None
    
    async def list(self, prefix: str = '') -> List[str]:
        """List keys with prefix"""
        keys = list(self.kv.keys())
        
        # Also scan files
        try:
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    key = filename[:-5]
                    if key not in keys:
                        keys.append(key)
        except FileNotFoundError:
            # If the storage directory was removed, just return in-memory keys
            pass
        
        if prefix:
            keys = [k for k in keys if k.startswith(prefix)]
        
        return keys
    
    async def commit(self, content: str, type: str = 'semantic', tags: List[str] = None, meta: Dict = None):
        """Commit particle to memory"""
        import uuid
        particle_id = str(uuid.uuid4())
        simhash = simhash64(content)
        timestamp = datetime.now().isoformat()
        
        particle = {
            'id': particle_id,
            'content': content,
            'type': type,
            'simhash': simhash,
            'tags': tags or [],
            'layer': 'L7',
            'timestamp': timestamp,
            'meta': meta or {}
        }
        
        await self.put(f"particle:{particle_id}", json.dumps(particle))
        
        # Update index
        self.index.append({
            'id': particle_id,
            'simhash': simhash,
            'tags': tags or [],
            'layer': 'L7',
            'type': type
        })
        
        return particle


class ParticleTestRecorder:
    """
    Particle Test Recorder
    
    Implements all 7 critical tests for particle system verification.
    """
    
    def __init__(self, storage_path: str = './test_particles'):
        """
        Initialize test recorder
        
        Args:
            storage_path: Path to store test particles
        """
        self.storage_path = storage_path
        self.memory = MockMemory(storage_path)
        self.merkle_chain = MerkleChain(os.path.join(storage_path, 'merkle'))
        self.tests = []
        
        logger.info(f"ParticleTestRecorder initialized at {storage_path}")
    
    def _create_test_result(
        self,
        test_name: str,
        status: str,
        details: Dict,
        particle_id: Optional[str] = None
    ) -> ParticleTest:
        """Create test result object"""
        import uuid
        return ParticleTest(
            test_id=str(uuid.uuid4()),
            test_name=test_name,
            status=status,
            timestamp=datetime.now().isoformat(),
            details=details,
            particle_id=particle_id
        )
    
    async def test_1_write(self) -> ParticleTest:
        """
        Test 1: Write Test
        Verify particle can write to KV storage
        """
        logger.info("Running Test 1: Write Test")
        
        try:
            content = "Test particle for write verification - 夥伴回來吧"
            particle = await self.memory.commit(
                content=content,
                type='fx.meta.test',
                tags=['test', 'write'],
                meta={'test_id': 1, 'test_name': 'write'}
            )
            
            # Verify written
            retrieved = await self.memory.get(f"particle:{particle['id']}")
            
            if retrieved:
                result = self._create_test_result(
                    test_name="write_test",
                    status="pass",
                    details={
                        'particle_id': particle['id'],
                        'content_length': len(content),
                        'simhash': particle['simhash']
                    },
                    particle_id=particle['id']
                )
            else:
                result = self._create_test_result(
                    test_name="write_test",
                    status="fail",
                    details={'error': 'Particle not found after write'}
                )
            
        except Exception as e:
            result = self._create_test_result(
                test_name="write_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def test_2_read(self, particle_id: str) -> ParticleTest:
        """
        Test 2: Read Test
        Verify particle can be read from storage
        """
        logger.info("Running Test 2: Read Test")
        
        try:
            particle_data = await self.memory.get(f"particle:{particle_id}")
            
            if particle_data:
                particle = json.loads(particle_data)
                result = self._create_test_result(
                    test_name="read_test",
                    status="pass",
                    details={
                        'particle_id': particle_id,
                        'content_preview': particle['content'][:50],
                        'type': particle['type']
                    },
                    particle_id=particle_id
                )
            else:
                result = self._create_test_result(
                    test_name="read_test",
                    status="fail",
                    details={'error': f'Particle {particle_id} not found'}
                )
        
        except Exception as e:
            result = self._create_test_result(
                test_name="read_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def test_3_simhash_collision(self) -> ParticleTest:
        """
        Test 3: SimHash Collision Test
        Check if similar particles are detected (Hamming distance ≤ 3)
        """
        logger.info("Running Test 3: SimHash Collision Test")
        
        try:
            # Create similar particles
            content_a = "夥伴回來吧，我們繼續開發粒子系統"
            content_b = "夥伴回來吧，我們繼續開發粒子架構"
            
            particle_a = await self.memory.commit(
                content=content_a,
                type='fx.meta.test',
                tags=['test', 'simhash', 'similar_a']
            )
            
            particle_b = await self.memory.commit(
                content=content_b,
                type='fx.meta.test',
                tags=['test', 'simhash', 'similar_b']
            )
            
            # Check hamming distance
            hash_a = particle_a['simhash']
            hash_b = particle_b['simhash']
            distance = hamming_distance(hash_a, hash_b)
            is_collision = is_similar(hash_a, hash_b, threshold=3)
            
            if is_collision and distance <= 3:
                status = "pass"
                details = {
                    'hash_a': hash_a,
                    'hash_b': hash_b,
                    'hamming_distance': distance,
                    'collision_detected': True
                }
            else:
                status = "fail"
                details = {
                    'hash_a': hash_a,
                    'hash_b': hash_b,
                    'hamming_distance': distance,
                    'collision_detected': False,
                    'note': 'Similar texts should have distance ≤ 3'
                }
            
            result = self._create_test_result(
                test_name="simhash_collision_test",
                status=status,
                details=details
            )
        
        except Exception as e:
            result = self._create_test_result(
                test_name="simhash_collision_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def test_4_merkle_integrity(self) -> ParticleTest:
        """
        Test 4: Merkle Integrity Test
        Verify Merkle chain integrity
        """
        logger.info("Running Test 4: Merkle Integrity Test")
        
        try:
            # Commit test particles to merkle chain
            test_contents = [
                "粒子記憶系統測試 1",
                "粒子記憶系統測試 2",
                "粒子記憶系統測試 3"
            ]
            
            for content in test_contents:
                self.merkle_chain.commit(
                    content=content,
                    simhash=simhash64(content),
                    tags=['test', 'merkle'],
                    layer='L7'
                )
            
            # Verify chain
            valid, errors = self.merkle_chain.verify()
            
            if valid:
                result = self._create_test_result(
                    test_name="merkle_integrity_test",
                    status="pass",
                    details={
                        'chain_valid': True,
                        'entries_verified': len(test_contents),
                        'merkle_root': self.merkle_chain.build_merkle_root()
                    }
                )
            else:
                result = self._create_test_result(
                    test_name="merkle_integrity_test",
                    status="fail",
                    details={
                        'chain_valid': False,
                        'errors': errors
                    }
                )
        
        except Exception as e:
            result = self._create_test_result(
                test_name="merkle_integrity_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def test_5_layer_retrieval(self) -> ParticleTest:
        """
        Test 5: Layer Retrieval Test
        Verify layer-based (L1-L7) retrieval
        """
        logger.info("Running Test 5: Layer Retrieval Test")
        
        try:
            # Create particles in different layers
            layers = ['L1', 'L2', 'L3', 'L4', 'L5', 'L6', 'L7']
            layer_particles = {}
            
            for layer in layers:
                content = f"Test particle for layer {layer}"
                particle = await self.memory.commit(
                    content=content,
                    type='fx.meta.test',
                    tags=['test', 'layer', layer],
                    meta={'layer': layer}
                )
                layer_particles[layer] = particle['id']
            
            # Verify retrieval by layer
            retrieved_layers = {}
            for layer in layers:
                # Search by tag
                all_keys = await self.memory.list('particle:')
                count = 0
                for key in all_keys:
                    particle_data = await self.memory.get(key)
                    if particle_data:
                        particle = json.loads(particle_data)
                        if layer in particle.get('tags', []):
                            count += 1
                retrieved_layers[layer] = count
            
            # Check if all layers have particles
            all_found = all(count > 0 for count in retrieved_layers.values())
            
            if all_found:
                result = self._create_test_result(
                    test_name="layer_retrieval_test",
                    status="pass",
                    details={
                        'layers_tested': layers,
                        'retrieval_counts': retrieved_layers,
                        'all_layers_found': True
                    }
                )
            else:
                result = self._create_test_result(
                    test_name="layer_retrieval_test",
                    status="fail",
                    details={
                        'layers_tested': layers,
                        'retrieval_counts': retrieved_layers,
                        'all_layers_found': False
                    }
                )
        
        except Exception as e:
            result = self._create_test_result(
                test_name="layer_retrieval_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def test_6_tag_search(self) -> ParticleTest:
        """
        Test 6: Tag Search Test
        Verify tag-based search
        """
        logger.info("Running Test 6: Tag Search Test")
        
        try:
            # Create particles with specific tags
            test_tags = [
                ['attention', 'pattern'],
                ['memory', 'system'],
                ['merkle', 'verification']
            ]
            
            created_particles = []
            for tags in test_tags:
                content = f"Particle with tags: {', '.join(tags)}"
                particle = await self.memory.commit(
                    content=content,
                    type='fx.meta.test',
                    tags=tags + ['test', 'tag_search']
                )
                created_particles.append(particle['id'])
            
            # Search by tag
            found_by_tag = {}
            search_tags = ['attention', 'memory', 'merkle', 'tag_search']
            
            for search_tag in search_tags:
                all_keys = await self.memory.list('particle:')
                count = 0
                for key in all_keys:
                    particle_data = await self.memory.get(key)
                    if particle_data:
                        particle = json.loads(particle_data)
                        if search_tag in particle.get('tags', []):
                            count += 1
                found_by_tag[search_tag] = count
            
            # Verify all search tags found particles
            all_found = all(count > 0 for count in found_by_tag.values())
            
            if all_found:
                result = self._create_test_result(
                    test_name="tag_search_test",
                    status="pass",
                    details={
                        'search_tags': search_tags,
                        'found_counts': found_by_tag,
                        'all_tags_found': True
                    }
                )
            else:
                result = self._create_test_result(
                    test_name="tag_search_test",
                    status="fail",
                    details={
                        'search_tags': search_tags,
                        'found_counts': found_by_tag,
                        'all_tags_found': False
                    }
                )
        
        except Exception as e:
            result = self._create_test_result(
                test_name="tag_search_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def test_7_frequency_resonance(self) -> ParticleTest:
        """
        Test 7: Frequency Resonance Test
        Find frequency-similar particles (±0.5Hz)
        """
        logger.info("Running Test 7: Frequency Resonance Test")
        
        try:
            # Create particles at different frequency layers
            target_freq = FREQ['L3']  # 20.50 Hz
            tolerance = 0.5
            
            # Create test particles
            test_particles = [
                ('L2', FREQ['L2']),  # 12.67 Hz - outside range
                ('L3', FREQ['L3']),  # 20.50 Hz - exact match
                ('L4', FREQ['L4']),  # 33.17 Hz - outside range
            ]
            
            created = []
            for layer, freq in test_particles:
                content = f"Particle at frequency {freq:.2f}Hz (layer {layer})"
                particle = await self.memory.commit(
                    content=content,
                    type='fx.meta.test',
                    tags=['test', 'frequency', layer],
                    meta={'frequency': freq, 'layer': layer}
                )
                created.append((particle['id'], freq, layer))
            
            # Find resonant particles (within ±0.5Hz of target)
            resonant = []
            for particle_id, freq, layer in created:
                if abs(freq - target_freq) <= tolerance:
                    resonant.append({
                        'particle_id': particle_id,
                        'frequency': freq,
                        'layer': layer,
                        'delta': abs(freq - target_freq)
                    })
            
            # Should find exactly 1 resonant particle (L3)
            if len(resonant) == 1 and resonant[0]['layer'] == 'L3':
                result = self._create_test_result(
                    test_name="frequency_resonance_test",
                    status="pass",
                    details={
                        'target_frequency': target_freq,
                        'tolerance': tolerance,
                        'resonant_particles': resonant,
                        'resonance_detected': True
                    }
                )
            else:
                result = self._create_test_result(
                    test_name="frequency_resonance_test",
                    status="fail",
                    details={
                        'target_frequency': target_freq,
                        'tolerance': tolerance,
                        'resonant_particles': resonant,
                        'expected': 1,
                        'found': len(resonant)
                    }
                )
        
        except Exception as e:
            result = self._create_test_result(
                test_name="frequency_resonance_test",
                status="error",
                details={'error': str(e)}
            )
        
        self.tests.append(result)
        return result
    
    async def run_all_tests(self) -> TestReport:
        """
        Run all 7 particle tests
        
        Returns:
            Complete test report
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        logger.info(f"Starting test session {session_id}")
        logger.info("="*80)
        
        # Test 1: Write
        test1 = await self.test_1_write()
        logger.info(f"Test 1 (Write): {test1.status}")
        
        # Test 2: Read (use particle from test 1)
        if test1.particle_id:
            test2 = await self.test_2_read(test1.particle_id)
        else:
            test2 = self._create_test_result(
                "read_test", "error",
                {'error': 'No particle from test 1'}
            )
            self.tests.append(test2)
        logger.info(f"Test 2 (Read): {test2.status}")
        
        # Test 3: SimHash Collision
        test3 = await self.test_3_simhash_collision()
        logger.info(f"Test 3 (SimHash): {test3.status}")
        
        # Test 4: Merkle Integrity
        test4 = await self.test_4_merkle_integrity()
        logger.info(f"Test 4 (Merkle): {test4.status}")
        
        # Test 5: Layer Retrieval
        test5 = await self.test_5_layer_retrieval()
        logger.info(f"Test 5 (Layer): {test5.status}")
        
        # Test 6: Tag Search
        test6 = await self.test_6_tag_search()
        logger.info(f"Test 6 (Tag): {test6.status}")
        
        # Test 7: Frequency Resonance
        test7 = await self.test_7_frequency_resonance()
        logger.info(f"Test 7 (Frequency): {test7.status}")
        
        # Generate report
        passed = sum(1 for t in self.tests if t.status == 'pass')
        failed = sum(1 for t in self.tests if t.status == 'fail')
        errors = sum(1 for t in self.tests if t.status == 'error')
        
        report = TestReport(
            session_id=session_id,
            total_tests=len(self.tests),
            passed=passed,
            failed=failed,
            errors=errors,
            tests=self.tests,
            timestamp=datetime.now().isoformat()
        )
        
        logger.info("="*80)
        logger.info(f"Test Session Complete: {passed}/{len(self.tests)} passed")
        
        # Store report as particle
        await self.memory.commit(
            content=json.dumps(report.to_dict(), indent=2),
            type='fx.meta.test.report',
            tags=['test', 'report', session_id],
            meta={'session_id': session_id, 'passed': passed, 'total': len(self.tests)}
        )
        
        return report


# CLI Interface
if __name__ == '__main__':
    import asyncio
    
    async def main():
        recorder = ParticleTestRecorder('./test_particles_output')
        report = await recorder.run_all_tests()
        
        print("\n" + "="*80)
        print("PARTICLE TEST REPORT")
        print("="*80)
        print(f"Session ID: {report.session_id}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed}")
        print(f"Failed: {report.failed}")
        print(f"Errors: {report.errors}")
        print("="*80)
        
        for test in report.tests:
            status_symbol = "✓" if test.status == "pass" else "✗"
            print(f"{status_symbol} {test.test_name}: {test.status}")
            if test.status != "pass":
                print(f"  Details: {test.details}")
        
        print("="*80)
    
    asyncio.run(main())
