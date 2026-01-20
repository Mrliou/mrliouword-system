# MrLiouWord Intelligent Repository Sync Guide

> 基於邏輯架構原理的全域智能同步系統
> 
> 哲學：**怎麼過去，就怎麼回來**

## 📚 目錄

1. [系統概述](#系統概述)
2. [快速開始](#快速開始)
3. [配置說明](#配置說明)
4. [架構原理](#架構原理)
5. [API 參考](#api-參考)
6. [範例](#範例)
7. [常見問題](#常見問題)

---

## 系統概述

### 為什麼需要邏輯架構感知同步？

傳統的檔案同步工具只是**盲目複製**，無法理解代碼的**語意和邏輯**。

MrLiouWord 智能同步系統實現了：

```
傳統同步：檔案 A → 複製 → 檔案 A'
             ↓
        只看表面，不懂內涵

智能同步：代碼 → 邏輯架構提取 → 粒子化記憶 → 語意去重 → 完整性驗證
             ↓            ↓            ↓           ↓
         理解原理      記憶形式      避免重複    可驗證還原
```

### 核心特性

#### 🧬 邏輯架構提取

不只看代碼**長什麼樣子**，而是理解它**在做什麼**：

- **核心概念**：提取函數名、類名、重要變數
- **因果關係**：識別 if-then、try-catch 等邏輯
- **推理鏈**：追蹤函數調用順序和數據流
- **架構模式**：識別注意力機制、記憶系統、粒子引擎等高層模式

#### 🌀 粒子化記憶系統

將代碼片段轉換為**可驗證的記憶粒子**：

```python
代碼片段 → CodeParticle {
    simhash: "a1b2c3..."     # SimHash64 語意指紋
    merkle: "d4e5f6..."      # Merkle 驗證雜湊
    layer: "L2"              # 七層記憶（L1-L7）
    patterns: ["attention"]  # 邏輯模式標籤
    importance: 0.85         # 重要性分數
}
```

**七層記憶架構**：

| 層級 | 頻率 (Hz) | 存儲內容 | 範例 |
|------|-----------|----------|------|
| L1 | 7.83 | 原子粒子 | 常量、基本資料 |
| L2 | 12.67 | 原型模組 | 函數、類定義 |
| L3 | 12.94 | 封裝層 | Package、模組 |
| L4 | 20.94 | 拓撲跳點 | 配置檔、拓撲 |
| L5 | 33.88 | 人格策略 | 人格檔、策略 |
| L6 | 54.82 | 系統映像 | Docker、映像 |
| L7 | 88.71 | 語意記憶 | 文檔、語意網格 |

基於 **Schumann 共振 (7.83Hz)** 和 **黃金比例 (φ)** 的頻率系統。

#### 🎯 注意力機制

使用**多頭注意力**篩選重要粒子：

- **向量相似度**：計算粒子間的語意相似度
- **頻率共振**：同層級粒子共振度更高
- **重要性排序**：根據被注意程度排序
- **關鍵時刻識別**：找出高注意力的核心代碼

#### ✅ 完整性保證

- **SimHash64 去重**：Hamming 距離 ≤ 3 視為重複
- **Merkle Chain 驗證**：每個粒子連結到前一狀態
- **可還原性**：怎麼過去，就怎麼回來

---

## 快速開始

### 環境要求

- Python 3.11+
- Git
- 依賴：`pyyaml`, `numpy`

### 安裝

```bash
# 克隆倉庫
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system

# 安裝依賴
pip install pyyaml numpy
```

### 基本使用

#### 1. 配置檔案

編輯 `intelligent_sync.yaml`：

```yaml
settings:
  scan_mode: "global"
  sync_strategy: "logical_pattern"
  
  pattern_matching:
    enabled: true
    patterns:
      - "attention_mechanism"
      - "memory_system"

repositories:
  - name: "my-repo"
    url: "https://github.com/user/repo.git"
    branch: "main"
    enabled: true
    
    logical_patterns:
      - pattern: "attention_mechanism"
        description: "注意力機制"
        target_layer: "L2"
```

#### 2. 驗證配置

```bash
python scripts/sync_config_validator.py intelligent_sync.yaml
```

#### 3. 執行同步

```bash
# 同步所有倉庫
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml

# 同步特定倉庫
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml --repo my-repo

# 同步特定模式
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml --pattern attention_mechanism
```

#### 4. 查看統計

```bash
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml --stats
```

---

## 配置說明

### settings 區塊

#### scan_mode

- `global`: 全域掃描整個倉庫
- `targeted`: 只掃描指定檔案

#### sync_strategy

- `logical_pattern`: 基於邏輯模式匹配
- `file_based`: 傳統檔案匹配

#### pattern_matching

```yaml
pattern_matching:
  enabled: true
  patterns:
    - "attention_mechanism"      # 注意力機制
    - "memory_system"            # 記憶系統
    - "particle_engine"          # 粒子引擎
    - "frequency_resonance"      # 頻率共振
    - "merkle_chain"             # Merkle 鏈
    - "logical_reasoning"        # 邏輯推理
```

#### particle_memory

```yaml
particle_memory:
  enabled: true
  storage_path: "./particle_memory"
  simhash_threshold: 3  # Hamming 距離（0-64）
  layer_mapping:
    concepts: "L1"      # 概念 → L1
    patterns: "L2"      # 模式 → L2
    functions: "L3"     # 函數 → L3
    reasoning: "L4"     # 推理 → L4
```

#### attention

```yaml
attention:
  enabled: true
  dimension: 64                # 向量維度
  num_heads: 8                 # 注意力頭數
  similarity_threshold: 0.75   # 相似度閾值
  use_frequency_resonance: true
```

### repositories 區塊

```yaml
repositories:
  - name: "倉庫名稱"
    url: "https://github.com/user/repo.git"
    branch: "main"
    enabled: true
    
    logical_patterns:
      - pattern: "模式名稱"
        description: "模式描述"
        target_layer: "目標層級（L1-L7）"
```

---

## 架構原理

### 系統流程圖

```
┌─────────────┐
│ 遠端倉庫    │
└──────┬──────┘
       │ git clone
       ↓
┌─────────────────────┐
│ 全域掃描            │
│ - Python (.py)      │
│ - TypeScript (.ts)  │
│ - JavaScript (.js)  │
│ - Shell (.sh)       │
│ - Markdown (.md)    │
└──────┬──────────────┘
       │ LogicalStructureExtractor
       ↓
┌─────────────────────┐
│ 邏輯架構            │
│ - concepts: [...]   │
│ - patterns: {...}   │
│ - relationships     │
│ - reasoning_chains  │
└──────┬──────────────┘
       │ pattern matching
       ↓
┌─────────────────────┐
│ 本地架構匹配        │
│ similarity >= 0.5   │
└──────┬──────────────┘
       │ particlize
       ↓
┌─────────────────────┐
│ 粒子列表            │
│ [Particle1, ...]    │
└──────┬──────────────┘
       │ SimHash64 dedupe
       ↓
┌─────────────────────┐
│ 唯一粒子            │
│ Hamming dist <= 3   │
└──────┬──────────────┘
       │ AttentionFilter
       ↓
┌─────────────────────┐
│ 高重要性粒子        │
│ importance >= 0.75  │
└──────┬──────────────┘
       │ store + Merkle commit
       ↓
┌─────────────────────┐
│ 粒子記憶            │
│ L1/ L2/ ... L7/     │
│ + Merkle Chain      │
└─────────────────────┘
```

### 核心類架構

#### LogicalStructureExtractor

```python
class LogicalStructureExtractor:
    """邏輯架構提取器"""
    
    def extract_from_code(code: str, language: str) -> Dict:
        """
        提取代碼邏輯架構
        
        Returns:
        {
            'concepts': ['Attention', 'Query', ...],
            'patterns': {
                'attention_mechanism': ['attention', 'query', 'key']
            },
            'relationships': [...],
            'reasoning_chains': [...],
            'functions': [...],
            'imports': [...],
            'keywords': {...},
            'complexity': 0.65
        }
        """
```

支援語言：
- Python (AST 解析)
- TypeScript/JavaScript (正則表達式)
- Shell (函數提取)
- Markdown (標題和代碼塊)

#### ParticleMemoryManager

```python
class ParticleMemoryManager:
    """粒子化記憶管理器"""
    
    def particlize_code(...) -> CodeParticle:
        """代碼 → 粒子"""
    
    def deduplicate(particles: List) -> Tuple[unique, duplicates]:
        """SimHash 去重"""
    
    def store_particle(particle: CodeParticle) -> bool:
        """存儲到層級目錄 + Merkle 提交"""
    
    def query_by_pattern(pattern: str) -> List[CodeParticle]:
        """按模式查詢"""
    
    def find_similar(content: str) -> List[Tuple[Particle, distance]]:
        """找相似粒子"""
    
    def verify_integrity() -> Tuple[bool, errors]:
        """驗證 Merkle 鏈"""
```

#### AttentionBasedFilter

```python
class AttentionBasedFilter:
    """注意力過濾器"""
    
    def compute_attention(particles: List) -> Dict:
        """計算粒子間注意力權重"""
    
    def filter_by_similarity(particles, query) -> List:
        """相似度過濾"""
    
    def rank_by_importance(particles) -> List:
        """重要性排序"""
    
    def _frequency_resonance(layer1, layer2) -> float:
        """頻率共振匹配"""
```

---

## API 參考

### 命令行介面

#### intelligent_repo_sync.py

```bash
python scripts/intelligent_repo_sync.py [OPTIONS]

選項:
  --config PATH       配置檔案路徑 (預設: intelligent_sync.yaml)
  --repo NAME         只同步指定倉庫
  --pattern PATTERN   只同步指定模式
  --stats             只顯示統計資訊

範例:
  # 同步所有
  python scripts/intelligent_repo_sync.py
  
  # 同步 attention_mechanism 模式
  python scripts/intelligent_repo_sync.py --pattern attention_mechanism
```

#### sync_config_validator.py

```bash
python scripts/sync_config_validator.py [CONFIG] [OPTIONS]

選項:
  --strict            嚴格模式（警告也視為錯誤）

範例:
  python scripts/sync_config_validator.py intelligent_sync.yaml
```

### Python API

#### 提取邏輯架構

```python
from integrations.github.logical_extractor import LogicalStructureExtractor

extractor = LogicalStructureExtractor()
structure = extractor.extract_from_code(code, 'python')

print(structure['patterns'])  # 識別的模式
print(structure['concepts'])  # 核心概念
```

#### 粒子化記憶

```python
from integrations.github.particle_memory import ParticleMemoryManager

manager = ParticleMemoryManager('./particle_memory')

# 創建粒子
particle = manager.particlize_code(
    content=code,
    language='python',
    file_path='attention.py',
    patterns=['attention_mechanism']
)

# 存儲
manager.store_particle(particle)

# 查詢
results = manager.query_by_pattern('attention_mechanism')
```

#### 注意力過濾

```python
from integrations.github.attention_filter import AttentionBasedFilter

filter = AttentionBasedFilter(dimension=64, num_heads=8)

# 計算注意力
attention_map = filter.compute_attention(particles)

# 重要性排序
ranked = filter.rank_by_importance(particles, attention_map)
```

---

## 範例

### 範例 1：同步 flow-tasks 的注意力機制

**配置**：

```yaml
repositories:
  - name: "flow-tasks"
    url: "https://github.com/dofaromg/flow-tasks.git"
    branch: "main"
    enabled: true
    
    logical_patterns:
      - pattern: "attention_mechanism"
        target_layer: "L2"
```

**執行**：

```bash
python scripts/intelligent_repo_sync.py --pattern attention_mechanism
```

**結果**：

```
🔍 開始掃描倉庫: https://github.com/dofaromg/flow-tasks.git
📥 克隆倉庫...
✅ 掃描完成: 142 個檔案

🔗 開始匹配邏輯模式...
  找到 8 個包含 attention_mechanism 的遠端結構
✅ 匹配完成: 8 個匹配

💾 開始同步到粒子記憶...
  去重: 6 唯一, 2 重複
  注意力過濾: 保留 5, 過濾 1
✅ 同步完成: 5 個粒子

📊 同步統計
  新增粒子: 5
  總粒子數: 23
  L2: 5
  Merkle 完整性: ✅
```

### 範例 2：查詢相似代碼

```python
from integrations.github.particle_memory import ParticleMemoryManager

manager = ParticleMemoryManager('./particle_memory')

# 查詢內容
query = """
def attention(query, key, value):
    scores = query @ key.T
    return softmax(scores) @ value
"""

# 找相似粒子
similar = manager.find_similar(query, threshold=3, limit=5)

for particle, distance in similar:
    print(f"距離: {distance}")
    print(f"檔案: {particle.file_path}")
    print(f"模式: {particle.patterns}")
    print()
```

### 範例 3：自定義邏輯模式

```yaml
# 添加自定義模式
settings:
  pattern_matching:
    patterns:
      - "custom_crypto_algorithm"  # 自定義模式

repositories:
  - name: "crypto-lib"
    logical_patterns:
      - pattern: "custom_crypto_algorithm"
        description: "加密演算法實現"
        target_layer: "L3"
```

---

## 常見問題

### Q: 與傳統 git submodule 的差別？

**A**: 

| 特性 | git submodule | Intelligent Sync |
|------|---------------|------------------|
| 同步單位 | 整個倉庫 | 邏輯架構片段 |
| 去重 | 無 | SimHash64 語意去重 |
| 完整性 | Git SHA | Merkle Chain |
| 理解能力 | 無 | 邏輯架構感知 |
| 粒度 | 倉庫級 | 函數/類級 |

### Q: SimHash 閾值如何設定？

**A**: 

- `threshold = 0`: 完全相同
- `threshold = 1-3`: 幾乎相同（推薦）
- `threshold = 4-8`: 相似
- `threshold > 8`: 太寬鬆

### Q: 如何處理私有倉庫？

**A**:

GitHub Actions 中設定 `GITHUB_TOKEN`:

```yaml
env:
  GITHUB_TOKEN: ${{ secrets.PAT_TOKEN }}
```

或使用 SSH:

```yaml
url: "git@github.com:user/private-repo.git"
```

### Q: 記憶粒子會佔用多少空間？

**A**:

每個粒子約 1-5KB（包含 JSON 元資料）。
1000 個粒子 ≈ 1-5MB。

可以定期清理舊粒子或低重要性粒子。

### Q: Merkle 鏈驗證失敗怎麼辦？

**A**:

```python
from integrations.github.particle_memory import ParticleMemoryManager

manager = ParticleMemoryManager('./particle_memory')
valid, errors = manager.verify_integrity()

if not valid:
    for error in errors:
        print(error)
    
    # 可選：回滾到上一個有效狀態
    # manager.merkle_chain.rollback(target_merkle)
```

---

## 延伸閱讀

- [SYSTEM_INDEX.md](../SYSTEM_INDEX.md) - 七層記憶架構
- [core/simhash64.py](../core/simhash64.py) - SimHash 實現
- [core/merkle.py](../core/merkle.py) - Merkle Chain 實現
- [index.ts](../index.ts) - ParticleAttention 引擎

---

> **哲學**：這個系統不只是「複製檔案」，而是：
> - 理解**邏輯架構原理**
> - 以**粒子形式記憶**
> - 通過**注意力機制**識別重要性
> - 保證**完整性可驗證**（Merkle）
> - 實現**語意去重**（SimHash）
> 
> 讓系統真正「理解」它在同步什麼，而不是盲目複製。
> 
> **怎麼過去，就怎麼回來** 🌀
