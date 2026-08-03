---
title: "MRL_ASI 官網跨來源復盤與 GitHub 接入 v1.2"
date: "2026-08-03"
author: "Mr.liou"
origin_signature: "MrLiouWord"
status: "review"
tags: [website, github, notion, dropbox, reconciliation, provenance]
---

# MRL_ASI 官網跨來源復盤與 GitHub 接入 v1.2

> origin_signature: `MrLiouWord`  
> authority: `Mr.liou`  
> official_domain: `Mrliouword.com`  
> branch: `mrl/website-cross-source-reconciliation-v1.2`

## 1. 本文件定位

本文件把 2026-08-03 完成的 Notion × Dropbox 官網企劃復盤接回 GitHub。它不是新增平行架構，而是把既有程式、規格、部署紀錄、來源衝突與真正缺口對齊到目前活躍的實作倉庫。

官網定位仍然是 MRL Mother 的 Projection / Entry / Verification Surface。外部平台只作 Provider、Adapter、Runtime、Evidence 或投影載體。

## 2. GitHub 倉庫判定

### 活躍實作倉庫

`dofaromg/mrliouword-system`

判定依據：

- 2026-07-21 至 2026-07-24 持續有 Runtime、ParticleLayer、Provider/Adapter、部署與測試提交。
- README 已包含自主化 Provider/Adapter 與自架部署內容。
- PR #60、#56、#28、#22、#13、#4 等提供可追溯的工程歷史。

### 組織投影倉庫

`Mrliou/mrliouword-system`

目前 README 與活躍實作倉庫並不完全同步，缺少較新的 Provider/Adapter 自主化段落。暫時分類為：

`MIRROR_CANDIDATE / VERSION_DRIFT`

在完成 commit/tree 比對前，不直接把任何一方宣告為唯一 Canon，也不覆蓋任一倉庫。

## 3. 已找回、不得重建的 GitHub 能力

| 能力 | GitHub 證據 | 官網處理 |
|---|---|---|
| Provider/Adapter 架構 | PR #60、commit `ad43d29d15806443ae4eeee231533a979da006ba` | 官網 AI、Auth、Memory、Storage、UI State 應接既有 Factory，不另建第二套 Provider 層 |
| 自架部署骨架 | `deploy/docker-compose.yml`、Caddy、Postgres、Redis、MinIO、Authentik | 列為 Existing Implementation，補 Dockerfile、Secrets、Runtime 驗證 |
| Universal Container Runtime | PR #13、#28 | 官網 Console 的 Runtime/Container 功能先接現有 containers/，不另寫平行 Runtime |
| FLPKG / FLTNZ / PCODE | PR #13、#28 | 官網 Roundtrip Workspace 接現有 compiler/decompiler，補實際 Hash 驗收 |
| Unified Gateway | PR #4 | API Gateway 先盤點現有端點、D1/KV/R2 綁定與版本，不另建相同路由 |
| UnifiedParticle / reversible adapters | PR #56 | Notion、Dropbox、GitHub 資產映射可沿用 canonical transport model |
| 文件整合與驗證 | PR #22、#23 | 官網 Docs 應從現有 docs/ 索引與 metadata 發布，不重複搬運 |
| Particle plugin runtime | PR #32 | Tools/Tasks/Trace 可接 manifest、policy、Merkle trace 與 pack exporter |

## 4. GitHub 發現的真實缺口

### 4.1 Provider/Adapter 尚未閉合

PR #60 明確保留：

- Authentik refresh-token rotation 未完成。
- `deploy/Dockerfile.nextjs`、`deploy/Dockerfile.gateway` 仍為 placeholder。
- Gemini / OpenAI / Anthropic provider cases 未接線。
- Firebase → Postgres 資料遷移腳本尚未完成。

這些項目分類為 `PARTIAL_IMPLEMENTATION`，不得在官網標示為 Runtime PASS。

### 4.2 Runtime 線上狀態未重新驗證

PR #21 只確認 130 個檔案與本地建置，外部 Worker 健康測試因執行環境防火牆而未完成。這表示：

`REPOSITORY_VERIFIED != LIVE_RUNTIME_VERIFIED`

官網 Trust Center 必須分開呈現 Code、CI、Deployment Record、Live Health 四種證據。

### 4.3 倉庫鏡像漂移

同名倉庫至少存在：

- `dofaromg/mrliouword-system`
- `Mrliou/mrliouword-system`
- `dofaromg/mrliouword-system1`
- 其他 MrLiouWord 命名倉庫

需要建立 Repo Registry，以 commit SHA、default branch、visibility、用途、owner、upstream/mirror 關係與最後同步時間判定 Canonical Candidate。

### 4.4 網域與部署設定需重新定錨

現有程式與 PR 中出現多個 Worker URL、`mrliouword.com`、`api.mrliouword.com`、`auth.mrliouword.com` 等部署目標。正式權位已鎖定為：

- Primary Domain: `Mrliouword.com`
- Canonical URL: `https://mrliouword.com`

任何 DNS、Caddy、Cloudflare、Worker route 或環境變數都必須經 Domain Reconciliation Gate，不以舊文件直接覆蓋現況。

## 5. 接入官網計畫的任務

| Task | GitHub 工作 |
|---|---|
| T068 | 建立 Repo/File Canonical Candidate Resolver，保留所有 Raw 與 Mirror |
| T069 | 建立 dev/staging/prod/local/tailscale Endpoint Authority Matrix |
| T071 | 建立 Subdomain & Route Registry |
| T074 | 盤點現有網站 Repo、Next.js、Worker、部署資產與可運行狀態 |
| T075 | 將 SYSTEM_INDEX、docs、registry 與 Relation/Asset Map 接到 Sitemap |
| T077 | 接回 Auth/Portal/Provider，不做平行登入 |
| T079 | 接回 FLTNZ/FLPKG Runtime，執行 input→archive→restore Hash 驗收 |
| T082 | 建立 Code/CI/Deploy/Live 四層 Evidence 與 freshness |
| T083 | Notion、Dropbox、GitHub、Mother、Website 五方閉環驗收 |

## 6. GitHub 處理原則

1. 不直接在 `main` 覆蓋；所有修正先進 review branch 與 Draft PR。
2. 不把 PR 描述中的「完成」直接當成目前 Runtime 狀態。
3. 不刪除重複倉庫或文件；先建立 upstream / mirror / archive / candidate 分類。
4. 不重新發明 Provider、Runtime、Gateway、Particle、Container、Docs Index。
5. 所有官網公開數字與端點必須帶 `as_of`、`scope`、`source`、`evidence_status`。
6. 所有正式域名設定以 Mr.liou 最新指令為最高權位。

## 7. 下一個 GitHub 工程切片

本 PR 只固定復盤結果與 GitHub 接入基線。後續程式修改應分成獨立 PR：

1. Repo Registry + Mirror Drift Report。
2. Website Asset Inventory + Stack Decision Gate。
3. Domain / Endpoint Registry。
4. Existing Provider/Runtime integration tests。
5. Source Freshness / Evidence API。

---

**Closure rule:** 先搜尋、再比對、只回收真實增量；未實測 Runtime 不宣稱 PASS。  
**Signature:** `MrLiouWord`
