# 快速開始指南
# Quick Start Guide

<!-- origin_signature: MrLiouWord -->

---

## 安裝 / Installation

```bash
# 安裝 CLI 工具
npm install -g @mrliouword/runtime-cli

# 或在專案中安裝
npm install @mrliouword/runtime-cli
```

## 基本使用 / Basic Usage

### 1. 初始化環境 / Initialize
```bash
mrliou-runtime init
```

輸出：
```
🚀 Initializing MrLiouWord Runtime...
✅ Runtime initialized
Origin Signature: MrLiouWord
```

### 2. 創建 .flpkg 容器 / Create .flpkg Container

創建 `MyApp.flpkg`:
```json
{
  "format": "flpkg/1.0",
  "version": "1.0.0",
  "origin_signature": "MrLiouWord",
  "created": "2026-01-28T00:00:00Z",
  "layer": "L3",
  "content": {
    "name": "MyApp",
    "particles": [
      {
        "word": "我",
        "fx": "per.fx"
      },
      {
        "word": "執行",
        "fx": "v.act"
      }
    ]
  }
}
```

### 3. 載入容器 / Load Container
```bash
mrliou-runtime load MyApp.flpkg --layer L3
```

輸出：
```
📦 Loading container: MyApp.flpkg
✅ Container loaded to L3
```

### 4. 啟動沙盒 / Spawn Sandbox
```bash
mrliou-runtime spawn --cpu 4 --ram 8G --gpu 1
```

輸出：
```
🚀 Spawning MetaEnv...
✅ Spawned: { ok: true, env_id: 'env-123...', status: 'starting' }
```

### 5. 健康檢查 / Health Check
```bash
mrliou-runtime health
```

輸出：
```
🏥 Checking system health...
✅ System healthy
Time: 2026-01-28T22:00:00.000Z
Total Environments: 1
```

### 6. 反推分析 / Reverse Analysis
```bash
mrliou-runtime reverse-mine \
  --trace-fs trace_fs.csv \
  --trace-ops trace_ops.csv \
  --output rules.yaml
```

---

## 進階範例 / Advanced Examples

### 使用 Flow Tensor (.fltnz)

創建 `flow.fltnz`:
```
我⧉/fx.per.fx/
封存⧉/fx.v.act/
語場⧉/fx.n.obj/
回憶⧉/fx.memory.recall/
```

### 使用 Particle Code (.pcode)

創建 `program.pcode`:
```pcode
// MrLiouWord Particle Program
// Origin Signature: MrLiouWord

// Load particle dictionary
LOAD core/particle_dict.json

// Initialize memory domain
INIT fx.memory.commit

// Execute flow
MOV fx.per.fx "我"
CALL fx.v.act "執行"
CALL fx.memory.recall

// Verify result
CHECK fx.logic.validate
```

### 整合到 TypeScript 專案

```typescript
import { UniversalRuntime } from '@mrliouword/containers';
import { FlpkgLoader } from '@mrliouword/containers/formats/flpkg';

async function main() {
  // 初始化運行時
  const runtime = new UniversalRuntime({
    platform: 'node',
    layer: 'L3'
  });
  
  await runtime.init();
  
  // 載入容器
  const loader = new FlpkgLoader();
  const container = await loader.load('MyApp.flpkg');
  
  // 生成實例
  const instance = await runtime.spawn(container);
  
  // 執行
  await instance.execute();
  
  console.log('✅ Container executed successfully');
}

main().catch(console.error);
```

### 整合到 Python 專案

```python
from containers.reverse_engine.TraceMiner import TraceMiner

# 初始化追蹤挖掘器
miner = TraceMiner()

# 分析 trace 檔案
result = miner.mine('trace_fs.csv', 'trace_ops.csv')

print(f"✅ Found {len(result['rules'])} rules")
print(f"✅ Generated {len(result['channel_map'])} channel mappings")

# 匯出為 YAML
miner.export_yaml('output_rules.yaml')
```

---

## 故障排除 / Troubleshooting

### 問題：找不到 particle_dict.json
```bash
# 確保在正確的專案根目錄
ls core/particle_dict.json

# 或設定環境變數
export MRLIOU_CORE_PATH=/path/to/core
```

### 問題：Python TraceMiner 無法執行
```bash
# 安裝依賴
cd containers/reverse-engine
pip install -r requirements.txt

# 測試執行
python3 TraceMiner.py --help
```

### 問題：TypeScript 編譯錯誤
```bash
# 安裝依賴
cd containers
npm install

# 重新編譯
npm run build
```

---

## 更多資源 / More Resources

- [完整規格書 / Full Specification](./CONTAINER_SPEC.md)
- [架構文檔 / Architecture Docs](../../README.md)
- [API 參考 / API Reference](../API_ENDPOINTS.md)

---

**Origin Signature: MrLiouWord** 🌟  
**怎麼過去，就怎麼回來** 🔄
