# Intelligent Synchronization Guide

> **Philosophy:** 怎麼過去，就怎麼回來 (What goes around, comes around)

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Quick Start](#quick-start)
3. [Configuration Guide](#configuration-guide)
4. [Architecture Details](#architecture-details)
5. [API Reference](#api-reference)
6. [Use Cases](#use-cases)
7. [FAQ](#faq)

---

## System Overview

The **MrLiouWord Intelligent Synchronization System** is a comprehensive GitHub Global Logical Architecture Synchronization platform that:

- 🔍 **Searches** GitHub globally for logical architecture patterns
- 🧠 **Extracts** logical concepts, patterns, and relationships from code
- 🎯 **Filters** using attention-based similarity (inspired by WebGPU)
- ✅ **Tests** particle system with 7 critical verification tests
- 🏷️ **Names** particles automatically based on logical understanding
- 💾 **Stores** as particles with SimHash deduplication and Merkle verification
- 📊 **Reports** comprehensive synchronization results

### Key Features

- **Multi-language support**: Python, TypeScript, Go, Rust, Java, JavaScript
- **Pattern detection**: Attention, Memory, Merkle, Particle, Flow, Layer architectures
- **Deduplication**: SimHash64 with Hamming distance ≤ 3
- **Integrity verification**: Merkle chain for tamper-proof memory
- **Layer assignment**: L1-L7 based on similarity scores
- **Frequency resonance**: Schumann (7.83Hz) × Phi-based frequencies

---

## Quick Start

### Prerequisites

```bash
# Python 3.10+
python --version

# Required packages
pip install requests pyyaml numpy
```

### Basic Usage

```bash
# 1. Set GitHub token
export GITHUB_TOKEN="your_github_token"

# 2. Run sync for a specific pattern
python scripts/intelligent_repo_sync.py --pattern "attention mechanism" --limit 10

# 3. Run sync for all patterns in config
python scripts/intelligent_repo_sync.py --all

# 4. Run particle tests
python integrations/particle/test_recorder.py
```

### GitHub Actions

The system runs automatically every Monday at 00:00 UTC via GitHub Actions. You can also trigger manually:

1. Go to **Actions** → **Intelligent GitHub Sync**
2. Click **Run workflow**
3. Enter optional pattern and limit
4. Click **Run workflow**

---

## Configuration Guide

Edit `intelligent_sync.yaml` to customize behavior:

```yaml
github:
  min_stars: 10          # Minimum repository stars
  languages:             # Languages to search
    - Python
    - TypeScript
  max_results: 30        # Max results per pattern

patterns:                # Patterns to search
  - "attention mechanism"
  - "merkle tree"

particle_memory:
  simhash_threshold: 3   # Hamming distance for dedup
  layer_assignment:      # Similarity → Layer mapping
    L1: 0.9             # ≥0.9 → L1 (highest quality)
    L2: 0.75
    L3: 0.6
    L4: 0.4

testing:
  enabled: true          # Run 7 particle tests
  run_on_sync: true

naming:
  auto_version: true     # Handle conflicts with versioning
```

### Layer Assignment

Particles are assigned to layers based on similarity scores:

| Similarity | Layer | Frequency (Hz) | Quality |
|-----------|-------|----------------|---------|
| ≥ 0.9     | L1    | 7.83           | Highest |
| ≥ 0.75    | L2    | 12.67          | High    |
| ≥ 0.6     | L3    | 20.50          | Medium  |
| ≥ 0.4     | L4    | 33.17          | Low     |
| < 0.4     | L5    | 53.68          | Lowest  |

Frequencies are calculated as: **SCHUMANN (7.83 Hz) × PHI^n**

---

## Architecture Details

### System Flow

```
┌─────────────────┐
│ GitHub Search   │ ──► Search code globally
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Logical Extract │ ──► Extract patterns, concepts, reasoning
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Attention Filter│ ──► Compute similarity matrix
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Particle Tests  │ ──► Run 7 verification tests
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Naming Engine   │ ──► Auto-generate particle names
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Memory Storage  │ ──► Store with dedup & Merkle
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Sync Report     │ ──► Generate comprehensive report
└─────────────────┘
```

### Components

#### 1. GitHub Search Engine
**File:** `scripts/global_github_search.py`

- GitHub Code Search API integration
- Semantic query builder
- Multi-language support
- Rate limit handling

#### 2. Logical Architecture Extractor
**File:** `integrations/github/logical_extractor.py`

Detects patterns:
- **Attention**: query/key/value, softmax, multi-head
- **Memory**: cache, storage, recall, commit
- **Merkle**: hash tree, root hash, verification
- **Particle**: quantum, resonance, frequency
- **Flow**: pipeline, stream, orchestration
- **Layer**: hierarchy, stack, stratification

#### 3. Attention Filter
**File:** `integrations/webgpu/attention_filter.py`

- Frequency-based embeddings (Schumann 7.83Hz)
- Multi-head attention similarity
- Cosine similarity matrix
- Top-k selection with softmax weights

#### 4. Particle Test Recorder ⭐
**File:** `integrations/particle/test_recorder.py`

Implements 7 critical tests:

1. **Write Test**: Verify particle can write to KV
2. **Read Test**: Verify particle can be read
3. **SimHash Collision**: Check similar particles (Hamming ≤ 3)
4. **Merkle Integrity**: Verify Merkle chain
5. **Layer Retrieval**: Verify layer-based (L1-L7) retrieval
6. **Tag Search**: Verify tag-based search
7. **Frequency Resonance**: Find frequency-similar particles (±0.5Hz)

Test results are stored as particles (`fx.meta.test`) in L7.

#### 5. Particle Naming Engine ⭐
**File:** `integrations/particle/naming_engine.py`

Auto-generates names based on:

| Pattern/Concept | Particle Type |
|----------------|---------------|
| attention      | `fx.pattern.attention` |
| memory         | `fx.pattern.memory` |
| merkle/chain   | `fx.pattern.chain` |
| particle       | `fx.pattern.particle` |
| flow           | `fx.flow.pipeline` |
| layer          | `fx.pattern.hierarchical` |
| distributed    | `fx.system.distributed` |
| neural         | `fx.ai.neural` |
| *default*      | `fx.logic.{reasoning_type}` |

Handles conflicts with versioning (e.g., `name_v2`, `name_v3`).

#### 6. Particle Memory Storage
**File:** `integrations/particle/memory_storage.py`

- **SimHash64 deduplication**: Hamming ≤ 3
- **Source merging**: Combines similar particles
- **Merkle chain**: Tamper-proof verification
- **Layer assignment**: Based on similarity score
- **Frequency calculation**: Schumann × Phi^n

#### 7. Sync Orchestrator
**File:** `scripts/intelligent_repo_sync.py`

Main controller coordinating all components.

---

## API Reference

### GitHub Search Engine

```python
from scripts.global_github_search import GitHubSearchEngine

engine = GitHubSearchEngine(token="github_token")

# Search code
snippets = engine.search_code(
    pattern="attention mechanism",
    languages=["Python", "TypeScript"],
    limit=30,
    min_stars=10
)

# Each snippet has:
# - repo: full repository name
# - path: file path
# - language: programming language
# - code: source code
# - url: GitHub URL
# - score: search score
```

### Logical Extractor

```python
from integrations.github.logical_structure_extractor import LogicalStructureExtractor

extractor = LogicalStructureExtractor()

structure = extractor.extract_from_code(code="...", language="Python")

# structure['patterns']: ['attention', 'memory']
# structure['concepts']: ['vector', 'neural']
# structure['relationships']: {'classes': [...], 'functions': [...]}
# structure['reasoning_chains']: ['query -> key -> value -> softmax']
# structure['formula']: 'Attention(Q,K,V) = softmax(QK^T/√d)V'
# structure['confidence']: 0.85
```

### Attention Filter

```python
from integrations.webgpu.attention_filter import AttentionFilter

filter = AttentionFilter(embedding_dim=128, num_heads=4)

# Compute embedding
embedding = filter.compute_embedding("attention mechanism", base_freq=7.83)

# Filter by attention
scores = filter.filter_by_attention(
    texts=["text1", "text2", "text3"],
    threshold=0.5
)

# Each score has:
# - snippet_a: index of first text
# - snippet_b: index of second text
# - similarity: cosine similarity
# - layer: assigned layer (L1-L5)
# - frequency: frequency in Hz
```

### Particle Test Recorder

```python
from integrations.particle.test_recorder import ParticleTestRecorder

recorder = ParticleTestRecorder('./test_particles')

# Run all 7 tests
import asyncio
report = asyncio.run(recorder.run_all_tests())

# report.total_tests: 7
# report.passed: number passed
# report.failed: number failed
# report.tests: list of test results
```

### Naming Engine

```python
from integrations.particle.naming_engine import ParticleNamingEngine

engine = ParticleNamingEngine('./naming_history')

decision = engine.generate_name(
    patterns=['attention', 'memory'],
    concepts=['vector', 'neural'],
    reasoning_chains=['query -> key -> value'],
    source_info={'repo': 'user/repo', 'language': 'Python'}
)

# decision.particle_name: 'fx.pattern.attention.attention_vector_repo'
# decision.particle_type: 'fx.pattern.attention'
# decision.reasoning: 'Primary pattern 'attention' detected'
# decision.confidence: 0.9
# decision.version: 1
```

### Memory Storage

```python
from integrations.particle.memory_storage import ParticleMemoryStorage

storage = ParticleMemoryStorage('./particle_memory')

# Store particle
particle, is_new = storage.store(
    name='fx.pattern.attention.test',
    particle_type='fx.pattern.attention',
    content='attention mechanism implementation',
    source_info={'repo': 'user/repo', 'url': 'https://...'},
    tags=['attention', 'neural'],
    metadata={'confidence': 0.85}
)

# Search particles
particles = storage.search_by_layer('L2')
particles = storage.search_by_tag('attention')
particles = storage.search_by_frequency(7.83, tolerance=0.5)

# Verify Merkle chain
valid, errors = storage.verify_merkle_chain()
```

---

## Use Cases

### 1. Learn from Open Source

Discover how top repositories implement specific patterns:

```bash
python scripts/intelligent_repo_sync.py --pattern "attention mechanism" --limit 50
```

Then explore particles:

```python
from integrations.particle.memory_storage import ParticleMemoryStorage
storage = ParticleMemoryStorage('./particle_memory')

attention_particles = storage.search_by_type('fx.pattern.attention')
for p in attention_particles:
    print(f"{p.name}: {len(p.sources)} sources")
    for source in p.sources:
        print(f"  - {source['repo']}")
```

### 2. Track Architecture Evolution

Run weekly syncs to see how patterns evolve:

```bash
# Automatic via GitHub Actions every Monday
# Manual: python scripts/intelligent_repo_sync.py --all
```

Compare naming history:

```python
from integrations.particle.naming_engine import ParticleNamingEngine
engine = ParticleNamingEngine('./naming_history')

# Get all attention patterns
attention_names = engine.get_by_type('fx.pattern.attention')
print(f"Found {len(attention_names)} attention implementations")
```

### 3. Verify System Integrity

Run particle tests before deployment:

```bash
python integrations/particle/test_recorder.py
```

Verify Merkle chain:

```python
from integrations.particle.memory_storage import ParticleMemoryStorage
storage = ParticleMemoryStorage('./particle_memory')

valid, errors = storage.verify_merkle_chain()
if not valid:
    print("Chain compromised!")
    for error in errors:
        print(f"  - {error}")
```

### 4. Discover Similar Implementations

Find repositories with similar architectures:

```python
from integrations.webgpu.attention_filter import AttentionFilter

filter = AttentionFilter()

# Get all particle contents
storage = ParticleMemoryStorage('./particle_memory')
particles = storage.search_by_type('fx.pattern.attention')

contents = [p.content for p in particles]
scores = filter.filter_by_attention(contents, threshold=0.7)

# scores shows similar implementations
```

---

## FAQ

### Q: How does SimHash deduplication work?

**A:** SimHash generates a 64-bit fingerprint from text. Similar texts have similar hashes (Hamming distance ≤ 3). When storing a particle, we check if a similar one exists (Hamming ≤ 3) and merge sources instead of creating a duplicate.

### Q: What is the Merkle chain used for?

**A:** The Merkle chain provides tamper-proof verification. Each particle has a `merkle` hash computed from `content + simhash + timestamp + prev_merkle`. This creates an immutable chain where any modification breaks verification.

### Q: Why frequency-based embeddings?

**A:** Following MrLiouWord philosophy, we use Schumann resonance (7.83Hz) as the base frequency. Embeddings modulate this frequency with character distributions, creating resonant patterns that reflect logical structure.

### Q: How are layers assigned?

**A:** Layers are assigned based on similarity scores:
- High similarity (≥0.9) → L1 (core patterns)
- Medium similarity (0.6-0.9) → L2-L3
- Low similarity (<0.6) → L4-L5 (experimental)

### Q: What happens when particle names conflict?

**A:** The naming engine auto-versions conflicts:
- First: `fx.pattern.attention.transformer`
- Second: `fx.pattern.attention.transformer_v2`
- Third: `fx.pattern.attention.transformer_v3`

### Q: Can I add custom patterns?

**A:** Yes! Edit `intelligent_sync.yaml`:

```yaml
patterns:
  - "your custom pattern"
  - "another pattern"
```

### Q: How do I export all particles?

```bash
python -c "
from integrations.particle.memory_storage import ParticleMemoryStorage
storage = ParticleMemoryStorage('./particle_memory')
storage.export_particles('particles_export.json')
"
```

### Q: What are the 7 particle tests?

1. **Write**: Can particle write to KV storage?
2. **Read**: Can particle be read back?
3. **SimHash**: Are similar particles detected (Hamming ≤ 3)?
4. **Merkle**: Is the Merkle chain valid?
5. **Layer**: Can particles be retrieved by layer (L1-L7)?
6. **Tag**: Can particles be searched by tags?
7. **Frequency**: Can particles be found by frequency resonance (±0.5Hz)?

All tests must pass for system integrity.

---

## Support

- **GitHub Issues**: [Report bugs or request features](https://github.com/your-repo/issues)
- **Documentation**: This guide
- **Philosophy**: 怎麼過去，就怎麼回來 (What goes around, comes around)

---

**Built with ❤️ by MR.liou**

*Understanding logic, not just code.*
