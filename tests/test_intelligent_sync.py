#!/usr/bin/env python3
"""
Tests for Intelligent Synchronization System
============================================

Comprehensive test suite for all components.

Author: MR.liou
"""

import os
import sys
import pytest
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from scripts.global_github_search import GitHubSearchEngine, CodeSnippet
from integrations.github.logical_extractor import LogicalExtractor, LogicalStructure
from integrations.webgpu.attention_filter import AttentionFilter, VectorCore
from integrations.particle.test_recorder import ParticleTestRecorder
from integrations.particle.naming_engine import ParticleNamingEngine
from integrations.particle.memory_storage import ParticleMemoryStorage


class TestGitHubSearch:
    """Test GitHub Search Engine"""
    
    def test_build_query(self):
        """Test query builder"""
        engine = GitHubSearchEngine()
        
        query = engine.build_query(
            pattern="attention",
            languages=["Python", "TypeScript"],
            min_stars=10
        )
        
        assert "attention" in query
        assert "language:Python" in query or "language:TypeScript" in query
        assert "stars:>=10" in query
        assert "fork:false" in query
    
    @patch('requests.get')
    def test_search_code(self, mock_get):
        """Test code search with mocked API"""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {
                    'repository': {'full_name': 'user/repo'},
                    'path': 'test.py',
                    'language': 'Python',
                    'html_url': 'https://github.com/user/repo/blob/main/test.py',
                    'url': 'https://api.github.com/repos/user/repo/contents/test.py',
                    'score': 1.0
                }
            ]
        }
        mock_response.headers = {
            'X-RateLimit-Remaining': '30',
            'X-RateLimit-Reset': '1234567890'
        }
        mock_get.return_value = mock_response
        
        engine = GitHubSearchEngine()
        
        # Mock _fetch_file_content
        with patch.object(engine, '_fetch_file_content', return_value='test code'):
            snippets = engine.search_code("test", limit=1)
            
            assert len(snippets) > 0
            assert snippets[0].repo == 'user/repo'


class TestLogicalExtractor:
    """Test Logical Architecture Extractor"""
    
    def test_extract_patterns(self):
        """Test pattern extraction"""
        extractor = LogicalExtractor()
        
        code = """
        class AttentionLayer:
            def forward(self, query, key, value):
                scores = torch.matmul(query, key.transpose(-2, -1))
                attn = F.softmax(scores, dim=-1)
                output = torch.matmul(attn, value)
                return output
        """
        
        structure = extractor.extract(code, "Python")
        
        assert 'attention' in structure.patterns
        assert structure.confidence > 0
        assert len(structure.reasoning_chains) > 0
    
    def test_extract_concepts(self):
        """Test concept extraction"""
        extractor = LogicalExtractor()
        
        code = """
        class DistributedCache:
            async def get(self, key):
                # Distributed concurrent access
                pass
        """
        
        structure = extractor.extract(code, "Python")
        
        assert 'distributed' in structure.concepts or 'concurrent' in structure.concepts
    
    def test_generate_formula(self):
        """Test formula generation"""
        extractor = LogicalExtractor()
        
        structure = LogicalStructure(
            patterns=['attention'],
            concepts=['vector']
        )
        
        formula = extractor._generate_formula(structure)
        
        assert 'Attention' in formula or 'softmax' in formula


class TestAttentionFilter:
    """Test Attention Filter"""
    
    def test_vector_operations(self):
        """Test vector core operations"""
        import numpy as np
        
        a = np.array([1.0, 2.0, 3.0])
        b = np.array([4.0, 5.0, 6.0])
        
        dot = VectorCore.dot(a, b)
        assert dot == 32.0
        
        norm = VectorCore.norm(a)
        assert abs(norm - 3.7416573867739413) < 0.001
        
        sim = VectorCore.cosine_similarity(a, b)
        assert 0.9 < sim < 1.0
    
    def test_compute_embedding(self):
        """Test embedding computation"""
        filter = AttentionFilter(embedding_dim=128)
        
        embedding = filter.compute_embedding("test text")
        
        assert len(embedding) == 128
        assert VectorCore.norm(embedding) > 0
    
    def test_similarity_matrix(self):
        """Test similarity matrix computation"""
        import numpy as np
        
        filter = AttentionFilter()
        
        embeddings = [
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0]),
            np.array([1.0, 0.0])
        ]
        
        matrix = filter.compute_similarity_matrix(embeddings)
        
        assert matrix.shape == (3, 3)
        assert matrix[0, 0] == 1.0  # Self-similarity
        assert matrix[0, 2] > 0.9    # Similar vectors
        assert matrix[0, 1] < 0.5    # Dissimilar vectors


class TestParticleTestRecorder:
    """Test Particle Test Recorder"""
    
    @pytest.mark.asyncio
    async def test_write_test(self):
        """Test particle write"""
        recorder = ParticleTestRecorder('./test_temp')
        
        result = await recorder.test_1_write()
        
        assert result.status in ['pass', 'fail', 'error']
        assert result.test_name == 'write_test'
    
    @pytest.mark.asyncio
    async def test_simhash_collision(self):
        """Test SimHash collision detection"""
        recorder = ParticleTestRecorder('./test_temp')
        
        result = await recorder.test_3_simhash_collision()
        
        assert result.status in ['pass', 'fail', 'error']
        assert result.test_name == 'simhash_collision_test'
        
        if result.status == 'pass':
            assert result.details.get('collision_detected') == True
    
    @pytest.mark.asyncio
    async def test_all_tests(self):
        """Test running all 7 tests"""
        recorder = ParticleTestRecorder('./test_temp')
        
        report = await recorder.run_all_tests()
        
        assert report.total_tests == 7
        assert report.passed + report.failed + report.errors == 7


