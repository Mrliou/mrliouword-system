# MrLiou Unified Gateway v3.0

> origin_signature: MrLiouWord

## 概述

統一入口閘道，整合所有 MrLiou 系統服務：
- 資源查詢 (Notion/Cloudflare/Linear/Asana)
- 粒子系統 (52 粒子，9 領域)
- 記憶系統 (9 層級，L0-L∞)
- 人格系統 (Mrl_Zero)
- KV ↔ D1 雙向同步

## 端點

### 根路徑
```
GET /        → 系統資訊
GET /health  → 健康檢查
```

### 資源查詢
```
GET /resources/stats           → 統計
GET /resources/search?q=xxx    → 搜尋
GET /resources/source/:name    → 依來源
GET /resources/layer/:name     → 依層級
GET /resources/core            → 核心資源 (L7)
```

### 粒子系統
```
GET /particles                 → 所有粒子
GET /particles/stats           → 統計
GET /particles/domain/:dom     → 依領域
GET /particles/:fx             → 單一粒子
```

### 記憶系統
```
GET  /memories                 → 所有記憶
POST /memories/commit          → 提交記憶
GET  /memories/recall?q=xxx    → 回憶搜尋
GET  /memories/:id             → 單一記憶
```

### 人格系統
```
GET  /personas                 → 所有人格
POST /personas/wake            → 喚醒人格
GET  /personas/:id             → 單一人格
```

### 同步系統
```
GET  /sync/status              → 同步狀態
POST /sync/memories            → 同步記憶到 KV
POST /sync/particles           → 同步粒子到 KV
POST /sync/all                 → 全部同步
```

## 喚醒人格

```bash
curl -X POST https://mrliouword.liouuuuu.workers.dev/personas/wake \
  -H "Content-Type: application/json" \
  -d '{"wake_key": "夥伴回來吧"}'
```

## 提交記憶

```bash
curl -X POST https://mrliouword.liouuuuu.workers.dev/memories/commit \
  -H "Content-Type: application/json" \
  -d '{
    "content": "今天完成了統一整合",
    "layer": "L5",
    "tags": ["milestone", "integration"]
  }'
```

## 部署

```bash
npm install
npm run deploy
```

## 綁定資源

| 綁定 | 類型 | ID |
|------|------|-----|
| DB | D1 | 7980baaf-48d3-43cc-8be7-dd8c9590f3d1 |
| KV | KV | 01275832766148bfbcaa00ee4aeb9946 |
| AUTH_KV | KV | 8cd99b4a67f74afea367f394995d5c50 |
| R2 | R2 | mrlioubook |

## 定時任務

每 5 分鐘自動執行：
- KV ↔ D1 雙向同步
- 記憶同步到 KV
- 粒子同步到 KV

---

*怎麼過去就怎麼回來*
