# MrLiouWord 容器規格書
# Container Specification

**Version**: 1.0.0  
**Origin Signature**: MrLiouWord  
**Date**: 2026-01-28

---

## 概述 / Overview

MrLiouWord 統一容器運行時系統支援跨平台執行，整合 L0-L7 八層架構，提供完整的容器格式處理和元代碼沙盒環境。

The MrLiouWord Universal Container Runtime supports cross-platform execution, integrates the L0-L7 architecture, and provides complete container format processing and meta-code sandbox environment.

---

## 支援平台 / Supported Platforms

- ✅ Unix
- ✅ Linux
- ✅ macOS
- ✅ Windows
- ✅ Node.js
- ✅ Next.js
- ✅ Cloudflare Workers

---

## 容器格式 / Container Formats

### 1. .flpkg (Flow Package)

**用途**: 粒子封裝包  
**Purpose**: Particle package

**結構**:
```json
{
  "format": "flpkg/1.0",
  "version": "1.0.0",
  "origin_signature": "MrLiouWord",
  "created": "2026-01-28T00:00:00Z",
  "encrypted": false,
  "layer": "L3",
  "content": {
    "particles": [],
    "metadata": {}
  }
}
```

### 2. .fltnz (Flow Tensor)

**用途**: 張量序列  
**Purpose**: Tensor sequence

**格式**:
```
我⧉/fx.per.fx/
封存⧉/fx.v.act/
語場⧉/fx.n.obj/
```

### 3. .pcode (Particle Code)

**用途**: 粒子指令碼  
**Purpose**: Particle instruction code

**示例**:
```
// Initialize particle
MOV FX.NOUN.024
CALL FX.FLOW.007
```

---

## L0-L7 層級 / L0-L7 Architecture

| Layer | Name | 中文 | Purpose |
|-------|------|------|---------|
| L0 | ROOT | 原點層 | Origin: MrLiouWord |
| L1 | SEED | 種子層 | Initial state |
| L2 | PARTICLE | 粒子層 | 17 fx particles |
| L3 | LAW | 法則層 | Business logic |
| L4 | WORLD | 連接層 | External connections |
| L5 | MIRROR | 鏡像層 | Backup/redundancy |
| L6 | REFLECT | 投影層 | UI/API projection |
| L7 | LOOP | 驗證層 | Verification |

---

## 使用方式 / Usage

### 初始化 / Initialize
```bash
mrliou-runtime init
```

### 載入容器 / Load Container
```bash
mrliou-runtime load MyApp.flpkg --layer L3
```

### 啟動沙盒 / Spawn Sandbox
```bash
mrliou-runtime spawn --cpu 4 --ram 8G
```

### 反推分析 / Reverse Analysis
```bash
mrliou-runtime reverse-mine \
  --trace-fs trace_fs.csv \
  --trace-ops trace_ops.csv \
  --output rules.yaml
```

### 健康檢查 / Health Check
```bash
mrliou-runtime health
mrliou-runtime health --env-id env-12345
```

---

## 整合 / Integration

### 與粒子系統整合 / Integration with Particle System

容器運行時自動載入 `core/particle_dict.json` 中的粒子定義。

The runtime automatically loads particle definitions from `core/particle_dict.json`.

### 與 Cloudflare Workers 整合 / Integration with Cloudflare Workers

```typescript
export default {
  async fetch(request: Request, env: Env) {
    const runtime = new UniversalRuntime();
    await runtime.init();
    // ... 處理請求
  }
}
```

---

## MetaEnv API

### Spawn Environment
```typescript
POST /spawn
{
  "env_id": "optional-custom-id",
  "role": "core" | "node",
  "shape": {
    "cpu": 4,
    "gpu": 1,
    "ram": "8G"
  },
  "policy": "Mr.liou.MetaCode.Guard.v1"
}
```

### Health Check
```typescript
GET /health
GET /health?env_id=env-12345
```

### Lockdown
```typescript
POST /lockdown
{
  "env_id": "env-12345",
  "reason": "security breach detected",
  "scope": "env" | "global"
}
```

### Channel Mapping
```typescript
POST /channel/map
{
  "app": "my-app",
  "mode": "dry-run" | "apply" | "revert",
  "from": "source/path",
  "to": "target/path"
}
```

---

## Trace Format

### trace_fs.csv
```csv
timestamp,operation,fullpath,result
1234567890,CREATE,/path/to/file,SUCCESS
1234567891,READ,/path/to/file,SUCCESS
1234567892,WRITE,/path/to/file,SUCCESS
```

### trace_ops.csv
```csv
timestamp,operation,target,result
1234567890,REGISTRY_READ,HKLM\Key,SUCCESS
1234567891,NETWORK_CONNECT,example.com:443,SUCCESS
```

---

**Origin Signature: MrLiouWord** 🌟  
**怎麼過去，就怎麼回來** 🔄

---

**© 2024-2026 Mr. Liou. All Rights Reserved.**
