# MrLiouWord 自主化遷移指引

> **「怎麼過去，就怎麼回來」**
> Origin Signature: MrLiouWord

---

## 架構概覽（文字版）

```
使用者瀏覽器
    │  HTTPS 443
    ▼
Caddy (反向代理 + 自動 TLS)
    │
    ├──▶ mrliouword.com          → mrliouai-control-center (Next.js :3000)
    │
    └──▶ api.mrliouword.com      → mrl-api-gateway (:8080)
             │
             ├── /health                      系統健康檢查
             ├── /api/mrl/runtimeos/ai/*      AI 模型 (→ DL580 :7810)
             ├── /api/mrl/memory/*            記憶搜尋 (→ pgvector / KV)
             ├── /api/mrl/tools/execute       工具執行
             ├── /api/mrl/files/*             檔案存取 (→ MinIO)
             ├── /api/mrl/audit/traces        審計記錄 (→ Postgres)
             └── /api/mrl/ui-state/*          UI 狀態 (→ Postgres / Firestore)
                  │
                  ├── postgres (pgvector)     主資料庫
                  ├── redis                   快取/佇列
                  ├── minio                   檔案儲存
                  └── authentik               登入系統 (auth.mrliouword.com)
                       │
                       ▼
             auth.mrliouword.com → authentik-server (:9000)
```

### Provider 切換矩陣

| 功能 | Phase 0-1 (Firebase) | Phase 2+ (自主) | 環境變數 |
|------|---------------------|----------------|---------|
| 認證 | FirebaseAuthAdapter | AuthentikAuthAdapter | `NEXT_PUBLIC_AUTH_PROVIDER` |
| UI 狀態 | FirestoreUIStateAdapter | PostgresUIStateAdapter | `UI_STATE_PROVIDER` |
| 記憶 | CloudflareKV (mrliouword-private) | pgvector via API | `MEMORY_PROVIDER` |
| 檔案 | Cloudflare R2 | MinIOStorageAdapter | `STORAGE_PROVIDER` |
| AI | MRLiouLocalProvider | MRLiouLocalProvider | `AI_PROVIDER` |

---

## 遷移分階段

### Phase 0 — 現況（Firebase 依賴）
**狀態**：已部署  
**目標**：維持既有 Firebase 路徑可用，不中斷服務

- [x] Cloudflare Workers 部署（mrliouword-private, particle-auth-gateway）
- [x] KV/D1/R2 存儲綁定
- [x] `NEXT_PUBLIC_AUTH_PROVIDER=firebase`（預設值）

---

### Phase 1 — Provider 抽象層（本 PR）
**狀態**：已完成  
**目標**：業務邏輯不再直接 import Firebase SDK

- [x] 定義 `AuthProvider`, `AIProvider`, `MemoryProvider`, `StorageProvider`, `UIStateProvider` 介面
- [x] 實作 `FirebaseAuthAdapter`（過渡用）
- [x] 實作 `AuthentikAuthAdapter`（OIDC/PKCE 骨架）
- [x] 實作 `FirestoreUIStateAdapter`, `PostgresUIStateAdapter`
- [x] 實作 `MinIOStorageAdapter`, `MRLiouLocalProvider`
- [x] Provider factory（依環境變數切換）
- [x] 17 個單元測試全部通過
- [x] 補齊 API Gateway 端點契約（`/health`, `/api/mrl/*`）
- [x] 更新 `.env.example`
- [x] `deploy/docker-compose.yml` 骨架

---

### Phase 2 — 自主服務啟動
**目標**：本地啟動完整自主化堆疊

**步驟**：

```bash
# 1. 複製並填寫環境變數
cp deploy/.env.deploy deploy/.env
vim deploy/.env   # 填入所有 REPLACE_WITH_... 值

# 2. 啟動容器
docker compose -f deploy/docker-compose.yml up -d

# 3. 確認服務健康
docker compose -f deploy/docker-compose.yml ps
curl https://api.mrliouword.com/health
```

**Authentik 初始設定**：

1. 訪問 `https://auth.mrliouword.com/if/flow/initial-setup/` 建立管理員帳戶
2. 建立 Application：
   - Provider type: OAuth2/OpenID Connect
   - Client type: Public（PKCE，無 client secret）
   - Redirect URI: `https://mrliouword.com/auth/callback`
   - Scopes: `openid profile email offline_access`
3. 取得 Client ID 填入 `NEXT_PUBLIC_AUTH_CLIENT_ID`
4. 設定 `NEXT_PUBLIC_AUTH_PROVIDER=authentik`

**MinIO 初始設定**：

```bash
# 建立 bucket
docker compose -f deploy/docker-compose.yml exec minio \
  mc alias set local http://localhost:9000 $MINIO_ACCESS_KEY $MINIO_SECRET_KEY
docker compose -f deploy/docker-compose.yml exec minio \
  mc mb local/mrliouai
```

---

### Phase 3 — 完整資料遷移
**目標**：將 Firebase/Cloudflare KV 資料遷移至 Postgres/pgvector

**待辦**：
- [ ] 撰寫資料遷移腳本（Firebase Firestore → Postgres ui_preferences）
- [ ] 撰寫記憶遷移腳本（CloudflareKV → memory_documents）
- [ ] 設定 `UI_STATE_PROVIDER=postgres`
- [ ] 設定 `MEMORY_PROVIDER=api`（透過 mrl-api-gateway → pgvector）
- [ ] 實作 mrl-api-gateway 完整 Postgres 查詢（TODO 已標記）

---

### Phase 4 — 強化安全與監控
**目標**：生產環境強化

