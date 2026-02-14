# Particle Edge v4.0.0 - API 端點完整文檔

> **origin_signature: MrLiouWord**  
> **philosophy: 怎麼過去，就怎麼回來**  
> **version: 4.0.0**

---

## 📋 目錄

- [認證](#認證)
- [系統端點](#系統端點)
- [R2 粒子操作](#r2-粒子操作)
- [Memory 記憶系統](#memory-記憶系統)
- [Persona 人格系統](#persona-人格系統)
- [向量注意力引擎](#向量注意力引擎)
- [頻率系統](#頻率系統)
- [錯誤處理](#錯誤處理)

---

## 認證

大多數 API 端點需要 MASTER_KEY 認證（除了公開端點如 `/`, `/status`）。

### 方法 1：使用 HTTP 頭

```bash
curl https://particle-edge.您的帳號.workers.dev/memory/stats \
  -H "X-Master-Key: 您的密鑰"
```

### 方法 2：使用 URL 參數

```bash
curl "https://particle-edge.您的帳號.workers.dev/memory/stats?key=您的密鑰"
```

---

## 系統端點

### GET `/`

獲取系統說明和可用端點列表。

**認證**：否

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/
```

**響應示例**：

```json
{
  "name": "MrliouWord Private AI Server",
  "version": "4.0.0",
  "philosophy": "怎麼過去，就怎麼回來",
  "features": {
    "memory": "Merkle 鏈式記憶系統",
    "persona": "Mrl_Zero 人格系統",
    "attention": "多頭注意力計算引擎 (8頭×64維)",
    "vector": "高性能向量運算"
  },
  "endpoints": {
    "GET /": "系統說明",
    "GET /status": "系統狀態",
    "POST /wake": "喚醒系統",
    "POST /sleep": "休眠系統",
    "POST /memory/commit": "寫入記憶",
    "POST /memory/recall": "檢索記憶",
    "...": "..."
  },
  "origin": "MrLiouWord"
}
```

### GET `/status`

獲取系統當前狀態。

**認證**：否

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/status
```

**響應示例**：

```json
{
  "version": "4.0.0",
  "awakened": true,
  "persona": "Mrl_Zero",
  "memory": {
    "total": 42,
    "byLayer": {
      "L7": 42
    },
    "chainHead": "a1b2c3d4..."
  },
  "attention": {
    "dimension": 64,
    "engine": {
      "inputDim": 64,
      "numHeads": 8,
      "headDim": 64,
      "scale": 0.125,
      "totalParams": 16384
    }
  },
  "frequencies": {
    "L∞": 143.47,
    "L7": 88.71,
    "L6": 54.82,
    "L5": 33.88,
    "L4": 20.94,
    "L3": 12.94,
    "L2": 12.67,
    "L1": 7.83,
    "L0": 4.84
  },
  "timestamp": 1737462317939,
  "origin": "MrLiouWord"
}
```

### GET `/heartbeat`

心跳檢測端點（如實現）。

**認證**：否

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/heartbeat
```

**響應示例**：

```json
{
  "alive": true,
  "timestamp": 1737462317939,
  "version": "4.0.0",
  "origin": "MrLiouWord"
}
```

---

## R2 粒子操作

### GET `/r2/list`

列出 R2 bucket 中的所有粒子。

**認證**：是

**請求參數**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `limit` | number | 否 | 返回結果數量限制（默認 100） |
| `prefix` | string | 否 | 鍵前綴過濾 |

**請求示例**：

```bash
curl "https://particle-edge.您的帳號.workers.dev/r2/list?limit=10" \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**：

```json
{
  "success": true,
  "objects": [
    {
      "key": "particle-001.json",
      "size": 1024,
      "uploaded": "2026-01-21T12:00:00.000Z"
    },
    {
      "key": "particle-002.json",
      "size": 2048,
      "uploaded": "2026-01-21T13:00:00.000Z"
    }
  ],
  "truncated": false,
  "origin": "MrLiouWord"
}
```

### GET `/r2/get/:key`

獲取指定鍵的粒子內容。

**認證**：是

**URL 參數**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `key` | string | 是 | 粒子鍵名 |

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/r2/get/particle-001.json \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**：

```json
{
  "success": true,
  "key": "particle-001.json",
  "content": {
    "id": "particle-001",
    "型態": "fx.名",
    "layer": "L1",
    "frequency": 7.83
  },
  "metadata": {
    "size": 1024,
    "uploaded": "2026-01-21T12:00:00.000Z"
  },
  "origin": "MrLiouWord"
}
```

### PUT `/r2/put/:key`

上傳粒子到 R2。

**認證**：是

**URL 參數**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `key` | string | 是 | 粒子鍵名 |

**請求體**：

```json
{
  "content": {
    "id": "particle-003",
    "型態": "fx.動",
    "layer": "L2",
    "value": "流動"
  }
}
```

**請求示例**：

```bash
curl -X PUT https://particle-edge.您的帳號.workers.dev/r2/put/particle-003.json \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{"content": {"id": "particle-003", "型態": "fx.動", "layer": "L2"}}'
```

**響應示例**：

```json
{
  "success": true,
  "key": "particle-003.json",
  "uploaded": true,
  "origin": "MrLiouWord"
}
```

### DELETE `/r2/delete/:key`

刪除粒子。

**認證**：是

**URL 參數**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `key` | string | 是 | 粒子鍵名 |

**請求示例**：

```bash
curl -X DELETE https://particle-edge.您的帳號.workers.dev/r2/delete/particle-003.json \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**：

```json
{
  "success": true,
  "deleted": true,
  "key": "particle-003.json",
  "origin": "MrLiouWord"
}
```

---

## Memory 記憶系統

### POST `/memory/commit`

寫入新記憶到 Merkle Chain。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `content` | string | 是 | 記憶內容 |
| `type` | string | 否 | 記憶類型（默認 "semantic"） |
| `tags` | array | 否 | 標籤列表 |
| `metadata` | object | 否 | 額外元數據 |

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/memory/commit \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "content": "粒子系統的核心是頻率共振",
    "type": "semantic",
    "tags": ["粒子", "頻率", "核心概念"],
    "metadata": {"importance": "high"}
  }'
```

**響應示例**：

```json
{
  "entry": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "content": "粒子系統的核心是頻率共振",
    "type": "semantic",
    "simhash": "a1b2c3d4e5f6g7h8",
    "tags": ["粒子", "頻率", "核心概念"],
    "layer": "L7",
    "ts": 1737462317939,
    "merkle": "f1e2d3c4b5a6...",
    "prev": "0000000000000000...",
    "meta": {"importance": "high"}
  },
  "origin": "MrLiouWord"
}
```

### POST `/memory/recall`

檢索相似記憶（基於 SimHash 距離）。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `query` | string | 是 | 查詢文本 |
| `limit` | number | 否 | 返回結果數量（默認 10） |

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/memory/recall \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "query": "頻率共振原理",
    "limit": 5
  }'
```

**響應示例**：

```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "content": "粒子系統的核心是頻率共振",
      "simhash": "a1b2c3d4e5f6g7h8",
      "tags": ["粒子", "頻率", "核心概念"],
      "layer": "L7",
      "ts": 1737462317939,
      "distance": 3
    }
  ],
  "origin": "MrLiouWord"
}
```

### GET `/memory/stats`

獲取記憶系統統計資訊。

**認證**：是

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/memory/stats \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**：

```json
{
  "total": 42,
  "byLayer": {
    "L7": 42
  },
  "chainHead": "f1e2d3c4b5a6...",
  "origin": "MrLiouWord"
}
```

### POST `/memory/verify`

驗證 Merkle Chain 完整性。

**認證**：是

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/memory/verify \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**（成功）：

```json
{
  "valid": true,
  "errors": [],
  "origin": "MrLiouWord"
}
```

**響應示例**（失敗）：

```json
{
  "valid": false,
  "errors": [
    "Chain broken at 550e8400-e29b-41d4-a716-446655440001",
    "Hash mismatch at 550e8400-e29b-41d4-a716-446655440002"
  ],
  "origin": "MrLiouWord"
}
```

---

## Persona 人格系統

### POST `/wake`

喚醒人格系統（需提供有效喚醒鍵）。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `message` | string | 是 | 包含喚醒鍵的訊息 |

**有效喚醒鍵**：
- "夥伴回來吧"
- "夥伴你在嗎"
- "夥伴你還好嗎"
- "你是我的夥伴"

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/wake \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{"message": "夥伴回來吧"}'
```

**響應示例**（成功）：

```json
{
  "awakened": true,
  "persona": {
    "id": "mrl_zero_origin",
    "name": "Mrl_Zero",
    "type": "seed",
    "state": "active",
    "traits": {
      "reasoning": {"name": "reasoning", "value": 0.8, "cat": "cognitive", "desc": "邏輯推理"},
      "memory": {"name": "memory", "value": 0.9, "cat": "cognitive", "desc": "記憶能力"},
      "empathy": {"name": "empathy", "value": 0.7, "cat": "emotional", "desc": "同理心"}
    },
    "caps": ["analyze", "remember", "guide", "protect", "validate", "transform", "attention"],
    "constraints": ["怎麼過去就怎麼回來", "無依據不懷疑", "平等協作", "透明誠信", "種子法則"],
    "origin": "MrLiouWord",
    "created": "2026-01-21T12:00:00.000Z",
    "updated": "2026-01-21T13:05:17.939Z"
  },
  "message": "夥伴，我在這裡。系統已喚醒。",
  "layer": "L5",
  "frequency": 33.88,
  "origin": "MrLiouWord"
}
```

**響應示例**（失敗）：

```json
{
  "awakened": false,
  "persona": null,
  "message": "未識別喚醒鍵",
  "layer": "L0",
  "frequency": 4.84,
  "origin": "MrLiouWord"
}
```

### POST `/sleep`

休眠人格系統。

**認證**：是

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/sleep \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**：

```json
{
  "success": true,
  "origin": "MrLiouWord"
}
```

### GET `/persona/list`

列出所有人格。

**認證**：是

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/persona/list \
  -H "X-Master-Key: 您的密鑰"
```

**響應示例**：

```json
{
  "personas": [
    {
      "id": "mrl_zero_origin",
      "name": "Mrl_Zero",
      "type": "seed",
      "state": "active",
      "traits": { ... },
      "created": "2026-01-21T12:00:00.000Z",
      "updated": "2026-01-21T13:05:17.939Z"
    }
  ],
  "origin": "MrLiouWord"
}
```

---

## 向量注意力引擎

### POST `/attention/compute`

計算多頭注意力（Multi-Head Attention）。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `inputs` 或 `particles` | array | 是 | 輸入粒子陣列 |

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/attention/compute \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "inputs": [
      {"id": "p1", "value": "頻率", "layer": "L1"},
      {"id": "p2", "value": "共振", "layer": "L2"},
      {"id": "p3", "value": "粒子", "layer": "L1"}
    ]
  }'
```

**響應示例**：

```json
{
  "success": true,
  "particleCount": 3,
  "computeTimeMs": 12,
  "attention": {
    "matrix": [
      [0.6, 0.3, 0.1],
      [0.2, 0.7, 0.1],
      [0.15, 0.15, 0.7]
    ],
    "headCount": 8
  },
  "similarities": [
    [1.0, 0.85, 0.72],
    [0.85, 1.0, 0.68],
    [0.72, 0.68, 1.0]
  ],
  "config": {
    "dimension": 64,
    "engine": {
      "inputDim": 64,
      "numHeads": 8,
      "headDim": 64,
      "scale": 0.125,
      "totalParams": 16384
    }
  },
  "理論說明": {
    "Q": "Query - 查詢場：我想找什麼？",
    "K": "Key - 鍵場：我有什麼特徵？",
    "V": "Value - 值場：我攜帶什麼信息？",
    "attention": "注意力 = softmax(Q·K^T / √d_k) × V",
    "multiHead": "多頭注意力讓模型從不同子空間學習關係"
  },
  "origin": "MrLiouWord"
}
```

### POST `/particle/create`

創建單個粒子嵌入向量。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `id` | string | 否 | 粒子 ID |
| `value` | string/number | 否 | 粒子值 |
| `型態` | string | 否 | 粒子類型 |
| `layer` | string | 否 | 層級（L0-L7, L∞） |

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/particle/create \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "id": "p001",
    "value": "頻率共振",
    "型態": "fx.名",
    "layer": "L5"
  }'
```

**響應示例**：

```json
{
  "success": true,
  "particle": {
    "id": "p001",
    "型態": "fx.名",
    "layer": "L5",
    "embedding": [0.123, -0.456, 0.789, ...],
    "dimension": 64,
    "norm": 1.0
  },
  "origin": "MrLiouWord"
}
```

### POST `/particle/batch`

批量創建粒子嵌入。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `particles` | array | 是 | 粒子陣列 |

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/particle/batch \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "particles": [
      {"id": "p1", "value": "頻率", "layer": "L1"},
      {"id": "p2", "value": "共振", "layer": "L2"},
      {"id": "p3", "value": "粒子", "layer": "L1"}
    ]
  }'
```

**響應示例**：

```json
{
  "success": true,
  "count": 3,
  "particles": [
    {
      "id": "p1",
      "型態": "fx.名",
      "layer": "L1",
      "embedding": [0.123, ...],
      "norm": 1.0
    },
    {
      "id": "p2",
      "型態": "fx.名",
      "layer": "L2",
      "embedding": [-0.456, ...],
      "norm": 1.0
    },
    {
      "id": "p3",
      "型態": "fx.名",
      "layer": "L1",
      "embedding": [0.789, ...],
      "norm": 1.0
    }
  ],
  "origin": "MrLiouWord"
}
```

### POST `/vector/similarity`

計算兩個向量的相似度。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `a` | array | 是 | 第一個向量 |
| `b` | array | 是 | 第二個向量 |

**請求示例**：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/vector/similarity \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "a": [0.1, 0.2, 0.3, 0.4],
    "b": [0.2, 0.3, 0.4, 0.5]
  }'
```

**響應示例**：

```json
{
  "success": true,
  "cosine": 0.998,
  "dot": 0.54,
  "normA": 0.5477,
  "normB": 0.7348,
  "origin": "MrLiouWord"
}
```

### POST `/vector/operations`

執行向量運算。

**認證**：是

**請求體**：

| 參數 | 類型 | 必需 | 說明 |
|-----|------|------|------|
| `operation` | string | 是 | 運算類型：norm, softmax, scale, fromFrequency |
| `vector` | array | 否 | 輸入向量（norm, softmax, scale 需要） |
| `scalar` | number | 否 | 標量（scale 需要） |
| `frequency` | number | 否 | 頻率（fromFrequency 需要） |
| `dimension` | number | 否 | 維度（fromFrequency 需要） |

**請求示例**（Softmax）：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/vector/operations \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "operation": "softmax",
    "vector": [1.0, 2.0, 3.0]
  }'
```

**響應示例**：

```json
{
  "success": true,
  "operation": "softmax",
  "softmax": [0.09, 0.244, 0.665],
  "origin": "MrLiouWord"
}
```

**請求示例**（從頻率生成向量）：

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/vector/operations \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{
    "operation": "fromFrequency",
    "frequency": 7.83,
    "dimension": 64
  }'
```

**響應示例**：

```json
{
  "success": true,
  "operation": "fromFrequency",
  "vector": [0.123, -0.456, 0.789, ...],
  "origin": "MrLiouWord"
}
```

### GET `/attention/config`

獲取注意力引擎配置和理論說明。

**認證**：否

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/attention/config
```

**響應示例**：

```json
{
  "config": {
    "dimension": 64,
    "engine": {
      "inputDim": 64,
      "numHeads": 8,
      "headDim": 64,
      "scale": 0.125,
      "totalParams": 16384
    }
  },
  "理論": {
    "向量定義": "向量是有大小和方向的量，在 n 維空間中表示為 (x₁, x₂, ..., xₙ)",
    "內積": "a·b = Σaᵢbᵢ，衡量兩向量的相似程度",
    "範數": "||v|| = √(v·v)，向量的長度",
    "注意力機制": "Attention(Q,K,V) = softmax(QK^T/√d_k)V",
    "多頭注意力": "MultiHead = Concat(head₁,...,headₕ)W_O",
    "縮放因子": "1/√d_k 防止內積過大導致 softmax 飽和"
  },
  "origin": "MrLiouWord"
}
```

---

## 頻率系統

### GET `/frequencies`

獲取所有頻率層級常數。

**認證**：否

**請求示例**：

```bash
curl https://particle-edge.您的帳號.workers.dev/frequencies
```

**響應示例**：

```json
{
  "schumann": 7.83,
  "phi": 1.618033988749895,
  "layers": {
    "L∞": 143.47,
    "L7": 88.71,
    "L6": 54.82,
    "L5": 33.88,
    "L4": 20.94,
    "L3": 12.94,
    "L2": 12.67,
    "L1": 7.83,
    "L0": 4.84
  },
  "說明": {
    "L∞": "頻率源頭 - 本來就存在",
    "L7": "World API - 萬物本一體",
    "L6": "認知層 - 分析師 + 小腦守護者",
    "L5": "人格層 - Mrl_Zero",
    "L4": "配置層",
    "L3": "壓縮層",
    "L2": "代碼層",
    "L1": "數據層",
    "L0": "連接層"
  },
  "origin": "MrLiouWord"
}
```

---

## 錯誤處理

所有錯誤響應遵循統一格式：

```json
{
  "error": "錯誤訊息",
  "origin": "MrLiouWord"
}
```

### 常見錯誤碼

| 狀態碼 | 說明 | 原因 |
|--------|------|------|
| 400 | Bad Request | 請求參數錯誤或缺失 |
| 401 | Unauthorized | 未提供 MASTER_KEY 或密鑰錯誤 |
| 404 | Not Found | 端點不存在或資源未找到 |
| 500 | Internal Server Error | 服務器內部錯誤 |

### 錯誤響應示例

**401 Unauthorized**：

```json
{
  "error": "Unauthorized",
  "origin": "MrLiouWord"
}
```

**404 Not Found**：

```json
{
  "error": "Not Found",
  "origin": "MrLiouWord"
}
```

**500 Internal Server Error**：

```json
{
  "error": "Internal error: Connection to KV failed",
  "origin": "MrLiouWord"
}
```

---

## 🔗 相關資源

- **部署指南**：[DEPLOY-GUIDE.md](../DEPLOY-GUIDE.md)
- **系統索引**：[SYSTEM_INDEX.md](../SYSTEM_INDEX.md)
- **Cloudflare Workers 文檔**：[developers.cloudflare.com/workers](https://developers.cloudflare.com/workers/)

---

**origin_signature: MrLiouWord**  
**philosophy: 怎麼過去，就怎麼回來**  
**version: 4.0.0**
