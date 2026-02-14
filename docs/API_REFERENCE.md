# MrLiouWord Container API Reference
# MrLiouWord 容器 API 參考

> **Origin Signature**: MrLiouWord  
> **Version**: 1.0.0

---

## UniversalRuntime

### Constructor

```typescript
const runtime = new UniversalRuntime()
```

自動檢測當前平台並初始化適配器。

### Methods

#### `spawn(container: FlpkgContainer): Promise<RuntimeInstance>`

生成容器運行時實例。

**Parameters:**
- `container`: FlpkgContainer - 容器定義

**Returns:** Promise<RuntimeInstance>

**Example:**
```typescript
const container: FlpkgContainer = {
  id: 'my-app',
  version: 'flpkg/1.0',
  origin_signature: 'MrLiouWord',
  layer: 'L3',
  content: {
    particles: [],
    metadata: {}
  }
}

const instance = await runtime.spawn(container)
```

#### `load(path: string): Promise<FlpkgContainer>`

從文件載入容器。

**Parameters:**
- `path`: string - 文件路徑 (.json, .flpkg, .zip)

**Returns:** Promise<FlpkgContainer>

**Example:**
```typescript
const container = await runtime.load('./my-app.flpkg')
```

---

## LayerManager

### `configure(instance: RuntimeInstance, layer: Layer): Promise<void>`

配置運行時實例的層級。

**Parameters:**
- `instance`: RuntimeInstance - 運行時實例
- `layer`: Layer - 層級 ('L0' | 'L1' | ... | 'L7')

**Example:**
```typescript
import { configure } from './LayerManager'

await configure(instance, 'L2')
```

### LAYERS Constant

```typescript
const LAYERS = {
  L0: 'ROOT',
  L1: 'SEED',
  L2: 'PARTICLE',
  L3: 'LAW',
  L4: 'WORLD',
  L5: 'MIRROR',
  L6: 'REFLECT',
  L7: 'LOOP',
}
```

---

## MetaEnvController

### Constructor

```typescript
const controller = new MetaEnvController()
```

### Methods

#### `spawn(req: SpawnRequest): Promise<SpawnResponse>`

生成元環境。

**SpawnRequest:**
```typescript
interface SpawnRequest {
  env_id?: string
  role?: 'core' | 'node'
  shape: {
    cpu: number
    gpu?: number
    ram: string
  }
  policy?: string
}
```

**SpawnResponse:**
```typescript
interface SpawnResponse {
  ok: boolean
  env_id: string
  status: string
}
```

**Example:**
```typescript
const result = await controller.spawn({
  shape: {
    cpu: 4,
    ram: '8G'
  },
  policy: 'Mr.liou.MetaCode.Guard.v1'
})

console.log(`Environment: ${result.env_id}`)
```

#### `applyPolicy(env_id: string, policy: string): Promise<void>`

應用安全策略。

**Parameters:**
- `env_id`: string - 環境 ID
- `policy`: string - 策略名稱

**Example:**
```typescript
await controller.applyPolicy('env-123', 'Mr.liou.MetaCode.Guard.v1')
```

#### `createSnapshot(env_id: string, encrypted?: boolean): Promise<string>`

創建環境快照。

**Parameters:**
- `env_id`: string - 環境 ID
- `encrypted`: boolean - 是否加密 (預設: true)

**Returns:** Promise<string> - 快照 ID

**Example:**
```typescript
const snapshot_id = await controller.createSnapshot('env-123', true)
```

#### `channelMap(app: string, from: string, to: string, mode?: string): Promise<any>`

通道映射。

**Parameters:**
- `app`: string - 應用名稱
- `from`: string - 源路徑
- `to`: string - 目標路徑
- `mode`: 'dry-run' | 'apply' | 'revert' (預設: 'dry-run')

**Returns:** Promise<{ ok: boolean, changes: string[], revert_token?: string }>

**Example:**
```typescript
const result = await controller.channelMap(
  'my-app',
  '/data/old',
  '/data/new',
  'dry-run'
)

if (result.ok) {
  console.log('Changes:', result.changes)
}
```

#### `lockdown(env_id: string, reason: string): Promise<void>`

緊急鎖死環境。

**Parameters:**
- `env_id`: string - 環境 ID
- `reason`: string - 鎖死原因

**Example:**
```typescript
await controller.lockdown('env-123', 'Security breach detected')
```

---

## GuardV1

### Methods

#### `applyPolicy(env_id: string, policy: string): Promise<void>`

應用安全策略。

**Example:**
```typescript
const guard = new GuardV1()
await guard.applyPolicy('env-123', 'Mr.liou.MetaCode.Guard.v1')
```

#### `lockdown(env_id: string, reason: string): Promise<void>`

執行鎖死程序:
1. 斷開外部連接
2. 撤銷所有 tokens
3. 凍結快照

---

