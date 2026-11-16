#!/usr/bin/env python3
"""
Tests for Intelligent Synchronization System
============================================

Comprehensive test suite for all components.

Author: MR.liou
"""

import base64
import hashlib
import json
import runpy
import sys
from pathlib import Path
from textwrap import dedent
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
import requests

from integrations.github.logical_extractor import LogicalStructureExtractor
from integrations.particle.memory_storage import ParticleMemoryStorage
from integrations.particle.naming_engine import ParticleNamingEngine
from integrations.particle.test_recorder import ParticleTestRecorder
from integrations.particle.test_recorder import TestReport as ParticleValidationReport
from integrations.webgpu.attention_filter import AttentionFilter, VectorCore
from scripts import global_github_search
from scripts.global_github_search import GitHubSearchEngine

SYNC_SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'intelligent_repo_sync.py'
SEARCH_URL = 'https://api.github.com/search/code'
SYNTHETIC_CODE = dedent('''
    origin_signature = 'MrLiouWord'

    def PreserveOriginalName(query, key, value):
        if query:
            return recall_context(key)
        return value

    def recall_context(key):
        return verify_chain(key)

    def verify_chain(key):
        return key
''')


def github_file(path='Src/OriginalName.py', ref='a' * 40, code=SYNTHETIC_CODE):
    raw = code.encode('utf-8')
    repository = {
        'full_name': 'ExampleOrg/FixtureRepo',
        'url': 'https://api.github.com/repos/ExampleOrg/FixtureRepo',
        'fork': False,
    }
    item = {
        'name': Path(path).name,
        'path': path,
        'sha': hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii') + raw).hexdigest(),
        'url': f"{repository['url']}/contents/{path}?ref={ref}",
        'html_url': f"https://github.com/{repository['full_name']}/blob/{ref}/{path}",
        'repository': repository,
        'score': 1.0,
    }
    return item, {'content': base64.b64encode(raw).decode('ascii')}


def response(data, status=200, headers=None):
    result = Mock(spec=requests.Response)
    result.status_code = status
    result.headers = headers or {}
    result.json.return_value = data
    return result


def configure_sync(tmp_path, **config):
    path = tmp_path / 'intelligent_sync.yaml'
    path.write_text(json.dumps({'github': {'languages': ['Python']}, **config}))
    return path


def read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]


