# 🌀 Intelligent Repository Sync

> **哲學：怎麼過去，就怎麼回來**
>
> 基於邏輯架構原理的全域智能同步系統

## 快速開始

```bash
# 1. 安裝依賴
pip install pyyaml numpy

# 2. 驗證配置
python scripts/sync_config_validator.py intelligent_sync.yaml

# 3. 執行同步
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml

# 4. 查看統計
python scripts/intelligent_repo_sync.py --config intelligent_sync.yaml --stats
```

## 核心特性

### 🧬 邏輯架構提取
不只看代碼**長什麼樣子**，而是理解它**在做什麼**

- 提取核心概念、因果關係、推理鏈
- 識別架構模式：attention_mechanism, memory_system, particle_engine...
- 支援 Python, TypeScript, JavaScript, Shell, Markdown

### 🌀 粒子化記憶
將代碼轉換為**可驗證的記憶粒子**

- SimHash64 語意指紋去重
- Merkle Chain 完整性驗證
- 七層記憶存儲 (L1-L7)
- 基於 Schumann 共振 (7.83Hz) 和黃金比例 (φ)

### 🎯 注意力機制
使用**多頭注意力**篩選重要粒子

- 向量相似度計算
- 頻率共振匹配
- 重要性排序

## 系統架構

```
Repository → 全域掃描 → 邏輯架構提取 → 模式匹配 → 粒子化
    ↓           ↓            ↓              ↓           ↓
  Clone      Python/TS/   Concepts      Similarity  SimHash64
             JS/Shell     Patterns       >= 0.5     Fingerprint
                                                         ↓
                                                    去重 (≤3)
                                                         ↓
                                                    注意力過濾
                                                         ↓
                                                   存儲 L1-L7
                                                         ↓
                                                   Merkle 驗證
```

## 配置範例

```yaml
settings:
  scan_mode: "global"
  sync_strategy: "logical_pattern"
  
  pattern_matching:
    enabled: true
    patterns:
      - "attention_mechanism"
      - "memory_system"
      - "particle_engine"

repositories:
  - name: "flow-tasks"
    url: "https://github.com/dofaromg/flow-tasks.git"
    enabled: true
    
    logical_patterns:
      - pattern: "attention_mechanism"
        target_layer: "L2"
```

## 使用範例

### 同步特定模式
```bash
python scripts/intelligent_repo_sync.py --pattern attention_mechanism
```

### 同步特定倉庫
```bash
python scripts/intelligent_repo_sync.py --repo flow-tasks
```

### 查詢相似粒子
```python
from integrations.github.particle_memory import ParticleMemoryManager

manager = ParticleMemoryManager('./particle_memory')
similar = manager.find_similar(query_code, threshold=3)
```

## GitHub Actions

自動化同步工作流程：
- 每週一自動執行
- 支援手動觸發
- 可指定模式或倉庫過濾
- 自動提交粒子記憶
- Merkle 鏈完整性驗證

## 文檔

詳細文檔請參考：
- [完整使用指南](docs/INTELLIGENT_SYNC_GUIDE.md)
- [系統索引](SYSTEM_INDEX.md)
- [配置範本](intelligent_sync.yaml)

## 測試

```bash
python tests/test_intelligent_sync.py
```

測試覆蓋：
- 邏輯結構提取 ✅
- 粒子記憶管理 ✅
- 注意力過濾 ✅
- Merkle 鏈驗證 ✅
- 跨語言支持 ✅

## 成功標準

1. ✅ 自動識別並同步「注意力機制」相關代碼
2. ✅ 同步內容以粒子形式存儲，包含 SimHash 和 Merkle 驗證
3. ✅ 支持 `--pattern attention_mechanism` 語意查詢
4. ✅ 去重機制正常工作 (SimHash Hamming 距離 ≤ 3)
5. ✅ GitHub Actions 自動化正常運行
6. ✅ 文檔清晰完整

## 安全性

- ✅ CodeQL 掃描通過 (0 漏洞)
- ✅ GitHub Actions 權限正確配置
- ✅ 錯誤處理完善
- ✅ Merkle 防碰撞保護

## 授權

本專案遵循 MrLiouWord System 授權協議

---

> 讓系統真正「理解」它在同步什麼，而不是盲目複製
> 
> **怎麼過去，就怎麼回來** 🌀