## ChannelMapper

### Methods

#### `map(app: string, from: string, to: string, mode: 'dry-run' | 'apply' | 'revert'): Promise<any>`

執行通道映射。

**Modes:**
- `dry-run`: 模擬映射，不實際執行
- `apply`: 執行映射
- `revert`: 回退映射

---

## FlpkgLoader

### Functions

#### `load(filepath: string): Promise<FlpkgContainer>`

載入 .flpkg 容器。

**Supported formats:**
- `.json` - JSON 格式
- `.flpkg` - ZIP 格式
- `.zip` - ZIP 格式

**Example:**
```typescript
import { load } from './formats/flpkg/FlpkgLoader'

const container = await load('./my-app.flpkg')
```

#### `pack(container: FlpkgContainer, outputPath: string): Promise<void>`

打包容器為 .flpkg 文件。

**Example:**
```typescript
import { pack } from './formats/flpkg/FlpkgLoader'

await pack(container, './output.flpkg')
```

---

## FlpkgDecompiler

### Functions

#### `decompile(container: FlpkgContainer): string`

將容器轉換為 .fltnz 格式。

**Returns:** Flow Tensor Notation 字串

**Example:**
```typescript
import { decompile } from './formats/flpkg/FlpkgDecompiler'

const fltnz = decompile(container)
// Output: "我⧉/fx.per.fx/ 封存⧉/fx.v.act/"
```

#### `compile(fltnz: string, metadata: any): FlpkgContainer`

將 .fltnz 格式編譯為容器。

**Example:**
```typescript
import { compile } from './formats/flpkg/FlpkgDecompiler'

const container = compile(
  "我⧉/fx.per.fx/ 封存⧉/fx.v.act/",
  { layer: 'L2' }
)
```

---

## TraceMiner (Python)

### Class: TraceMiner

#### `mine(trace_fs_path: str, trace_ops_path: str) -> Dict`

分析追蹤文件產生規則。

**Parameters:**
- `trace_fs_path`: 文件系統追蹤 CSV
- `trace_ops_path`: 操作追蹤 CSV

**Returns:** 包含 rules 和 channel_map 的字典

**Example:**
```python
from TraceMiner import TraceMiner

miner = TraceMiner()
result = miner.mine('trace_fs.csv', 'trace_ops.csv')

print(f"Found {len(result['rules'])} rules")
```

#### `export_yaml(output_path: str)`

匯出為 YAML 格式。

**Example:**
```python
miner.export_yaml('rules_output.yaml')
```

---

## Types

### FlpkgContainer

```typescript
interface FlpkgContainer {
  id: string
  version: string
  origin_signature: string
  layer: 'L0' | 'L1' | 'L2' | 'L3' | 'L4' | 'L5' | 'L6' | 'L7'
  content: {
    particles?: any[]
    references?: any[]
    metadata?: Record<string, any>
  }
  encrypted?: boolean
}
```

### RuntimeInstance

```typescript
interface RuntimeInstance {
  id: string
  container: FlpkgContainer
  platform: Platform
  status: 'starting' | 'running' | 'stopped' | 'failed'
  metadata: {
    origin_signature: string
    created_at: string
    [key: string]: any
  }
  particles?: any[]
  execute(): Promise<void>
  stop(): Promise<void>
}
```

### Platform

```typescript
type Platform = 'node' | 'next' | 'unix' | 'linux' | 'macos' | 'windows'
```

---

## CLI Commands

### `mrliou-runtime init`

初始化運行時環境。

### `mrliou-runtime load <file>`

載入容器文件。

**Options:**
- `-l, --layer <layer>`: 指定層級 (預設: L2)

### `mrliou-runtime spawn`

生成元環境。

**Options:**
- `--cpu <cores>`: CPU 核心數 (預設: 4)
- `--ram <size>`: 記憶體大小 (預設: 8G)
- `--policy <policy>`: 安全策略

### `mrliou-runtime reverse-mine`

執行反推分析。

**Options:**
- `--trace-fs <file>`: trace_fs.csv 路徑 (必需)
- `--trace-ops <file>`: trace_ops.csv 路徑 (必需)
- `-o, --output <file>`: 輸出文件 (預設: rules_output.yaml)

---

## Error Handling

所有異步方法都可能拋出錯誤，建議使用 try-catch:

```typescript
try {
  const container = await runtime.load('my-app.flpkg')
} catch (error) {
  console.error('Failed to load container:', error)
}
```

---

## Best Practices

1. **Layer Selection**: 根據應用需求選擇適當的層級
2. **Security**: 始終使用加密快照保護敏感數據
3. **Channel Mapping**: 先使用 dry-run 模式驗證映射
4. **Lockdown**: 僅在緊急情況下使用 lockdown

---

**© 2024-2026 Mr. Liou. All Rights Reserved.**  
**Origin Signature: MrLiouWord**
