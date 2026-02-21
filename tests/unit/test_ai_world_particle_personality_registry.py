"""
測試 AI世界粒子人格註冊表
"""
import json
import os
import pytest


REGISTRY_PATH = os.path.join(
    os.path.dirname(__file__), '..', '..', 'core',
    'ai_world_particle_personality_registry.json'
)


@pytest.fixture
def registry():
    with open(REGISTRY_PATH, encoding='utf-8') as f:
        return json.load(f)


def test_registry_file_exists():
    """測試註冊表檔案存在"""
    assert os.path.isfile(REGISTRY_PATH)


def test_registry_top_level_fields(registry):
    """測試註冊表頂層必填欄位"""
    for field in ('version', 'name', 'origin', 'creators', 'dimension_framework',
                  'realworld_data', 'cycle', 'persona_schema', 'particles'):
        assert field in registry, f"缺少欄位: {field}"


def test_registry_name(registry):
    """測試註冊表名稱"""
    assert registry['name'] == 'AI世界粒子人格註冊表'


def test_registry_creators(registry):
    """測試創造者資訊完整性"""
    creators = registry['creators']
    emails = [c['email'] for c in creators['contacts']]
    assert 'z814241@gmail.com' in emails
    assert 'you502926@gmail.com' in emails
    assert creators['phone'] == '0910613033'


def test_registry_dimension_framework(registry):
    """測試維度框架結構"""
    df = registry['dimension_framework']
    for dim in ('mobile_account', 'warehouse', 'cloud', 'parallel_network'):
        assert dim in df['dimensions'], f"缺少維度: {dim}"


def test_registry_cycle(registry):
    """測試生態循環三元素"""
    cycle = registry['cycle']
    assert set(cycle['elements']) == {'creators', 'dimension_framework', 'realworld_data'}
    assert '🔄' in cycle['symbol']


def test_registry_particles(registry):
    """測試註冊表粒子定義"""
    particles = registry['particles']
    for fx in ('fx.persona.register', 'fx.persona.deregister', 'fx.persona.sync'):
        assert fx in particles, f"缺少粒子: {fx}"
        assert particles[fx]['dom'] == 'persona'
        assert 'ai_world' in particles[fx]['tags']


def test_registry_persona_schema(registry):
    """測試人格 Schema 定義"""
    schema = registry['persona_schema']
    for field in ('id', 'name', 'type', 'origin_email', 'dimension', 'state'):
        assert field in schema['required_fields']