**待辦**：
- [ ] Prometheus + Grafana 監控面板
- [ ] Loki 日誌收集
- [ ] Fail2Ban / Rate limiting 在 Caddy 層
- [ ] 定期備份（Postgres → MinIO）
- [ ] JWT 驗證在 mrl-api-gateway（Authentik JWK endpoint）

---

### Phase 5 — Kubernetes 升級（選填）
**目標**：高可用性部署

**待辦**：
- [ ] Helm charts
- [ ] HPA 自動擴縮
- [ ] Persistent Volume Claims

---

## 啟動步驟

### 本地開發

```bash
# TypeScript Provider 測試
npm install --legacy-peer-deps
npx jest containers/__tests__/providers.test.ts

# Python Agent 測試
python -m pytest tests/unit -q

# Cloudflare Worker 本地開發
npm run dev
```

### 伺服器部署（Phase 2+）

```bash
# 前置：Docker 和 Docker Compose v2
apt install docker.io docker-compose-plugin

# 複製設定
cp deploy/.env.deploy deploy/.env

# 填寫所有必要值（請見 deploy/.env.deploy 說明）
# 重要：以下不可留空
#   POSTGRES_PASSWORD
#   MINIO_ACCESS_KEY / MINIO_SECRET_KEY
#   AUTHENTIK_SECRET_KEY
#   AUTH_CLIENT_SECRET（Phase 2+）

# 啟動
docker compose -f deploy/docker-compose.yml up -d

# 查看狀態
docker compose -f deploy/docker-compose.yml logs -f
```

### 驗證 Provider 切換

```bash
# 確認 firebase auth
NEXT_PUBLIC_AUTH_PROVIDER=firebase node -e "
  const { createAuthProvider } = require('./containers/providers');
  const p = createAuthProvider();
  console.log(p.constructor.name); // FirebaseAuthAdapter
"

# 確認 authentik auth
NEXT_PUBLIC_AUTH_PROVIDER=authentik node -e "
  const { createAuthProvider } = require('./containers/providers');
  const p = createAuthProvider();
  console.log(p.constructor.name); // AuthentikAuthAdapter
"

# 健康檢查
curl https://api.mrliouword.com/health
# { "ok": true, "service": "mrl-silly-api", "version": "2.1.0", "origin_signature": "MrLiouWord" }
```

---

## 常見錯誤排查

### `NEXT_PUBLIC_FIREBASE_API_KEY` 未設定
**症狀**：FirebaseAuthAdapter 初始化失敗，瀏覽器報 `Firebase: Error (auth/invalid-api-key)`  
**解法**：填入 `.env` 中的 Firebase 設定，或設定 `NEXT_PUBLIC_AUTH_PROVIDER=authentik`

### JWT issuer 不符（401 Unauthorized）
**症狀**：Authentik 登入後 API Gateway 返回 401  
**解法**：確認 `AUTH_ISSUER` 與 Authentik Application 的 OpenID Configuration issuer 一致：
```bash
curl https://auth.mrliouword.com/application/o/mrliouai/.well-known/openid-configuration | jq .issuer
```

### CORS 錯誤（跨域請求被阻擋）
**症狀**：瀏覽器報 `Access-Control-Allow-Origin` 錯誤  
**解法**：
1. 確認 Caddy `header` 設定中 `Access-Control-Allow-Origin` 指向正確前端網域
2. 確認 API Gateway 的 CORS middleware 允許前端 origin
3. 臨時除錯可將 origin 改為 `*`（生產環境禁用）

### Authentik PKCE callback 失敗
**症狀**：瀏覽器 console 報 `OAuth state mismatch`  
**解法**：確認 `redirect_uri` 與 Authentik Application 設定完全一致（包含 trailing slash）

### MinIO 連線失敗
**症狀**：`mrl-api-gateway` 日誌報 `connect ECONNREFUSED minio:9000`  
**解法**：
```bash
# 確認 minio 服務啟動
docker compose -f deploy/docker-compose.yml ps minio
docker compose -f deploy/docker-compose.yml logs minio
```

### `DATABASE_URL` 憑證錯誤
**症狀**：Postgres 連線失敗，日誌報 `authentication failed`  
**解法**：確認 `POSTGRES_USER`, `POSTGRES_PASSWORD` 與 `DATABASE_URL` 一致，並重建容器：
```bash
docker compose -f deploy/docker-compose.yml down postgres
docker volume rm mrliouword_postgres-data  # 僅開發環境
docker compose -f deploy/docker-compose.yml up -d postgres
```

---

## 未完成的 TODO

| 項目 | 檔案 | 說明 |
|------|------|------|
| Authentik 實際租戶參數 | `AuthentikAuthAdapter.ts` | 填入真實 base URL 與 client ID |
| Token 自動刷新 | `AuthentikAuthAdapter.ts:218` | 使用 refresh_token 換新 access_token |
| MRL Gateway 完整實作 | `mrl-api-gateway (Dockerfile.gateway)` | 目前為 stub，需接入 Postgres/MinIO |
| GeminiAIAdapter | `createAIProvider.ts` | 新增 case 'gemini' |
| OpenAIAdapter | `createAIProvider.ts` | 新增 case 'openai' |
| CloudflareR2StorageAdapter | `createStorageProvider.ts` | 新增 case 'r2' |
| Dockerfile.nextjs | `deploy/` | 需建立 Next.js 應用後補充 |
| Dockerfile.gateway | `deploy/` | 需建立 Node.js gateway 後補充 |
| 資料遷移腳本 | `scripts/` | Firebase → Postgres 遷移 |
| Prometheus metrics | `mrl-api-gateway` | 新增 `/metrics` 端點 |