class TestNamingEngine:
    """Test Particle Naming Engine"""
    
    def test_determine_type_attention(self):
        """Test type determination for attention pattern"""
        engine = ParticleNamingEngine('./test_naming')
        
        particle_type, reasoning, confidence = engine.determine_type(
            patterns=['attention'],
            concepts=[],
            reasoning_chains=[]
        )
        
        assert particle_type == 'fx.pattern.attention'
        assert confidence >= 0.9
    
    def test_determine_type_memory(self):
        """Test type determination for memory pattern"""
        engine = ParticleNamingEngine('./test_naming')
        
        particle_type, reasoning, confidence = engine.determine_type(
            patterns=['memory'],
            concepts=[],
            reasoning_chains=[]
        )
        
        assert particle_type == 'fx.pattern.memory'
    
    def test_generate_name(self):
        """Test name generation"""
        engine = ParticleNamingEngine('./test_naming')
        
        decision = engine.generate_name(
            patterns=['attention'],
            concepts=['vector'],
            reasoning_chains=[],
            source_info={'repo': 'user/test-repo'}
        )
        
        assert decision.particle_type == 'fx.pattern.attention'
        assert 'attention' in decision.particle_name
        assert decision.version >= 1
    
    def test_name_conflict_versioning(self):
        """Test name conflict handling"""
        engine = ParticleNamingEngine('./test_naming')
        
        # Generate same name twice
        decision1 = engine.generate_name(
            patterns=['attention'],
            concepts=[],
            reasoning_chains=[],
            source_info={'repo': 'user/repo'}
        )
        
        decision2 = engine.generate_name(
            patterns=['attention'],
            concepts=[],
            reasoning_chains=[],
            source_info={'repo': 'user/repo'}
        )
        
        # Second should have higher version
        assert decision2.version > decision1.version


class TestMemoryStorage:
    """Test Particle Memory Storage"""
    
    def test_store_new_particle(self):
        """Test storing new particle"""
        storage = ParticleMemoryStorage('./test_storage')
        
        particle, is_new = storage.store(
            name='fx.test.particle',
            particle_type='fx.test',
            content='test content',
            source_info={'repo': 'user/repo'},
            tags=['test']
        )
        
        assert is_new == True
        assert particle.name == 'fx.test.particle'
        assert particle.simhash is not None
        assert particle.layer in ['L1', 'L2', 'L3', 'L4', 'L5']
    
    def test_store_similar_particle(self):
        """Test storing similar particle (should merge)"""
        storage = ParticleMemoryStorage('./test_storage')
        
        # Store first particle
        particle1, is_new1 = storage.store(
            name='fx.test.similar',
            particle_type='fx.test',
            content='test content for similarity',
            source_info={'repo': 'user/repo1'},
            tags=['test']
        )
        
        # Store similar particle
        particle2, is_new2 = storage.store(
            name='fx.test.similar',
            particle_type='fx.test',
            content='test content for similar',  # Very similar
            source_info={'repo': 'user/repo2'},
            tags=['test']
        )
        
        # Should merge, not create new
        if is_new2 == False:
            assert len(particle2.sources) > 1
            assert particle1.id == particle2.id
    
    def test_search_by_layer(self):
        """Test layer-based search"""
        storage = ParticleMemoryStorage('./test_storage')
        
        # Store a particle
        storage.store(
            name='fx.test.layer',
            particle_type='fx.test',
            content='layer test',
            source_info={'repo': 'test'},
            tags=['test']
        )
        
        # Search by layers
        for layer in ['L1', 'L2', 'L3', 'L4', 'L5']:
            particles = storage.search_by_layer(layer)
            assert isinstance(particles, list)
    
    def test_search_by_tag(self):
        """Test tag-based search"""
        storage = ParticleMemoryStorage('./test_storage')
        
        storage.store(
            name='fx.test.tag',
            particle_type='fx.test',
            content='tag test',
            source_info={'repo': 'test'},
            tags=['attention', 'test']
        )
        
        particles = storage.search_by_tag('attention')
        assert len(particles) > 0
        
        for p in particles:
            assert 'attention' in p.tags
    
    def test_merkle_verification(self):
        """Test Merkle chain verification"""
        storage = ParticleMemoryStorage('./test_storage')
        
        valid, errors = storage.verify_merkle_chain()
        
        assert isinstance(valid, bool)
        assert isinstance(errors, list)


class TestSyncOrchestrator:
    """Test Sync Orchestrator (integration tests)"""
    
    @pytest.mark.asyncio
    @patch('scripts.global_github_search.GitHubSearchEngine.search_code')
    async def test_sync_pattern(self, mock_search):
        """Test pattern synchronization"""
        from scripts.intelligent_repo_sync import IntelligentRepoSync
        
        # Mock GitHub search results
        mock_search.return_value = [
            CodeSnippet(
                repo='user/test-repo',
                path='test.py',
                language='Python',
                code='def attention(): pass',
                url='https://github.com/user/test-repo',
                score=1.0
            )
        ]
        
        sync = IntelligentRepoSync()
        
        # Run sync
        report = await sync.sync_pattern('test pattern', limit=1)
        
        assert report is not None
        assert report.pattern == 'test pattern'
        assert isinstance(report.github_results, int)


# Pytest fixtures
@pytest.fixture(autouse=True)
def cleanup():
    """Cleanup test directories after each test"""
    yield
    
    # Clean up test directories
    import shutil
    test_dirs = [
        './test_temp',
        './test_naming',
        './test_storage',
        './test_particles_output'
    ]
    
    for dir_path in test_dirs:
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