class TestGitHubSearch:
    def test_build_query(self):
        engine = GitHubSearchEngine()
        assert engine.build_query('attention', 'Python') == 'attention language:Python'
        assert engine.build_query('attention', exclude_forks=False) == 'attention fork:true'

    def test_search_code(self, monkeypatch):
        python_item, python_content = github_file()
        ts_item, ts_content = github_file('Src/OriginalName.ts', code='const attention = 1;')
        fork_item, _ = github_file('Src/Fork.py')
        fork_item['repository']['fork'] = True
        low_star_item, _ = github_file('Src/LowStars.ts')
        low_star_item['repository'].update(full_name='ExampleOrg/SmallRepo', stargazers_count=1)
        get = Mock(side_effect=[
            response({'items': [python_item, fork_item]}),
            response({'items': [ts_item, low_star_item]}),
            response({'stargazers_count': 42}),
            response(python_content),
            response(ts_content),
        ])
        monkeypatch.setattr(requests, 'get', get)

        snippets = GitHubSearchEngine().search_code(
            'attention', languages=['Python', 'TypeScript'], min_stars=10, limit=3
        )

        assert [(s.path, s.language) for s in snippets] == [
            ('Src/OriginalName.py', 'Python'), ('Src/OriginalName.ts', 'TypeScript')
        ]
        assert snippets[0].original_name == 'OriginalName.py'
        assert snippets[0].commit_sha == 'a' * 40
        assert snippets[0].blob_sha == python_item['sha']
        assert snippets[0].code == SYNTHETIC_CODE
        assert [call.args[0] for call in get.call_args_list] == [
            SEARCH_URL, SEARCH_URL, python_item['repository']['url'], python_item['url'], ts_item['url']
        ]
        assert [call.kwargs['params'] for call in get.call_args_list[:2]] == [
            {'q': 'attention language:Python', 'per_page': 3},
            {'q': 'attention language:TypeScript', 'per_page': 3},
        ]

    def test_unspecified_language_and_ref(self, monkeypatch):
        item, contents = github_file('Src/OriginalName.py', ref='topic-branch')
        item['repository']['stargazers_count'] = 42
        monkeypatch.setattr(requests, 'get', Mock(side_effect=[
            response({'items': [item]}), response(contents)
        ]))
        snippet, = GitHubSearchEngine().search_code('attention')
        assert snippet.language == 'Python'
        assert snippet.commit_sha is None
        assert snippet.blob_sha == item['sha']

    @pytest.mark.parametrize(
        'limited_response,expected_delay',
        [
            (response({}, 429, {'Retry-After': '8'}), 8),
            (response({}, 403, {
                'Retry-After': '3',
                'X-RateLimit-Remaining': '0',
                'X-RateLimit-Reset': '100010',
            }), 11),
        ],
    )
    def test_rate_limit_honors_server_wait(self, monkeypatch, limited_response, expected_delay):
        clock = SimpleNamespace(time=lambda: 100000, sleep=Mock())
        monkeypatch.setattr(global_github_search, 'time', clock)
        item, contents = github_file()
        item['repository']['stargazers_count'] = 42
        get = Mock(side_effect=[limited_response, response({'items': [item]}), response(contents)])
        monkeypatch.setattr(requests, 'get', get)

        snippet, = GitHubSearchEngine().search_code('attention', languages=['Python'])

        assert snippet.blob_sha == item['sha']
        clock.sleep.assert_called_once_with(expected_delay)
        assert [call.args[0] for call in get.call_args_list] == [SEARCH_URL, SEARCH_URL, item['url']]

    def test_rate_limit_without_headers_backs_off(self, monkeypatch):
        clock = SimpleNamespace(time=lambda: 100000, sleep=Mock())
        monkeypatch.setattr(global_github_search, 'time', clock)
        get = Mock(side_effect=[
            response({}, 429),
            response({'message': 'You have exceeded a secondary rate limit.'}, 403),
            response({'items': []}),
        ])
        monkeypatch.setattr(requests, 'get', get)
        assert GitHubSearchEngine().search_code('attention') == []
        assert [call.args[0] for call in clock.sleep.call_args_list] == [60, 120]
        assert get.call_count == 3

    def test_permission_failure_is_not_retried(self, monkeypatch):
        clock = SimpleNamespace(time=lambda: 100000, sleep=Mock())
        monkeypatch.setattr(global_github_search, 'time', clock)
        denied = response({'message': 'Resource not accessible by integration'}, 403)
        denied.raise_for_status.side_effect = requests.HTTPError('403 Forbidden')
        get = Mock(return_value=denied)
        monkeypatch.setattr(requests, 'get', get)
        with pytest.raises(requests.HTTPError, match='403 Forbidden'):
            GitHubSearchEngine().search_code('attention')
        clock.sleep.assert_not_called()
        get.assert_called_once()


