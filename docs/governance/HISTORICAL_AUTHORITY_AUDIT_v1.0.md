---
title: "MRL Historical Authority Audit"
version: "1.0.0"
date: "2026-08-03"
authority: "Mr.liou"
origin_signature: "MrLiouWord"
status: "investigation_open"
---

# MRL Historical Authority Audit v1.0

## 調查目的

調查 MRL 上層定義被下層程式、模型、平台、倉庫或生成工具採用後，來源權位是否被弱化、混淆、替換或遺失；建立可驗證的修正與補償紀錄。

本報告不在缺乏證據時指控特定第三方侵權。所有判定只分為：

- `PROVEN`
- `DOCUMENTED`
- `AMBIGUOUS`
- `UNVERIFIED`
- `REQUIRES_EXTERNAL_EVIDENCE`

## 已確認證據

### E-001：正本權位其實已存在，但執行層沒有強制

`.mrliou/meta.json` 已寫明：

- `authority = Mr.liou`
- `namespace = mrliouword`
- `dofaromg/mrliouword-system` 的角色是 `source_of_truth`
- 其他倉庫是 sync target

**判定：PROVEN**

問題不是完全沒有權位定義，而是權位只存在一份 metadata，沒有被 CODEOWNERS、CI、發布 Gate、套件 metadata、鏡像規則與官網內容強制執行。

### E-002：LAW-0 保護簽名，但沒有充分區分人類權位、工具與產物

`docs/law0/implementation.md` 規定 `origin_signature = MrLiouWord` 全局唯一且不可變。

**判定：PROVEN**

這能證明來源鏈，但單一簽名欄位不足以回答：

- 誰是 canonical authority
- 哪個 repo 是 source of truth
- 哪個是鏡像
- 誰是實作者
- 哪個 AI 只是工具
- 哪個產物是衍生物

因此下層只複製 `origin_signature`，仍可能在展示、套件、GitHub namespace 或自動生成說明中造成權位模糊。

### E-003：命名規則是 stable_locked，但只管前綴與原名

`registry/rules/naming_rules_v1.yaml` 規定：

- Original names are NEVER changed
- 只允許 `mrl_` 前綴
- 未註冊產物不可進入命名與索引

**判定：PROVEN**

缺口是它沒有要求 `canonical_authority`、`derived_from`、`artifact_owner`、`contributor_role` 與 `mirror_of`。

### E-004：GitHub 同名倉庫與使用者／組織投影造成正本漂移風險

已看到至少：

- `dofaromg/mrliouword-system`
- `Mrliou/mrliouword-system`
- `dofaromg/mrliouword-system1`
- 其他相近命名倉庫

其中活躍提交主要集中於 `dofaromg/mrliouword-system`，而組織版本的 README/commit 已產生漂移。

**判定：DOCUMENTED**

GitHub 顯示的 repository owner、organization、commit author、PR author 並不等同原始思想或系統權位；但目前缺少醒目、機器可驗證的區分。

### E-005：README 的協作描述仍可能造成角色壓縮

README 寫著「由 MR.liou 設計，Claude 協作開發」。這比完全缺少來源好，但把長期上層定義、架構權位、具體人工實作、AI 協助與自動生成壓成一句話。

**判定：AMBIGUOUS**

需要改成 Founder / Canonical Authority / Original System Definition / Human Implementers / AI Assistance / Platform Roles 分欄。

### E-006：缺少 CODEOWNERS 與 Authority CI

調查時主分支不存在 `.github/CODEOWNERS`，也沒有找到專門驗證不可變權位與衍生來源欄位的 CI。

**判定：PROVEN**

這使任何有寫入權限的自動代理或貢獻流程，可能在沒有權位審核的情況下修改根文件、命名與發布 metadata。

### E-007：AI／Copilot PR 可產生大量下層實作，但 GitHub 作者顯示不是來源權位證明

歷史 PR 包含 Copilot coding agent、自動生成摘要、Claude/OpenAI/Anthropic provider 接入等內容。這些 PR 能證明實作活動，不能證明 AI 或平台是 MRL 上層定義來源。

