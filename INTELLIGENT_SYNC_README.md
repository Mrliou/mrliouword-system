# MrLiouWord Intelligent Synchronization System

> **Philosophy:** 怎麼過去，就怎麼回來 (What goes around, comes around)

## 🎯 Overview

A comprehensive GitHub Global Logical Architecture Synchronization System that discovers, extracts, analyzes, and stores logical patterns from open-source code.

## ✨ Features

- 🔍 **GitHub Search**: Global code search with multi-language support
- 🧠 **Logical Extraction**: Pattern & concept detection (attention, memory, merkle, etc.)
- 🎯 **Attention Filter**: Frequency-based embeddings with Schumann resonance (7.83Hz)
- ✅ **7 Particle Tests**: Comprehensive verification suite
- 🏷️ **Auto-Naming**: Intelligent particle name generation
- 💾 **Memory Storage**: SimHash deduplication + Merkle chain integrity
- 📊 **Sync Reports**: Detailed synchronization analytics

## 🚀 Quick Start

```bash
# Install dependencies
pip install requests pyyaml numpy

# Set GitHub token
export GITHUB_TOKEN="your_github_token"

# Run sync for a pattern
python scripts/intelligent_repo_sync.py --pattern "attention mechanism" --limit 10

# Run all patterns
python scripts/intelligent_repo_sync.py --all

# Run particle tests
python integrations/particle/test_recorder.py

# Run test suite
python -m pytest tests/test_intelligent_sync.py -v
```

## 📁 Project Structure

```
mrliouword-system/
├── core/
│   ├── simhash64.py          # SimHash64 fingerprinting
│   └── merkle.py             # Merkle chain verification
├── integrations/
│   ├── github/
│   │   └── logical_extractor.py    # Pattern extraction
│   ├── webgpu/
│   │   └── attention_filter.py     # Attention similarity
│   └── particle/
│       ├── test_recorder.py         # 7 particle tests ⭐
│       ├── naming_engine.py         # Auto-naming ⭐
│       └── memory_storage.py        # Particle storage
├── scripts/
│   ├── global_github_search.py      # GitHub API client
│   └── intelligent_repo_sync.py     # Main orchestrator
├── tests/
│   └── test_intelligent_sync.py     # Test suite
├── docs/
│   └── INTELLIGENT_SYNC_GUIDE.md    # Full documentation
├── .github/workflows/
│   └── intelligent-sync.yml         # GitHub Actions
└── intelligent_sync.yaml             # Configuration
```

## 🔬 Components

### 1. GitHub Search Engine
Searches GitHub globally using Code Search API with semantic query building.

### 2. Logical Architecture Extractor
Detects patterns: attention, memory, merkle, particle, flow, layer architectures.

### 3. Attention Filter
WebGPU-inspired attention mechanism with frequency-based embeddings.

### 4. Particle Test Recorder ⭐
Runs 7 critical tests:
1. Write test
2. Read test
3. SimHash collision test
4. Merkle integrity test
5. Layer retrieval test
6. Tag search test
7. Frequency resonance test

### 5. Particle Naming Engine ⭐
Auto-generates particle names based on logical understanding:
- `fx.pattern.attention` for attention patterns
- `fx.pattern.memory` for memory systems
- `fx.pattern.chain` for merkle/blockchain
- Auto-versioning on conflicts

### 6. Particle Memory Storage
Stores particles with:
- SimHash64 deduplication (Hamming ≤ 3)
- Merkle chain integrity
- Layer assignment (L1-L7)
- Frequency calculation (Schumann × Phi^n)

### 7. Sync Orchestrator
Coordinates all components in a complete sync flow.

## 📋 Configuration

Edit `intelligent_sync.yaml`:

```yaml
github:
  min_stars: 10
  languages: [Python, TypeScript, Go, Rust]
  max_results: 30

patterns:
  - "attention mechanism"
  - "merkle tree"
  - "memory system"

particle_memory:
  simhash_threshold: 3
  layer_assignment:
    L1: 0.9    # ≥0.9 → L1 (highest quality)
    L2: 0.75
    L3: 0.6
    L4: 0.4

testing:
  enabled: true
  run_on_sync: true

naming:
  auto_version: true
```

## 🔄 GitHub Actions

Runs automatically every Monday at 00:00 UTC. Manual trigger available:

1. Go to **Actions** → **Intelligent GitHub Sync**
2. Click **Run workflow**
3. Enter pattern (optional) and limit
4. View sync reports in artifacts

## 📊 Example Usage

### Search & Extract
```python
from scripts.global_github_search import GitHubSearchEngine
from integrations.github.logical_extractor import LogicalExtractor

# Search GitHub
engine = GitHubSearchEngine()
snippets = engine.search_code("attention mechanism", limit=10)

# Extract logical structure
extractor = LogicalExtractor()
for snippet in snippets:
    structure = extractor.extract(snippet.code, snippet.language)
    print(f"Patterns: {structure.patterns}")
    print(f"Formula: {structure.formula}")
```

### Store Particles
```python
from integrations.particle.memory_storage import ParticleMemoryStorage

storage = ParticleMemoryStorage()
particle, is_new = storage.store(
    name='fx.pattern.attention.transformer',
    particle_type='fx.pattern.attention',
    content='attention implementation...',
    source_info={'repo': 'user/transformer', 'url': '...'},
    tags=['attention', 'neural']
)

print(f"Particle: {particle.name}, Layer: {particle.layer}")
```

### Run Tests
```python
import asyncio
from integrations.particle.test_recorder import ParticleTestRecorder

async def test():
    recorder = ParticleTestRecorder()
    report = await recorder.run_all_tests()
    print(f"Tests: {report.passed}/{report.total_tests} passed")

asyncio.run(test())
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/test_intelligent_sync.py -v

# Run specific test
python -m pytest tests/test_intelligent_sync.py::TestParticleTestRecorder -v

# Run particle tests
python integrations/particle/test_recorder.py
```

## 📖 Documentation

Full documentation: [docs/INTELLIGENT_SYNC_GUIDE.md](docs/INTELLIGENT_SYNC_GUIDE.md)

Topics covered:
- System architecture
- API reference
- Configuration guide
- Use cases
- FAQ

## 🔐 Philosophy

**怎麼過去，就怎麼回來** (What goes around, comes around)

- Understand logical principles, not just code
- 7-item test verification for completeness
- Dynamic naming evolution
- Particle-based memory with SimHash dedup + Merkle verification
- Complete traceability

## 📈 Sync Flow

```
GitHub Search → Logical Extract → Attention Filter → Particle Tests
                                                            ↓
Sync Report ← Memory Storage ← Naming Engine ← [Tests Pass?]
```

## 🛠️ Requirements

- Python 3.10+
- `requests` - GitHub API
- `pyyaml` - Configuration
- `numpy` - Vector operations
- `pytest` - Testing (optional)

## 📝 License

MIT License - See LICENSE file

## 👤 Author

**MR.liou**

*Understanding logic, not just code.*

---

**Built with ❤️ for the MrLiouWord System**