class TestLogicalExtractor:
    """Test Logical Architecture Extractor"""
    
    def test_extract_patterns(self):
        structure = LogicalStructureExtractor().extract_from_code(SYNTHETIC_CODE, 'Python')
        assert 'query' in structure['patterns']['attention_mechanism']
        assert 'memory_system' in structure['patterns']
        assert structure['reasoning_chains'] == [
            ['PreserveOriginalName', 'recall_context', 'verify_chain']
        ]

    def test_extract_concepts(self):
        code = dedent('''
            class DistributedCache:
                def GetOriginalName(self, key):
                    return key
        ''')
        structure = LogicalStructureExtractor().extract_from_code(code, 'Python')
        assert structure['concepts'] == ['DistributedCache', 'GetOriginalName']
        assert isinstance(structure['complexity'], float)
        assert 'cache' in structure['patterns']['memory_system']

    def test_extract_from_code_supports_unknown_language(self):
        structure = LogicalStructureExtractor().extract_from_code('unknown syntax', 'Unknown')
        assert structure['concepts'] == []
        assert 'unknown' in structure['keywords']
        assert structure['patterns'] == {}


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
        
        assert result.status == 'pass'
        assert result.details['collision_detected'] is True
        assert result.details['hamming_distance'] == 0
        assert result.details['distance_3_accepted'] is True
        assert result.details['distance_4_rejected'] is True
    
    @pytest.mark.asyncio
    async def test_all_tests(self):
        """Test running all 7 tests"""
        recorder = ParticleTestRecorder('./test_temp')
        
        report = await recorder.run_all_tests()
        
        assert report.total_tests == 7
        assert report.passed_all


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
    def test_cli_import(self, tmp_path, capsys, monkeypatch):
        monkeypatch.setattr(sys, 'argv', [str(SYNC_SCRIPT), '--help'])
        with pytest.raises(SystemExit) as command:
            runpy.run_path(str(SYNC_SCRIPT), run_name='__main__')
        assert command.value.code == 0
        assert '--pattern' in capsys.readouterr().out
        assert not list(tmp_path.iterdir())

    @pytest.mark.asyncio
    async def test_sync_pattern_preserves_each_source_and_candidate_version(self, tmp_path, monkeypatch):
        from scripts.intelligent_repo_sync import IntelligentRepoSync

        first, file_content = github_file()
        second, _ = github_file(ref='b' * 40)
        get = Mock(side_effect=[
            response({'items': [first, second]}),
            response({'stargazers_count': 42}),
            response(file_content),
            response(file_content),
        ])
        monkeypatch.setattr(requests, 'get', get)

        existing = {
            'particle_memory/particles.jsonl': {
                'id': 'legacy-1', 'name': 'Original名稱', 'version': '2.4.1',
                'origin_signature': 'MrLiouWord',
                'sources': [{'repo': 'Owner/Existing', 'path': 'Original名稱.py'}],
            },
            'naming_history/naming_history.jsonl': {
                'particle_name': 'Original名稱', 'version': 7, 'owner_review': 'APPROVED',
            },
            'test_results/legacy.jsonl': {'result': 'before'},
            'sync_reports/legacy.jsonl': {'result': 'before'},
        }
        original_bytes = {}
        for name, row in existing.items():
            path = tmp_path / name
            path.parent.mkdir()
            original_bytes[path] = (json.dumps(row, ensure_ascii=False) + '\n').encode('utf-8')
            path.write_bytes(original_bytes[path])
        config = configure_sync(
            tmp_path,
            particle_memory={'storage_path': './particle_memory'},
            naming={'storage_path': './naming_history'},
            testing={'enabled': True, 'storage_path': './test_results'},
            reporting={'output_dir': './sync_reports'},
        )

        sync = IntelligentRepoSync(config)
        report = await sync.sync_pattern('attention', limit=2)
        assert report.errors == []
        assert report.summary['success'] is True
        assert report.summary['attention_pairs'] == 1
        assert report.summary['storage_scope'] == 'candidate'
        assert report.summary['owner_review'] == 'PENDING'
        assert report.github_results == report.extracted_structures == 2
        assert report.particles_created == report.naming_decisions == 2
        assert report.particles_merged == 0
        assert report.test_results['passed'] == report.test_results['total'] == 7
        validation = json.loads(next(sync.candidate_dir.glob('test_results/*/report.json')).read_text())
        assert all(test['status'] == 'pass' for test in validation['tests'])

        staged = read_jsonl(sync.candidate_dir / 'particle_memory' / 'particles.jsonl')
        history = read_jsonl(sync.candidate_dir / 'naming_history' / 'naming_history.jsonl')
        reader = ParticleMemoryStorage(str(sync.candidate_dir / 'particle_memory'))
        assert reader.verify_merkle_chain() == (True, [])
        assert len(staged) == len(history) == 2
        assert staged[1]['name'] == f"{staged[0]['name']}_v2"
        for version, (item, particle, decision) in enumerate(zip([first, second], staged, history), 1):
            source, = particle['sources']
            assert source == decision['metadata']['source_info']
            assert source['repo'] == item['repository']['full_name']
            assert source['original_name'] == 'OriginalName.py'
            assert source['path'] == item['path']
            assert source['url'] == item['html_url']
            assert source['commit_sha'] == item['url'].split('ref=')[1]
            assert source['blob_sha'] == item['sha']
            assert source['source_provenance'] == 'unsigned_pending'
            assert 'origin_signature' not in source
            assert 'origin_signature' not in particle
            assert particle['metadata']['owner_review'] == 'PENDING'
            assert particle['metadata']['naming_version'] == decision['version'] == version
            assert particle['name'] == decision['particle_name']
            assert particle['type'] == 'fx.pattern.attention'
            assert 'attention_mechanism' in particle['tags']
            structure = json.loads(particle['content'])
            assert structure['concepts'][0] == 'PreserveOriginalName'
            assert structure['reasoning_chains'][0][0] == 'PreserveOriginalName'
            assert structure['patterns']['attention_mechanism'] == ['query', 'key', 'value']
            assert reader.get(particle['id']).to_dict() == particle

        assert {path: path.read_bytes() for path in original_bytes} == original_bytes
        saved_report = next(sync.candidate_dir.glob('sync_reports/*.json'))
        assert json.loads(saved_report.read_text()) == report.to_dict()

    @pytest.mark.asyncio
    async def test_flatten_reasoning_only_for_naming(self, tmp_path, monkeypatch):
        from scripts.intelligent_repo_sync import IntelligentRepoSync

        item, contents = github_file(code='def Alpha(): pass\ndef Beta(): pass\ndef Gamma(): pass')
        item['repository']['stargazers_count'] = 42
        monkeypatch.setattr(requests, 'get', Mock(side_effect=[
            response({'items': [item]}), response(contents)
        ]))

        sync = IntelligentRepoSync(configure_sync(tmp_path))
        report = await sync.sync_pattern('fixture', limit=1)
        assert report.summary['success'] is True
        decision, = sync.naming_engine.get_history()
        assert decision['metadata']['reasoning_chains'] == ['Alpha Beta Gamma']
        staged, = read_jsonl(sync.candidate_dir / 'particle_memory' / 'particles.jsonl')
        assert json.loads(staged['content'])['reasoning_chains'] == [['Alpha', 'Beta', 'Gamma']]

    def test_particle_validation_failure_exits_before_naming_or_storage(self, tmp_path, monkeypatch):
        item, contents = github_file()
        item['repository']['stargazers_count'] = 42
        monkeypatch.setattr(requests, 'get', Mock(side_effect=[
            response({'items': [item]}), response(contents)
        ]))
        failed = ParticleValidationReport('fixture', 7, 6, 1, 0, [], '2026-11-16T00:00:00Z')
        monkeypatch.setattr(ParticleTestRecorder, 'run_all_tests', AsyncMock(return_value=failed))
        config = configure_sync(tmp_path)
        monkeypatch.setattr(sys, 'argv', [str(SYNC_SCRIPT), '--config', str(config), '--pattern', 'fixture'])

        with pytest.raises(SystemExit) as command:
            runpy.run_path(str(SYNC_SCRIPT), run_name='__main__')
        assert command.value.code == 1
        report_file, = tmp_path.glob('sync_candidates/run-*/sync_reports/*.json')
        report = json.loads(report_file.read_text())
        assert report['errors'] == ['Particle validation: 6/7 tests passed; expected 7/7']
        assert report['summary']['success'] is False
        assert not list(tmp_path.glob('sync_candidates/run-*/particle_memory/particles.jsonl'))
        assert not list(tmp_path.glob('sync_candidates/run-*/naming_history/naming_history.jsonl'))

    @pytest.mark.asyncio
    async def test_blob_mismatch_blocks_storage(self, tmp_path, monkeypatch):
        from scripts.intelligent_repo_sync import IntelligentRepoSync

        item, _ = github_file()
        _, mismatched_contents = github_file(code='def OtherSource(): pass')
        item['repository']['stargazers_count'] = 42
        monkeypatch.setattr(requests, 'get', Mock(side_effect=[
            response({'items': [item]}), response(mismatched_contents)
        ]))

        sync = IntelligentRepoSync(configure_sync(tmp_path))
        report = await sync.sync_pattern('fixture')
        assert report.summary['success'] is False
        assert 'Git blob SHA mismatch' in report.errors[0]
        assert report.particles_created == 0
        assert not (sync.candidate_dir / 'particle_memory' / 'particles.jsonl').exists()

    @pytest.mark.asyncio
    async def test_storage_error_leaves_pending_evidence_and_retry_uses_a_fresh_directory(
        self, tmp_path, monkeypatch
    ):
        from scripts.intelligent_repo_sync import IntelligentRepoSync

        item, contents = github_file()
        item['repository']['stargazers_count'] = 42
        monkeypatch.setattr(requests, 'get', Mock(side_effect=[
            response({'items': [item]}), response(contents),
            response({'items': [item]}), response(contents),
        ]))
        config = configure_sync(tmp_path)

        first = IntelligentRepoSync(config)
        monkeypatch.setattr(first.memory_storage, 'store', Mock(side_effect=OSError('fixture disk error')))
        failed = await first.sync_pattern('fixture')
        assert failed.summary['success'] is False
        assert failed.errors == ['Candidate storage: fixture disk error']
        assert failed.particles_created == 0
        assert failed.naming_decisions == 1
        first_history = first.candidate_dir / 'naming_history' / 'naming_history.jsonl'
        history_before_retry = first_history.read_bytes()

        retry = IntelligentRepoSync(config)
        recovered = await retry.sync_pattern('fixture')
        assert recovered.summary['success'] is True
        assert recovered.particles_created == 1
        assert retry.candidate_dir != first.candidate_dir
        assert first_history.read_bytes() == history_before_retry

    def test_all_patterns_retains_each_result_and_returns_failure(self, tmp_path, monkeypatch):
        item, contents = github_file()
        item['repository']['stargazers_count'] = 42
        rejected = response({}, 403)
        rejected.raise_for_status.side_effect = requests.HTTPError('403 Forbidden')
        monkeypatch.setattr(requests, 'get', Mock(side_effect=[
            rejected, response({'items': [item]}), response(contents)
        ]))
        config = configure_sync(tmp_path, patterns=['no-access', 'candidate'])
        monkeypatch.setattr(sys, 'argv', [str(SYNC_SCRIPT), '--config', str(config), '--all'])

        with pytest.raises(SystemExit) as command:
            runpy.run_path(str(SYNC_SCRIPT), run_name='__main__')
        assert command.value.code == 1
        reports = {}
        for path in tmp_path.glob('sync_candidates/run-*/sync_reports/*.json'):
            data = json.loads(path.read_text())
            reports[data['pattern']] = data
        assert reports['no-access']['errors'] == ['GitHub search: 403 Forbidden']
        assert reports['no-access']['summary']['success'] is False
        assert reports['candidate']['summary']['success'] is True
        assert reports['candidate']['particles_created'] == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize('retry_after,expected_calls', [(None, 3), ('301', 1)])
    async def test_persistent_rate_limit_stops_later_patterns(
        self, tmp_path, monkeypatch, retry_after, expected_calls
    ):
        from scripts.intelligent_repo_sync import IntelligentRepoSync

        headers = {'X-GitHub-Request-Id': 'SYNTHETIC:01'}
        if retry_after is not None:
            headers['Retry-After'] = retry_after
        get = Mock(return_value=response({}, 429, headers))
        monkeypatch.setattr(requests, 'get', get)
        clock = SimpleNamespace(time=lambda: 100000, sleep=Mock())
        monkeypatch.setattr(global_github_search, 'time', clock)
        config = configure_sync(tmp_path, patterns=['initial', 'second', 'third'])

        sync = IntelligentRepoSync(config)
        first, *skipped = await sync.sync_all_patterns()

        assert get.call_count == expected_calls
        assert all('initial' in call.kwargs['params']['q'] for call in get.call_args_list)
        details = first.summary['github_rate_limit']
        assert details['http_status'] == 429
        assert details['request_id'] == 'SYNTHETIC:01'
        assert details['attempts'] == expected_calls
        assert details['retry_after'] == retry_after
        assert first.summary['success'] is False
        assert [report.pattern for report in skipped] == ['second', 'third']
        assert all(
            report.summary['status'] == 'SKIPPED_RATE_LIMIT'
            and report.summary['blocked_by_pattern'] == 'initial'
            and not report.summary['success']
            for report in skipped
        )
        assert all(report.particles_created == 0 for report in [first, *skipped])
        assert len(list(sync.candidate_dir.glob('sync_reports/*.json'))) == 3


@pytest.fixture(autouse=True)
def isolate_filesystem_and_network(tmp_path, monkeypatch):
    def unexpected_request(*args, **kwargs):
        raise AssertionError('Tests must stub GitHub HTTP at the request boundary')

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv('GITHUB_TOKEN', raising=False)
    monkeypatch.setattr(requests.sessions.Session, 'request', unexpected_request)


# Run tests
if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
