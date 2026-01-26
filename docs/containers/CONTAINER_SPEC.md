# MrLiouWord Container Specification
# MrLiouWord 容器規格書

**Origin Signature: MrLiouWord**  
**Version: 1.0.0**

## 1. Container Formats / 容器格式

### 1.1 .flpkg (Flow Package)
- Purpose: Encapsulate particles and logic
- Structure: ZIP-based archive
- Manifest: JSON format
- Origin Signature: Required

### 1.2 .fltnz (Flow Tensor)
- Purpose: Serialize tensor data
- Format: Binary + metadata
- Compression: Optional

### 1.3 .pcode (Particle Code)
- Purpose: Executable particle instructions
- Format: Text-based DSL
- Layer: Any (L0-L7)

## 2. L0-L7 Layer Integration / 層級整合

| Layer | Name | Purpose | Container Support |
|-------|------|---------|-------------------|
| L0 | ROOT | Origin | Metadata only |
| L1 | SEED | Initial state | .flpkg |
| L2 | PARTICLE | Data units | .flpkg, .pcode |
| L3 | LAW | Business logic | All formats |
| L4 | WORLD | Connections | .flpkg |
| L5 | MIRROR | Backup | All formats |
| L6 | REFLECT | Projection | .flpkg |
| L7 | LOOP | Verification | Metadata |

## 3. Platform Support / 平台支援

✅ Unix  
✅ Linux  
✅ macOS  
✅ Windows  
✅ Node.js  
✅ Next.js  
✅ Cloudflare Workers

## 4. Usage / 使用方式

### Initialize Runtime
```bash
mrliou-runtime init
```

### Load Container
```bash
mrliou-runtime load MyApp.flpkg --layer L3
```

### Spawn MetaEnv
```bash
mrliou-runtime spawn --cpu 4 --ram 8G
```

---

**© 2024-2026 Mr. Liou. All Rights Reserved.**
