# MrLiouWord Container Specification
# MrLiouWord 容器規格

> **Origin Signature**: MrLiouWord  
> **Version**: 1.0.0  
> **Philosophy**: 怎麼過去，就怎麼回來

---

## 架構概述

MrLiouWord 統一容器運行時基於 L0-L7 八層架構,支援所有主流平台。

### 支援平台

- ✅ **Node.js** (JavaScript/TypeScript runtime)
- ✅ **Next.js** (React framework)
- ✅ **Unix/Linux** (POSIX systems)
- ✅ **macOS** (Darwin kernel)
- ✅ **Windows** (Win32/WSL)

### L0-L7 層級

| Layer | Name | Purpose |
|-------|------|---------|
| L0 | ROOT | Origin: MrLiouWord |
| L1 | SEED | 種子層 - dimension_seed_restore |
| L2 | PARTICLE | 粒子層 - 17 fx particles |
| L3 | LAW | 法則層 - Business logic |
| L4 | WORLD | 連接層 - External connections |
| L5 | MIRROR | 鏡像層 - Backup/redundancy |
| L6 | REFLECT | 投影層 - UI/API projection |
| L7 | LOOP | 驗證層 - Verification |

---

## 容器格式

### .flpkg (Particle Package)

```json
{
  "id": "flpkg-1234567890",
  "version": "flpkg/1.0",
  "origin_signature": "MrLiouWord",
  "layer": "L2",
  "content": {
    "particles": [
      {"word": "我", "fx": "per.fx"},
      {"word": "封存", "fx": "v.act"},
      {"word": "語場", "fx": "n.obj"}
    ],
    "metadata": {
      "created": "2026-01-23T00:00:00Z"
    }
  },
  "encrypted": false
}
```

### .fltnz (Flow Tensor Notation)

```
我⧉/fx.per.fx/ 封存⧉/fx.v.act/ 語場⧉/fx.n.obj/
```

### .pcode (Particle Code)

Binary format for compressed particle sequences.

---

## CLI 使用

### 初始化
```bash
mrliou-runtime init
```

### 載入容器
```bash
mrliou-runtime load MyApp.flpkg --layer L3
```

### 啟動元環境
```bash
mrliou-runtime spawn --cpu 4 --ram 8G
```

### 反推規則
```bash
mrliou-runtime reverse-mine \
  --trace-fs trace_fs.csv \
  --trace-ops trace_ops.csv \
  --output rules.yaml
```

---

## API 參考

詳見 `docs/API_REFERENCE.md`

---

## 架構組件

### UniversalRuntime

統一容器運行時核心，負責:
- 平台檢測 (Node.js/Next.js/Unix/Linux/macOS/Windows)
- 適配器管理
- 容器生命週期管理
- L0-L7 層級配置

### LayerManager

層級管理系統，實現 L0-L7 配置:
- L0 ROOT: Origin signature
- L1 SEED: Dimension seed loading
- L2 PARTICLE: Particle dictionary integration
- L3 LAW: Business logic rules
- L4 WORLD: External connections
- L5 MIRROR: Backup and mirroring
- L6 REFLECT: UI/API projections
- L7 LOOP: Verification and closure

### MetaEnvController

元代碼沙盒控制器，提供:
- Environment spawning
- Policy management (Guard.v1)
- Snapshot creation
- Channel mapping
- Lockdown mechanism

### TraceMiner

反推引擎，分析系統追蹤:
- 讀取 trace_fs.csv 和 trace_ops.csv
- 提取操作模式
- 生成規則和通道地圖
- 輸出 YAML 配置

---

## 平台適配器

### NodeAdapter
Node.js 運行時適配器，支援標準 Node.js 應用。

### NextAdapter
Next.js 框架適配器，支援 React/Next.js 應用。

### PosixAdapter
POSIX 系統適配器，支援 Unix/Linux/macOS。

### WindowsAdapter
Windows 平台適配器，支援 Win32 應用。

---

## 安全機制

### Guard.v1

安全護欄系統:
- Policy 應用
- Lockdown 機制
- Token 撤銷
- 快照凍結

### 加密快照

支援加密快照以保護敏感資料:
```typescript
const snapshot_id = await controller.createSnapshot(env_id, true)
```

---

## 整合現有系統

### Particle Dictionary

與 `core/particle_dict.json` 整合:
- L2 層自動載入粒子字典
- 支援 fx particles 解析
- 與現有 simhash64 和 merkle 系統相容

### Cloudflare Workers

可部署到 Cloudflare Workers:
- 使用 Next.js adapter
- 支援 edge runtime
- 與現有 particle-auth-gateway 整合

---

## 開發環境

### Dev Container

使用 `.devcontainer/devcontainer.json` 配置:
- TypeScript/Node.js 20
- Python 3.11
- Docker-in-Docker
- GitHub CLI

### 建置

```bash
npm run build:containers
```

### 測試

```bash
npm test
```

---

## 擴展性

### 自訂適配器

創建新的平台適配器:

```typescript
import { FlpkgContainer, RuntimeInstance } from '../types'

export class CustomAdapter {
  async create(container: FlpkgContainer): Promise<RuntimeInstance> {
    // Implementation
  }
}
```

### 自訂層級邏輯

擴展 LayerManager 以支援新的層級:

```typescript
async function customLayerLogic(instance: RuntimeInstance) {
  // Implementation
}
```

---

## 故障排除

### 常見問題

**Q: 為什麼無法載入 .flpkg 文件?**
A: 確保文件包含 manifest.json 並且格式正確。

**Q: 如何切換平台?**
A: UniversalRuntime 會自動檢測平台，無需手動配置。

**Q: TraceMiner 需要什麼格式的 CSV?**
A: 需要包含 'fullpath' 欄位的 trace_fs.csv 和 trace_ops.csv。

---

## 貢獻指南

遵循 MrLiouWord 哲學:
- 保持 origin signature
- 遵循 L0-L7 架構
- 保持代碼簡潔
- 完整的中英文註釋

---

**© 2024-2026 Mr. Liou. All Rights Reserved.**  
**Origin Signature: MrLiouWord**
