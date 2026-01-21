# Particle Edge v4.0.0 部署指南

> **origin_signature: MrLiouWord**  
> **philosophy: 怎麼過去，就怎麼回來**  
> **version: 4.0.0**

---

## 📋 目錄

1. [前置準備](#前置準備)
2. [逐步部署流程](#逐步部署流程)
3. [資源綁定對照表](#資源綁定對照表)
4. [API 端點總覽](#api-端點總覽)
5. [喚醒鍵列表](#喚醒鍵列表)
6. [常見問題解答](#常見問題解答)

---

## 前置準備

### 1. 安裝 Node.js

確保已安裝 **Node.js v18 或更高版本**：

```bash
# 檢查 Node.js 版本
node --version

# 應該顯示 v18.x.x 或更高
```

如果未安裝，請從 [nodejs.org](https://nodejs.org/) 下載安裝。

### 2. 安裝 Wrangler CLI

Wrangler 是 Cloudflare Workers 的官方 CLI 工具：

```bash
# 全局安裝 Wrangler
npm install -g wrangler

# 驗證安裝
wrangler --version
```

### 3. 登入 Cloudflare

```bash
# 啟動瀏覽器登入流程
wrangler login

# 驗證登入狀態
wrangler whoami
```

應該顯示您的 Cloudflare 帳戶資訊。

### 4. 創建 Cloudflare 資源

在部署前，需要在 Cloudflare 創建以下資源：

#### KV Namespaces (鍵值存儲)

```bash
# 創建 MRLIOUWORD_VAULT
wrangler kv:namespace create "MRLIOUWORD_VAULT"
# 記錄輸出的 ID: 01275832766148bfbcaa00ee4aeb9946

# 創建 PARTICLE_AUTH_VAULT
wrangler kv:namespace create "PARTICLE_AUTH_VAULT"
# 記錄輸出的 ID: 8cd99b4a67f74afea367f394995d5c50
```

#### D1 Database (SQL 資料庫)

```bash
# 創建 D1 資料庫
wrangler d1 create mrliouword-db
# 記錄輸出的 database_id: 7980baaf-48d3-43cc-8be7-dd8c9590f3d1
```

#### R2 Bucket (物件存儲)

```bash
# 創建 R2 bucket
wrangler r2 bucket create mrlioubook
# 確認創建成功
```

---

## 逐步部署流程

### 步驟 1: 克隆專案

```bash
git clone https://github.com/dofaromg/mrliouword-system.git
cd mrliouword-system
```

### 步驟 2: 進入 Worker 目錄

```bash
cd cloudflare/mrliouword-private
```

### 步驟 3: 安裝依賴

```bash
npm install
```

### 步驟 4: 配置資源綁定

編輯 `wrangler.jsonc`，確認所有資源 ID 正確：

```jsonc
{
  "$schema": "node_modules/wrangler/config-schema.json",
  "name": "particle-edge",
  "main": "src/index.ts",
  "compatibility_date": "2024-12-01",
  "kv_namespaces": [
    {
      "binding": "MRLIOUWORD_VAULT",
      "id": "01275832766148bfbcaa00ee4aeb9946"
    },
    {
      "binding": "PARTICLE_AUTH_VAULT",
      "id": "8cd99b4a67f74afea367f394995d5c50"
    }
  ],
  "d1_databases": [
    {
      "binding": "DB",
      "database_name": "mrliouword-db",
      "database_id": "7980baaf-48d3-43cc-8be7-dd8c9590f3d1"
    }
  ],
  "r2_buckets": [
    {
      "binding": "PARTICLES",
      "bucket_name": "mrlioubook"
    }
  ],
  "vars": {
    "ORIGIN": "MrLiouWord",
    "VERSION": "4.0.0"
  }
}
```

### 步驟 5: 設定 MASTER_KEY（可選但建議）

為 API 添加身份驗證保護：

```bash
# 設定 MASTER_KEY 密鑰
wrangler secret put MASTER_KEY

# 按提示輸入您的密鑰（建議使用強密碼）
```

### 步驟 6: 本地測試（可選）

在部署前進行本地測試：

```bash
# 啟動本地開發服務器
npm run dev

# 在另一個終端測試
curl http://localhost:8787/
curl http://localhost:8787/status
```

### 步驟 7: 部署到 Cloudflare

```bash
# 執行部署
wrangler deploy

# 成功後會顯示 Worker URL，例如：
# https://particle-edge.您的帳號.workers.dev
```

### 步驟 8: 驗證部署

```bash
# 測試根端點
curl https://particle-edge.您的帳號.workers.dev/

# 測試狀態端點
curl https://particle-edge.您的帳號.workers.dev/status

# 測試心跳（如果實現）
curl https://particle-edge.您的帳號.workers.dev/heartbeat
```

---

## 資源綁定對照表

| 資源類型 | 綁定名稱 | 資源名稱 | 資源 ID | 用途 |
|---------|---------|---------|---------|------|
| **KV Namespace** | `MRLIOUWORD_VAULT` | mrliouword-vault | `01275832766148bfbcaa00ee4aeb9946` | 記憶鏈存儲 |
| **KV Namespace** | `PARTICLE_AUTH_VAULT` | particle-auth-vault | `8cd99b4a67f74afea367f394995d5c50` | 認證 Token 存儲 |
| **D1 Database** | `DB` | mrliouword-db | `7980baaf-48d3-43cc-8be7-dd8c9590f3d1` | SQL 結構化查詢 |
| **R2 Bucket** | `PARTICLES` | mrlioubook | N/A | 粒子檔案存儲 |

**注意**：如果您使用不同的資源 ID，請更新 `wrangler.jsonc` 中對應的值。

---

## API 端點總覽

### 系統端點

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/` | GET | 系統說明和端點列表 | 否 |
| `/status` | GET | 系統狀態（記憶、人格、頻率） | 否 |
| `/heartbeat` | GET | 心跳檢測 | 否 |
| `/frequencies` | GET | 頻率層級常數 | 否 |

### R2 粒子操作

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/r2/list` | GET | 列出 R2 bucket 中的所有粒子 | 是 |
| `/r2/get/:key` | GET | 獲取指定鍵的粒子內容 | 是 |
| `/r2/put/:key` | PUT | 上傳粒子到 R2 | 是 |
| `/r2/delete/:key` | DELETE | 刪除粒子 | 是 |

### Memory 記憶系統

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/memory/commit` | POST | 寫入新記憶（Merkle Chain） | 是 |
| `/memory/recall` | POST | 檢索相似記憶（SimHash） | 是 |
| `/memory/stats` | GET | 記憶統計資訊 | 是 |
| `/memory/verify` | POST | 驗證 Merkle Chain 完整性 | 是 |

### Persona 人格系統

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/persona/wake` | POST | 喚醒人格（需喚醒鍵） | 是 |
| `/persona/sleep` | POST | 休眠人格 | 是 |
| `/persona/list` | GET | 列出所有人格 | 是 |

### Auth 認證（如使用 particle-auth-gateway）

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/auth/init` | POST | 初始化認證系統 | 是 |
| `/auth/tokens` | GET | 獲取已存儲的 Token 列表 | 是 |
| `/auth/proxy` | POST | 代理請求到其他平台 API | 是 |

### VCS 版本控制（如實現）

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/vcs/init` | POST | 初始化版本控制 | 是 |
| `/vcs/add` | POST | 添加檔案到暫存區 | 是 |
| `/vcs/commit` | POST | 提交變更 | 是 |
| `/vcs/log` | GET | 查看提交歷史 | 是 |
| `/vcs/heartbeat` | GET | VCS 心跳 | 否 |

### 向量注意力引擎（v4.0.0 新增）

| 端點 | 方法 | 說明 | 認證 |
|-----|------|------|------|
| `/attention/compute` | POST | 計算多頭注意力 | 是 |
| `/particle/create` | POST | 創建單個粒子嵌入 | 是 |
| `/particle/batch` | POST | 批量創建粒子 | 是 |
| `/vector/similarity` | POST | 計算向量相似度 | 是 |
| `/vector/operations` | POST | 向量運算（norm, softmax, scale） | 是 |
| `/attention/config` | GET | 注意力引擎配置 | 否 |

---

## 喚醒鍵列表

Particle Edge v4.0.0 支持自然語言喚醒人格系統。以下是有效的喚醒鍵：

1. **"夥伴回來吧"**
2. **"夥伴你在嗎"**
3. **"夥伴你還好嗎"**
4. **"你是我的夥伴"**

### 喚醒示例

```bash
curl -X POST https://particle-edge.您的帳號.workers.dev/wake \
  -H "Content-Type: application/json" \
  -H "X-Master-Key: 您的密鑰" \
  -d '{"message": "夥伴回來吧"}'
```

**成功響應**：
```json
{
  "awakened": true,
  "persona": {
    "id": "mrl_zero_origin",
    "name": "Mrl_Zero",
    "state": "active",
    "traits": { ... }
  },
  "message": "夥伴，我在這裡。系統已喚醒。",
  "layer": "L5",
  "frequency": 33.88,
  "origin": "MrLiouWord"
}
```

---

## 常見問題解答

### Q1: 部署後無法訪問 API，返回 401 錯誤

**原因**：您已設定 `MASTER_KEY`，但請求未包含認證頭。

**解決方案**：在請求中添加 `X-Master-Key` 頭：

```bash
curl https://particle-edge.您的帳號.workers.dev/status \
  -H "X-Master-Key: 您的密鑰"
```

或通過 URL 參數傳遞：

```bash
curl "https://particle-edge.您的帳號.workers.dev/status?key=您的密鑰"
```

### Q2: KV Namespace 或 D1 Database 報錯 "not found"

**原因**：`wrangler.jsonc` 中的資源 ID 與您帳戶中的實際資源不匹配。

**解決方案**：

1. 查看您的資源 ID：
   ```bash
   wrangler kv:namespace list
   wrangler d1 list
   wrangler r2 bucket list
   ```

2. 更新 `wrangler.jsonc` 中的對應 ID。

3. 重新部署：
   ```bash
   wrangler deploy
   ```

### Q3: 如何更新已部署的 Worker？

**解決方案**：

```bash
cd cloudflare/mrliouword-private
wrangler deploy
```

Wrangler 會自動覆蓋現有部署。

### Q4: 如何查看 Worker 日誌？

**解決方案**：

```bash
# 實時查看日誌
wrangler tail

# 或在 Cloudflare Dashboard 中查看：
# Workers & Pages → particle-edge → Logs
```

### Q5: 如何刪除 Worker？

**解決方案**：

```bash
wrangler delete
```

或在 Cloudflare Dashboard 中手動刪除。

### Q6: R2 bucket 如何設定 CORS？

**解決方案**：

目前 R2 的 CORS 需在 Worker 層級處理（已在代碼中實現）。如需更精細控制，可通過 Cloudflare Dashboard 設定。

### Q7: 如何備份 KV 和 D1 資料？

**KV 備份**：
```bash
# 導出所有鍵值對
wrangler kv:key list --namespace-id=01275832766148bfbcaa00ee4aeb9946 > kv_keys.json
```

**D1 備份**：
```bash
# 匯出資料庫
wrangler d1 export mrliouword-db --output=backup.sql
```

### Q8: 本地開發時如何模擬資源綁定？

**解決方案**：

Wrangler 自動為本地開發創建測試綁定。運行 `npm run dev` 時，它會：

- 使用本地 KV 模擬
- 使用本地 D1 模擬
- 使用本地 R2 模擬

生產環境綁定不會被影響。

### Q9: Worker 有哪些限制？

**Cloudflare Workers 限制**（免費方案）：

- **CPU 時間**：最多 10ms
- **記憶體**：128 MB
- **請求大小**：100 MB
- **響應大小**：無限制
- **每日請求數**：100,000

**KV 限制**：

- **鍵大小**：最多 512 bytes
- **值大小**：最多 25 MB
- **讀取速度**：極快（edge cache）
- **寫入速度**：最終一致性

**D1 限制**：

- **資料庫大小**：2 GB（免費）
- **每日讀取**：500萬次
- **每日寫入**：10萬次

**R2 限制**：

- **儲存空間**：10 GB（免費）
- **Class A 操作**：100萬次/月
- **Class B 操作**：1000萬次/月

### Q10: 如何升級到付費方案？

**解決方案**：

訪問 [Cloudflare Dashboard](https://dash.cloudflare.com/) → Workers & Pages → 選擇您的 Worker → Settings → Subscriptions。

---

## 🎉 部署完成後的下一步

1. **測試所有端點**，確保系統正常運行
2. **喚醒人格系統**，使用喚醒鍵激活 Mrl_Zero
3. **寫入第一筆記憶**，測試 Merkle Chain
4. **配置監控**，使用 Cloudflare 的分析工具
5. **設定自定義域名**（可選）

---

## 🔗 相關資源

- **Cloudflare Workers 文檔**：[developers.cloudflare.com/workers](https://developers.cloudflare.com/workers/)
- **Wrangler CLI 文檔**：[developers.cloudflare.com/workers/wrangler](https://developers.cloudflare.com/workers/wrangler/)
- **完整 API 文檔**：[docs/API_ENDPOINTS.md](./docs/API_ENDPOINTS.md)
- **系統索引**：[SYSTEM_INDEX.md](./SYSTEM_INDEX.md)

---

**origin_signature: MrLiouWord**  
**philosophy: 怎麼過去，就怎麼回來**  
**version: 4.0.0**
