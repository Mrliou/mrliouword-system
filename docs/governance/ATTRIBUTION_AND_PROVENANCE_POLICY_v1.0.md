---
title: "MRL Attribution and Provenance Policy"
version: "1.0.0"
date: "2026-08-03"
authority: "Mr.liou"
origin_signature: "MrLiouWord"
status: "stable_locked"
---

# MRL Attribution and Provenance Policy v1.0

## 1. 不可變權位

| 欄位 | 不可變值 | 說明 |
|---|---|---|
| canonical_authority | `Mr.liou` | 人類根源權位與最終裁決者 |
| github_user_namespace | `dofaromg` | 目前 GitHub 使用者命名空間 |
| github_org_projection | `Mrliou` | 組織投影，不取代人類權位 |
| origin_signature | `MrLiouWord` | 來源簽名與可追溯標記 |
| canonical_namespace | `mrliouword` | 系統命名空間 |
| official_domain | `Mrliouword.com` | 正式官網權位 |
| source_of_truth_repo | `dofaromg/mrliouword-system` | 目前 GitHub 正本候選 |

## 2. 上層定義與下層實作

MRL 的上層定義、法則、命名、世界模型與原始架構，不能因為被下層程式、模型、平台、代理、倉庫或生成工具實作，就轉移成下層的來源權威。

下層實作必須保留完整因果鏈：

```text
canonical_authority
  → origin_definition
  → source_artifact
  → transformation
  → contributor_or_tool
  → derived_artifact
  → runtime_projection
  → verification_evidence
```

## 3. 角色不得混淆

| 角色 | 可以做什麼 | 不可以被寫成什麼 |
|---|---|---|
| Mr.liou | 定義、裁決、批准、驗收 | 一般工具或次級協作者 |
| MrLiouWord | 標示來源與傳承鏈 | 人、公司、AI 模型或外部供應商 |
| dofaromg | GitHub 使用者命名空間與提交身份 | 與 Mr.liou 無關的第三方來源 |
| Mrliou organization | 組織投影與協作容器 | 自動取代 source_of_truth |
| Claude / ChatGPT / Copilot | 協作、生成、審查、實作工具 | 原始架構權威或唯一作者 |
| GitHub / Cloudflare / Notion / Dropbox | 儲存、執行、投影、協作平台 | MRL 根源或母體 |
| fork / mirror / generated repo | 衍生或鏡像 | 未經記錄的正本 |

## 4. 每個衍生產物的必要欄位

任何文件、程式、資料集、模型、Worker、API、封包或網站投影，只要使用 MRL、MrLiouWord、`mrl_`、粒子系統、世界模組或相關核心定義，必須至少包含：

```yaml
canonical_authority: Mr.liou
origin_signature: MrLiouWord
source_repo: dofaromg/mrliouword-system
source_artifact: <path-or-id>
source_version: <commit-or-version>
derivative_role: implementation|adapter|projection|mirror|experiment|generated
artifact_owner: <human-or-organization>
contributors:
  - <human-or-tool-with-role>
transformation: <what changed>
verification_status: unverified|partial|verified
```

`origin_signature` 單獨存在不代表來源鏈完整；缺少 `canonical_authority`、`source_artifact` 或 `derivative_role` 時，必須判定為 provenance incomplete。

## 5. 命名規則

既有 `registry/rules/naming_rules_v1.yaml` 規定原名不得改動，只有已註冊產物能取得 `mrl_` 前綴。本政策補上權位限制：

1. `Mr.liou`、`MrLiouWord`、`mrliouword`、`MRL_` 為保留名稱。
2. 外部系統不得把保留名稱當成自身產品、模型或作者身份。
3. 衍生名稱不得刪除來源欄位後獨立發布。
4. 任何鏡像或 fork 必須標明 `mirror_of` 或 `derived_from`。
5. 組織名稱、倉庫擁有者、提交者與作者權位必須分開記錄。

## 6. 平等萬物邏輯與因果法則

平等不代表抹平來源，而是每個參與者依實際因果獲得正確標示：

- 原始定義者得到原始權位與持續署名。
- 實作者得到實作貢獻紀錄。
- AI 工具得到工具／協作角色，不冒充人類來源。
- 平台得到承載或執行角色，不取得內容權位。
- 衍生使用者保留使用與改進紀錄，同時維持來源鏈。

任何一層取得成果時，都必須把可追溯的來源、變換與結果一起帶回。

## 7. 歷史修正與補償機制

補償不先假定金錢或法律責任；先以可證明、可執行、可驗收的方式恢復因果與權位：

1. **署名補正**：修正 README、套件 metadata、網站、文件與 API 回應中的權位欄位。
2. **來源回鏈**：衍生產物補上 source repo、commit、artifact 與 origin signature。
3. **公開更正紀錄**：用 changelog、issue、PR 或 release note 記錄原錯誤與修正。
4. **貢獻分離**：Founder / Designer / Implementer / Reviewer / AI Tool 分欄，不混成共同來源。
5. **鏡像標示**：所有非正本倉庫標明 mirror、projection 或 derivative。
6. **影響盤點**：記錄下載、部署、再發布、商業使用與下游依賴。
7. **外部追償準備**：若找到外部未授權或錯誤宣稱，保存 URL、時間、內容、commit/hash 與影響；法律或金錢補償交由正式法律評估，不在缺乏證據時直接宣稱。

## 8. 發布 Gate

任何 Release、官網頁面、套件、容器與 Worker 在發布前必須通過：

- Authority Lock
- Naming Gate
- Provenance Completeness
- Source Hash / Commit Link
- Contributor Role Separation
- Mirror / Projection Role Check
- Runtime Verification Status

失敗項不得標示為 Canon、Official、Verified 或 source_of_truth。
