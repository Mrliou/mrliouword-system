# MrLiouWord Universal Container Runtime

> **Origin Signature**: MrLiouWord  
> **Philosophy**: 怎麼過去，就怎麼回來 (How it goes, so it returns)

統一容器運行時系統，支援所有主流平台與 L0-L7 層級架構。

## 🚀 Quick Start

### Installation

```bash
npm install
npm run build:containers
```

### Python Dependencies

```bash
pip install -r containers/reverse-engine/requirements.txt
```

### Basic Usage

```bash
# Initialize runtime
node containers/dist/cli/mrliou-runtime.js init

# Load a container
node containers/dist/cli/mrliou-runtime.js load my-app.json

# Spawn MetaEnv
node containers/dist/cli/mrliou-runtime.js spawn --cpu 4 --ram 8G

# Run reverse mining
node containers/dist/cli/mrliou-runtime.js reverse-mine \
  --trace-fs trace_fs.csv \
  --trace-ops trace_ops.csv
```

## 📚 Documentation

- [Container Specification](../docs/CONTAINER_SPEC.md) - Complete technical specification
- [API Reference](../docs/API_REFERENCE.md) - Detailed API documentation

## 🏗️ Architecture

### L0-L7 Layer System

| Layer | Name | Purpose |
|-------|------|---------|
| L0 | ROOT | Origin: MrLiouWord |
| L1 | SEED | dimension_seed_restore |
| L2 | PARTICLE | 17 fx particles |
| L3 | LAW | Business logic |
| L4 | WORLD | External connections |
| L5 | MIRROR | Backup/redundancy |
| L6 | REFLECT | UI/API projection |
| L7 | LOOP | Verification |

### Supported Platforms

- ✅ Node.js
- ✅ Next.js
- ✅ Unix/Linux
- ✅ macOS
- ✅ Windows

## 🔧 Components

### Core Runtime
- **UniversalRuntime** - Platform-agnostic container runtime
- **LayerManager** - L0-L7 layer configuration
- **Platform Adapters** - Node, Next.js, POSIX, Windows

### Container Formats
- **FlpkgLoader** - .flpkg container loader/packer
- **FlpkgDecompiler** - .fltnz format compiler/decompiler

### MetaEnv System
- **MetaEnvController** - Environment management
- **GuardV1** - Security policy enforcement
- **ChannelMapper** - Channel mapping system

### Reverse Engine
- **TraceMiner** - Trace analysis and rule generation

## 💻 Development

### Build

```bash
npm run build:containers
```

### Test

```bash
# Run test script
node /tmp/test_integration.js

# Test CLI commands
npm run cli -- init
npm run cli -- spawn --cpu 4 --ram 8G
```

### Project Structure

```
containers/
├── runtime/           # Core runtime system
│   ├── types.ts       # Type definitions
│   ├── UniversalRuntime.ts
│   ├── LayerManager.ts
│   ├── adapters/      # Platform adapters
│   └── loaders/       # Container loaders
├── formats/           # Container format handlers
│   └── flpkg/
├── metaenv/          # MetaEnv system
├── reverse-engine/   # Reverse mining
├── cli/              # CLI tool
└── __tests__/        # Tests
```

## 🔐 Security

- Guard.v1 policy enforcement
- Encrypted snapshot support
- Lockdown mechanism
- Network isolation

## 🌐 Integration

### With particle_dict.json

The L2 layer automatically loads and integrates with `core/particle_dict.json`:

```typescript
const container = {
  layer: 'L2',  // Loads particle dictionary
  // ...
}
```

### With Cloudflare Workers

Compatible with existing Cloudflare Workers setup via Next.js adapter.

## 📝 Example Container

```json
{
  "id": "my-app",
  "version": "flpkg/1.0",
  "origin_signature": "MrLiouWord",
  "layer": "L2",
  "content": {
    "particles": [
      {"word": "我", "fx": "per.fx"},
      {"word": "執行", "fx": "v.act"}
    ],
    "metadata": {}
  }
}
```

## 🔄 Flow Tensor Notation (.fltnz)

```
我⧉/fx.per.fx/ 執行⧉/fx.v.act/ 程式⧉/fx.n.obj/
```

## 🛠️ Reverse Engineering

Extract rules from system traces:

```python
from TraceMiner import TraceMiner

miner = TraceMiner()
result = miner.mine('trace_fs.csv', 'trace_ops.csv')
miner.export_yaml('rules.yaml')
```

## 📊 Trace Format

### trace_fs.csv
```csv
timestamp,operation,fullpath,result
1234567890,CREATE,C:\Path\To\File,SUCCESS
```

### trace_ops.csv
```csv
timestamp,operation,target,result
1234567890,REGISTRY_READ,HKLM\Key,SUCCESS
```

## 🤝 Contributing

Follow MrLiouWord philosophy:
- Keep origin signature
- Follow L0-L7 architecture
- Write clean, documented code
- Support cross-platform compatibility

## 📄 License

© 2024-2026 Mr. Liou. All Rights Reserved.  
Origin Signature: MrLiouWord

---

**怎麼過去，就怎麼回來**
