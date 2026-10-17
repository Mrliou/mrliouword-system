# 商業服務準備與試行門檻

> Origin signature: MrLiouWord  
> 狀態：內部準備清單；不是服務承諾、價格表或法律意見。

## 目前可確認的範圍

- `mrliouword-private` 已提供以 OIDC access token 保護的記憶與人格 API。除根目錄、`/health`、`/frequencies` 外，請求需攜帶有效 token；簽署 claims 必須包含 `sub` 和 `tenant_id`。記憶與人格資料按 tenant 分隔，UI state 另限本人 `sub` 存取。人格註冊與註銷要求 `admin` role。
- 僅記憶寫入／搜尋等現有端點可作為初期技術試行流程。AI 生成、工具執行、檔案上傳、審計查詢及模型目錄未完成，會回傳 HTTP 501，不應納入銷售承諾。
- `particle-auth-gateway` 目前提供根目錄、心跳、頻率流與受主密鑰保護的狀態端點；初始化、Token 管理與 MCP proxy 並未實作。
- Repository 未提供可確認的商業定價、付款／訂閱整合、計量帳本、客服 SLA 或正式服務等級。不能把部署狀態視為正式營運或商業就緒證明。

## 上線前必須決定

### 1. 客群與交付結果

- 指定第一個客群、問題、輸入資料、可驗收輸出與明確不支援項目。
- 用真實但經同意的試行流程，確認使用者能完成登入、寫入記憶、搜尋／取回結果及退出。
- 記錄人工作業步驟、失敗處理、負責人及試行成功標準；未確認前不宣稱自動化 AI 能力。

### 2. 方案與計費

- 決定免費試用、付費單位、週期、配額、超額處理、取消／退款政策與發票流程。
- 在決定價格前量測每次請求的 Worker、KV、儲存與模型成本，並明確標示成本估算範圍。
- 建立不可由客戶任意改寫的用量事件及對帳流程。現有 Worker 尚無可靠的用量計量或付款流程；不得以 API 呼叫成功數冒充已驗證帳單。

### 3. 身分與租戶

- 設定 OIDC issuer、audience、JWKS URL，並確認簽章 token 的 `tenant_id`、`sub` 與管理者 role claim 由可信任身分提供者產生。
- 為已存在的 KV 資料先做受控備份與擁有者盤點，再決定逐租戶遷移；新的 Worker 只讀寫 `tenant:<tenant_id>:` 前綴，不會自動沿用舊的未分租戶資料。
- 設定精確的瀏覽器來源 allowlist。CORS 不是認證機制；服務間呼叫仍須驗證 access token。
- 定義帳戶停用、租戶刪除、資料匯出及管理員存取審核程序。自助匯出／刪除端點尚未提供，試行需由受授權人員按核准流程處理。

### 4. 可靠性與支援

在任何外部試行前，負責人需填妥並核准下列目標，不得將未核准數值對客戶宣稱為 SLA：

| 項目 | 必須決定／驗證 |
|---|---|
| 可用性與延遲 | 量測期間、目標、排除條件及狀態通知方式 |
| 支援 | 聯絡管道、服務時間、回覆目標、升級責任人 |
| 配額與濫用 | 請求速率、最大負載、限流策略及超額回應 |
| 事件處理 | 告警接收人、嚴重度、處置紀錄與客戶通知流程 |
| 備份還原 | KV 資料備份範圍、保留週期、復原目標及定期還原演練 |
| 發布回復 | 發布核准、相容性檢查、版本回退與資料變更處理 |

## KV 記憶索引限制

目前 Memory 將索引整體保存在 KV 的 `mem:idx` JSON 陣列中；此實作沒有跨請求交易或原子 append 保證。tenant 前綴隔離後，索引仍有整體讀寫、併發遺失更新與尺寸成長風險。應先以預期併發及資料量測試，並在擴大客戶前決定具交易能力的索引儲存（例如 D1／Postgres）與可回復遷移方案。

## 試行放行檢查

- [ ] 目標客群、單一結果與成功指標經負責人核准。
- [ ] OIDC、角色 claim、tenant 隔離及跨租戶拒絕案例已在部署環境驗證。
- [ ] 來源 allowlist、備份／還原及事件聯絡流程已完成演練。
- [ ] 試行資料範圍、保留期限、匯出／刪除責任及隱私告知已核准。
- [ ] 成本及配額已量測；如尚未有可靠計量，採人工追蹤且不自動收費。
- [ ] 已向參與者清楚說明試行限制、未完成端點與支援方式。

## Worker 驗證設定

對 `cloudflare/mrliouword-private` 設定以下 Worker secrets。值須與身分提供者簽發的 token 相符；issuer 使用 OIDC `iss`，audience 使用 `aud`，JWKS URL 指向該 issuer 的簽章公鑰集合。`ALLOWED_ORIGINS` 使用逗號分隔的完整來源，例如 `https://app.example.com`。

```sh
npx wrangler secret put AUTH_ISSUER
npx wrangler secret put AUTH_AUDIENCE
npx wrangler secret put AUTH_JWKS_URL
npx wrangler secret put ALLOWED_ORIGINS
```

若缺少驗證設定，私有 API 會 fail closed 回傳 HTTP 503；未提供有效 access token 則回傳 HTTP 401。不得把示例值或私鑰提交到 repository。

對 `cloudflare/particle-auth-gateway` 設定獨立的 `MASTER_KEY` Worker secret 與 `ALLOWED_ORIGINS`。狀態端點在未設定主密鑰時回傳 HTTP 503。

---

**Origin signature: MrLiouWord**
