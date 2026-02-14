# MrLiouWord Particle Dictionary - Fluin Mapping System

## 🌐 概述 (Overview)

本文件夾包含MrLiouWord粒子系統的核心字典文件，實現Fluin反推映射生成系統。

## 📂 文件結構 (File Structure)

```
docs/particle-dictionary/
├── README.md                          # 本文件
├── fluin-mapping-system.md           # Fluin映射系統文檔
└── particle-integration-guide.md     # 粒子整合指南
```

## 🎯 核心概念 (Core Concepts)

### 粒子層級 (Particle Layers)

MrLiouWord系統定義了8個粒子層級：

- **L0 (ROOT)**: 根層 - 最基礎的粒子
- **L1 (SEED)**: 種子層 - 基本組件
- **L2 (PARTICLE)**: 粒子層 - 功能單元
- **L3 (LAW)**: 法則層 - 運作規則
- **L4 (WORLD)**: 世界層 - 環境系統
- **L5 (MIRROR)**: 鏡像層 - 映射機制
- **L6 (REFLECT)**: 反射層 - 回饋系統
- **L7 (LOOP)**: 迴圈層 - 閉環機制

### 閉環法則 (Closure Law)

**怎麼過去，就怎麼回來** - How it goes out, is how it comes back

這是MrLiouWord系統的核心原則，確保所有操作都遵循閉環一致性。

## 📊 粒子屬性 (Particle Attributes)

每個粒子包含以下屬性：

```json
{
  "fx": "fx.domain.action",      // 功能標識符
  "hv": "中文名稱",                // 人類可讀名稱
  "av": "動作描述",                // 動作說明
  "dom": "domain",               // 所屬領域
  "act": "action",               // 執行動作
  "nrg": 0.8,                    // 能量等級 (0-1)
  "links": ["fx.other"],         // 關聯粒子
  "tags": ["tag1", "tag2"]       // 標籤
}
```

## 🔗 同步機制 (Sync Mechanism)

本目錄中的文件會自動同步到以下倉庫：

1. **dofaromg/mrliouword-system** (主倉庫)
2. **dofaromg/flow-tasks** (任務流)
3. **dofaromg/flow-tasks-01** (任務流-01)

通過 `.mrliou/` 閉環同步系統維護一致性。

## 📖 參考資料 (References)

- [前粒子整合流程](../architecture/pre-particle.md)
- [粒子字典 JSON](../../core/particles/particle_dict.json)
- [閉環同步配置](../../.mrliou/sync.config.json)

---

**origin_signature**: MrLiouWord  
**version**: v1.0.0  
**principle**: 怎麼過去，就怎麼回來 ✨
