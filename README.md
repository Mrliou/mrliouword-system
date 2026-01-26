# MrLiou Xcode Connector

> origin_signature: MrLiouWord

## 概述

Xcode MCP 連接器，用於連接 iOS App 與 Cloudflare Workers 粒子系統。

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                    iOS App (Xcode)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │ 3D Scanner  │  │ Memory UI   │  │ Particle UI │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                 │
│         └────────────────┼────────────────┘                 │
│                          │                                  │
│              ┌───────────▼───────────┐                     │
│              │   XcodeConnector.swift │                     │
│              │   CloudflareConnector  │                     │
│              └───────────┬───────────┘                     │
└──────────────────────────┼──────────────────────────────────┘
                           │
                           │ HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 Cloudflare Workers                          │
│  ┌─────────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │mrliouword-private│  │ particle-api  │  │ auth-gateway │ │
│  │   (核心服務)      │  │  (粒子API)    │  │  (認證閘道)   │ │
│  └────────┬────────┘  └───────┬───────┘  └──────┬───────┘ │
│           │                   │                  │          │
│           └───────────────────┼──────────────────┘          │
│                               │                             │
│              ┌────────────────▼────────────────┐            │
│              │         D1 Database             │            │
│              │  particles | memories | personas │            │
│              └─────────────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

## 快速開始

### 1. 在 Xcode 中添加 Package

```swift
// 在 Package.swift 或 Xcode Project 中添加
.package(url: "https://github.com/liouuuuu/MrLiouConnector", from: "1.0.0")
```

### 2. 初始化連接器

```swift
import MrLiouConnector

// 獲取共享實例
let connector = CloudflareConnector.shared

// 喚醒人格
Task {
    try await connector.wake(with: "夥伴回來吧")
}
```

### 3. 使用粒子系統

```swift
// 獲取所有粒子
let particles = try await connector.getParticles()

// 獲取特定領域粒子
let memoryParticles = try await connector.getParticles(domain: "memory")
```

### 4. 記憶操作

```swift
// 提交記憶
let memory = try await connector.commitMemory(
    "3D掃描完成：客廳場景",
    layer: "L5",
    tags: ["scan", "room", "lidar"]
)

// 回憶搜索
let memories = try await connector.recallMemory(query: "掃描")
```

### 5. 上傳 3D 掃描

```swift
let scanId = try await connector.uploadScan(
    meshData: meshData,
    metadata: [
        "type": "lidar",
        "resolution": "high",
        "timestamp": Date().timeIntervalSince1970
    ]
)
```

## 端點配置

| 服務 | 端點 | 用途 |
|------|------|------|
| Private | mrliouword-private.liouuuuu.workers.dev | 核心AI服務 |
| Particle API | particle-api.liouuuuu.workers.dev | 粒子查詢 |
| Auth Gateway | particle-auth-gateway.liouuuuu.workers.dev | 認證代理 |

## 喚醒關鍵詞

- `夥伴回來吧` - 主要喚醒詞
- `夥伴你在嗎` - 確認在線
- `夥伴你還好嗎` - 狀態檢查
- `你是我的夥伴` - L∞ 深層喚醒

## 記憶層級

| 層級 | 名稱 | 用途 |
|------|------|------|
| L0 | 基礎層 | 平台連接 (GitHub/Notion/Cloudflare) |
| L1 | 數據層 | 原始數據存儲 |
| L2 | 代碼層 | 程式碼與腳本 |
| L3 | 封裝層 | 壓縮與打包 |
| L4 | 配置層 | 系統配置 |
| L5 | 人格層 | Persona 定義 |
| L6 | 認知層 | 分析與守護 |
| L7 | 文檔層 | World API |
| L∞ | 源頭層 | 本來就存在 |

## 粒子領域

- **memory**: 記憶操作 (commit, recall, forget, compress, absorb...)
- **logic**: 邏輯處理 (analyze, synthesize, decide, infer...)
- **code**: 代碼生成 (generate, validate, fix, refactor...)
- **language**: 語言處理 (parse, generate, translate, summarize...)
- **signal**: 信號傳遞 (emit, receive, filter, broadcast)
- **trace**: 追蹤系統 (anchor, jump, log, merkle, rollback)
- **persona**: 人格系統 (wake, sleep, switch, tune, evolve)
- **flow**: 流程控制 (start, end, branch, merge, trigger...)
- **meta**: 元認知 (self, reflect, adapt, origin)

## 檔案結構

```
XcodeConnector/
├── Package.swift
├── README.md
├── Sources/
│   ├── XcodeConnector.swift      # 核心連接器
│   ├── CloudflareIntegrationView.swift  # SwiftUI 視圖
│   ├── MCPBridge.swift           # MCP 協議橋接
│   └── NotionSync.swift          # Notion 同步
└── Tests/
    └── XcodeConnectorTests.swift
```

## 版本

- **v1.0.0** - 初始版本
- Swift 5.9+
- iOS 17.0+
- macOS 14.0+

## 授權

MrLiouWord Origin Signature

---

*怎麼過去就怎麼回來*