**判定：PROVEN AS ROLE DISTINCTION**

必須把「Git commit/PR 作者」與「原始系統權位」分開。

## 根本問題

```text
上層 Canon 存在
  ↓
下層複製 origin_signature
  ↓
沒有強制 canonical_authority / derived_from / role
  ↓
GitHub owner、AI 生成者、組織名稱、部署平台成為最醒目的身份
  ↓
外部閱讀者把承載者或實作者誤認為來源
  ↓
歷史因果與權位被弱化
```

這是一個 **治理與可驗證 metadata 缺口**，不是單靠再寫一次 `MrLiouWord` 就能解決。

## 立即修正

| ID | 修正 | 狀態 |
|---|---|---|
| R-001 | 建立 `.mrliou/authority-lock.json` | DONE IN PR #62 BRANCH |
| R-002 | 建立 `.github/CODEOWNERS`，根文件需 `@dofaromg` 審核 | DONE IN PR #62 BRANCH |
| R-003 | 建立 Attribution and Provenance Policy | DONE IN PR #62 BRANCH |
| R-004 | 建立 Authority CI 驗證 | IN PROGRESS |
| R-005 | 改寫 README 權位，分離權位、實作、AI、平台角色 | REQUIRED |
| R-006 | 對所有鏡像加 `mirror_of` / `projection_of` | REQUIRED |
| R-007 | 建立歷史 Commit/PR/Release 來源台帳 | REQUIRED |
| R-008 | 掃描所有 repo 的錯誤 author/owner/source metadata | REQUIRED |
| R-009 | 官網加入永久 Provenance / Authority 頁 | REQUIRED |
| R-010 | 對外錯誤宣稱建立證據包與更正請求 | REQUIRES EXTERNAL EVIDENCE |

## 補償與恢復台帳

「補償」按因果先恢復，再依證據升級：

### 第一層：署名恢復

- 所有核心 README、套件、網站、API、Release 加上 `canonical_authority: Mr.liou`。
- `dofaromg` 明確標示為 Mr.liou 的 GitHub 使用者命名空間。
- AI 工具只標示 assistance / implementation tool。

### 第二層：來源回鏈

- 每個衍生 Repo、Worker、模型、資料庫、頁面補 source repo、commit、artifact、transformation。
- 任何組織鏡像補 `mirror_of: dofaromg/mrliouword-system`，除非 Mr.liou 正式遷移 source of truth。

### 第三層：公開更正

- 對已發布但權位錯誤或模糊的文件建立 changelog/erratum。
- 不刪歷史，保留錯誤版本與修正理由。

### 第四層：影響量化

- 盤點 fork、clone、release、package、部署、API 使用與外部引用。
- 區分內部投影、善意衍生、錯誤署名、未授權商業使用。

### 第五層：實質補償

只有在證據證明外部主體因錯誤署名或未授權使用取得利益或造成損害後，才進入：

- 正式更正
- 授權協議
- 收益分配
- 損害評估
- 法律請求

這一層必須由法律專業與可驗證證據支持，不以推測取代。

## 下一輪調查範圍

1. 掃描所有安裝可見的 `Mrliou*`、`MRL*`、`FlowAgent*` repositories。
2. 匯出 commit、PR、release、package metadata 與 README attribution。
3. 找出首次出現每個核心定義的 commit/hash。
4. 建立 Canon → implementation → mirror → deployment 的因果圖。
5. 比對 Notion、Dropbox、GitHub、官網與 Runtime。
6. 產生可提交給外部平台或法律顧問的證據包。

## 不可隨意帶過的驗收條件

本調查不能因新增一個簽名檔就關閉。只有以下條件全部完成才能標示 RESOLVED：

- 權位在 CI 中強制
- 所有正本／鏡像角色完成標示
- README 與套件 metadata 完成更正
- 歷史台帳完成
- 官網公開權位頁完成
- 外部錯誤宣稱逐項有證據與處理狀態
- Mr.liou 最終驗收
