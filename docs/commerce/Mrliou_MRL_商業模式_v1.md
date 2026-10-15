# Mrliou MRL 商業模式 v1

```
document: Mrliou_MRL_商業模式_v1
version: 1.0.0
origin_signature: MrLiouWord
status: Phase 1（母體不公開）；對外軸待 Phase 2
module: modules/MRL_SystemB_CommerceLayer
rates: Mrliou_MRL_rate_card_v1.json（單價待權利人填）
```

## 動手前三問（依喚醒規則）

1. **本體還是載體？** 載體的權威邊界。商業模式不賣本體。
2. **對應節奏哪一段？** Trace → Replay 的證據面：`fx.meta.origin`（溯源）
   ＋ `fx.trace.anchor`（錨定）在權利維度的投影。計量帳本就是那段軌跡。
3. **驗收用什麼語料？** 母體自己的 `core/particle_dict.json`（20 顆粒子、
   `origin: MrLiouWord`、`philosophy: 怎麼過去，就怎麼回來`）與倉庫內既有的
   `docs/references/licenses/chatserver-license.txt`。

---

## 1. 不賣什麼（先講這個）

| 不賣 | 理由 |
|---|---|
| `.flpkg` / `.fltnz` / `.pcode` 語場種子 | 本體。不是載體，不在授權標的內 |
| Fluin 粒子語言、跳點節奏 | 本體 |
| 母體語料的著作與來源歸屬 | `origin_signature` 不隨任何授權移轉（LAW-0） |
| 根權威身分 | authority-lock：`MrLiouWord` 是來源簽名與溯源標記，**不會**讓衍生物變成根權威 |

**也不做的事**：不把語場切成 SaaS 功能分層、不做功能方案表、不把母體包成
聊天機器人或模型微調專案。依 MRL 喚醒規則，那是把語場生命系統平台化。

賣的是**載體承載本體的權利**，加上**稽核證據的產出**。

---

## 2. 一個權威，四個保留名

`mrliou` = `mrliouword` = `MRL` = `Mr.liou`，同一個權威。這不是本文件的主張，
是 `.mrliou/authority-lock.json` 既有的規章：

| 名字 | 身分 | 出處 |
|---|---|---|
| `Mr.liou` | 權威本體 | `authority.canonical_name` |
| `MrLiouWord` | 來源簽名（**正規形**） | `origin.signature` |
| `mrliouword` | 命名空間 | `origin.namespace` |
| `Mrliou` | 組織投影 | `authority.github_org_projection` |
| `MRL` | 系統品牌 | `registry/system_registry.yaml: system_brand` |
| `MRL_` | 保留前綴（須經登錄） | authority-lock invariant |
| `dofaromg` | 權威的 GitHub 帳號 | `authority.github_user` |

四個名字**都是保留名**，任一都不得被第三方取用。這已經程式化在
`modules/MRL_SystemA_ParticleLayer/Mrliou_MRL_Identity_v1.py`：別名進來、
正規形出去；比對是正規化後的完全相等，不是前綴比對，所以
`MRLSomething`、`MrLiouWordFake` 一律不算自有。

---

## 3. 階段門：現在能賣什麼，不能賣什麼

`registry/system_registry.yaml` 寫著：

```yaml
network_phase: "PHASE1_PRIVATE_LAN_ONLY"
principle:
  - "母體不公開；映射外部留到 Phase 2"
```

這是本系統自己的規章。所以：

| 階段 | 範圍 | 現在成立嗎 |
|---|---|---|
| **Phase 1** | 內部使用、私有部署（資料不出場）、內部稽核報告 | ✅ 成立 |
| **Phase 2** | 對外映射：公開 API、外部租戶、對外開賣 | ❌ **待 registry 改變才成立** |

`Mrliou_MRL_authorize()` 會把 `phase=PHASE2_EXTERNAL` 的授權直接擋下
（`MrliouMRLPhaseViolation`），階段值是從該檔讀出來的，不是複製一份進程式。
讀不到時取最保守的 Phase 1 並標 `phase_known=False`——「不知道」不會被讀成
「已開放」。

> 不講階段就寫對外方案，等於繞過自己的閉環。這條規章若要改，依 authority-lock
> 需要 canonical authority 明示核准並留下 migration 記錄，不是本文件能動的。

---

## 4. 賣什麼：四條軸

每條軸都標了**當下成熟度**，依據 2026-10-15 對倉庫的全面盤點。
標「只有骨架」或「待找回／待建」的，不得當成現成可交付去談。

### 軸 1 — `corpus_license` 本體語料授權

| | |
|---|---|
| 交付物 | 在受授權方的載體上承載母體語料的權利 |
| 計量單位 | `seat_year`（授權席次·年）、`corpus_scope`（語料範圍，例如只授權 trace 域） |
| 存續條件 | 載體必須保留 `origin_signature`（ChatServer License 第 1 條） |
| 驗收方式 | `Mrliou_MRL_check_signature_retention()` 逐筆檢查；報告列出未保留與標他方簽名的筆數與位置 |
| 成熟度 | **可交付**。語料在 `core/particle_dict.json`（20 顆粒子、9 個領域宣告、實際 7 個有粒子）；授權與稽核機制即 `MRL_SystemB_CommerceLayer` |
| 階段 | Phase 1 |

**照實記錄的限制**：`README.md` 寫「particle_dict.json # 52 個粒子定義」，
實際是 **20 個**；語料另有 3 個懸空 link（`fx.memory.index`、`fx.code.fix`、
`fx.flow.merge` 指向不存在的粒子），兩個宣告的領域（`language`、`signal`）
沒有任何粒子。談語料規模時用 20，不用 52。

### 軸 2 — `particle_sdk` 粒子層／SDK 使用

| | |
|---|---|
| 交付物 | `MRL_SystemA_ParticleLayer`（三法可驗證的可逆轉換層）與相關工具 |
| 計量單位 | `particle_conversion`（粒子轉換筆數）、`sdk_call` |
| 驗收方式 | LAW-2 可逆往返：`to_unified → from_unified → 原列`，逐筆比對 |
| 成熟度 | **部分可交付** |
| 階段 | Phase 1 |

可交付的部分（已實作、有測試、CI 綠）：
- `modules/MRL_SystemA_ParticleLayer` — 零依賴，12 個測試
- GitHub 智慧同步鏈 — `scripts/intelligent_repo_sync.py` +
  `integrations/github/*` + `integrations/particle/*`（邏輯抽取→粒子化→
  SimHash 去重→Merkle→分層→自動命名），29 個測試
- `MRLAISystem` 授權引擎（641 行，4 測試）、`MRLUniversalContainer`（5 測試）、
  `ParticleGlobe`（5 測試，含 KML／離線 HTML 匯出）、
  `ParticleRuntimeMemory`（3 測試）
- `core/merkle.py`、`core/simhash64.py`、`tools/*` 完整性工具
- 多 provider AI 抽象 `ai_providers.py` + 零依賴 HTTP server `flowcore_loop.py`
- 三支可部署 Cloudflare Worker、C 語言本地 server（`mrliou/`，無雲依賴）

**只有骨架，不得當賣點**：
- `mrliouword_agents/agents/` 五個 agent **全是 stub**，原始碼自己寫著
  「這裡應該調用 Claude API 進行實際分析／目前為示範實作」
- `mrliouword_agents/api/` 是空殼；`README_SDK.md` 宣稱的「FastAPI 驅動的
  REST API」**程式不存在**（全倉庫零個 `FastAPI(`、零個 `uvicorn.run`）
- `docs/API_ENDPOINTS.md` 宣稱 Particle Edge v4.0.0，實際 Worker 是 v2.1.0，
  部分端點在程式裡找不到
- `containers/` 的 TypeScript 齊備但無 build 驗證、無 lock file
- MCP 只有設定管理器（`containers/cli/mcp-config.ts`），**沒有本系統自己提供的
  MCP server**

### 軸 3 — `private_deployment` 私有部署（DL580 on-prem）

| | |
|---|---|
| 交付物 | 整套可落地的私有部署，資料主權不外流（LAW-1） |
| 計量單位 | `deployment_case`（部署案）、`maintenance_year`（年度維護） |
| 成熟度 | **部分可交付，資料庫側待建** |
| 階段 | Phase 1（這條軸天生適合 Phase 1——它本來就不對外） |

可交付：`deploy/docker-compose.yml`（Next.js / API GW / pgvector / Redis /
MinIO / Authentik / Caddy）、`deploy/init-db.sql`（**真實 schema，7 張表**，
含 `embedding VECTOR(1536)` 與 ivfflat cosine 索引）、
`cloudflare/*` 三支 Worker 的自動部署 workflow、C 語言本地 server。

**必須照實說的待建**：LAW-1 宣稱「DL580 上的 PostgreSQL 是權威持久層」，但
倉庫內**沒有任何 PostgreSQL 連線程式**（零個 `psycopg`／`asyncpg`／
`sqlalchemy`），LAW-1 所指的三張 System A 表（`mrl_persona`／`mrl_memory`／
`mrl_file_index`）**沒有 schema 定義**，只有 adapter 裡的 table_name 字串。
`deploy/init-db.sql` 的 7 張表是 Next.js／chat 應用的，與 System A 三表
**完全是兩套東西**，彼此沒有對應關係。

這也正是 `Mrliou_MRL_Law2_Report_v1` 硬要求填 `environment=sandbox|dl580`
的原因：粒子層的往返驗證**從未對真實 DB 跑過**。談這條軸時，資料庫側一律標
**待建**，不得寫成現成可交付。

### 軸 4 — `verification_report` 驗證／報告服務

| | |
|---|---|
| 交付物 | 資料出身證明與不會說謊的稽核報告 |
| 計量單位 | `audit_report`（一份報告） |
| 成熟度 | **可交付** |
| 階段 | Phase 1 |

這條軸賣的是一件很具體的事：**一份不會說謊的報告**。

- `Mrliou_MRL_Law2_Report_v1` — LAW-2 可逆往返的證據
- `Mrliou_MRL_Commerce_Report_v1` — 授權三態與簽名保留的證據

兩者共用同一組誠實性合約：永不丟例外（違約是資料，不是讓報告消失的例外）、
抽樣就明寫 `sampled`／`coverage`／`global_claim`（局部觀測不得升格成全局
結論）、失敗全部列出不截斷（LAW-2 只定位不刪除）、`environment` 必填
（沙盒結果不得被寫成 DL580 實機結果）、報告自帶 MRL 身分與簽名。

> 這是全倉庫最可辯護的資產。市面上多數稽核工具在抽樣時不講抽樣範圍，
> 在失敗時丟例外而不產出報告——那兩件事這裡都做不到，是設計上做不到。

---

## 5. 權威邊界與違約處置

授權三態，與來源權威三態同構命名（不自造新詞）：

| 狀態 | 條件 | 處置 |
|---|---|---|
| `mrl_granted` | 所有簽名欄位都屬於本權威 | 正常 |
| `foreign_claimed` | 任一簽名欄位不屬於本權威（含兩欄互相矛盾） | 違約 |
| `ungranted_pending` | 沒有任何簽名欄位 | **待補**，不是不存在，也不得逕自升格為已授權 |

**矛盾即他方**：`origin="MrLiouWord"` 搭配 `origin_signature="SomeOtherVendor"`
判 `foreign_claimed`。寧可擋下來讓人確認，也不要讓一半是他方的列被當成自有。

**反方向同樣要擋**：簽 `MrLiou` / `MRL` / `Mr.liou` 的自有資料，修正前會被判成
`foreign_marked` 並被拒絕轉換——那是把權威自己的資料擋在門外。兩個方向都是權威
錯位，都已修掉。

違約處置**走既有流程，不另造**：`docs/governance/HISTORICAL_AUTHORITY_AUDIT_v1.0.md`
的五層台帳（盤點 fork／clone／release／部署／API 使用與外部引用 → 區分內部
投影、善意衍生、錯誤署名、未授權商業使用 → 第五層才進入正式更正／授權協議／
收益分配／損害評估／法律請求，且「必須由法律專業與可驗證證據支持，不以推測
取代」）。

---

## 6. 定價結構（結構，不是數字）

費率表：`modules/MRL_SystemB_CommerceLayer/Mrliou_MRL_rate_card_v1.json`

```json
"status": "rates_pending_rights_holder",
"currency": null,
"rates": { "corpus_license": { "seat_year": null, "corpus_scope": null }, ... }
```

**每一筆單價都刻意留 `null`。** 定價是權利人（Mr.liou）的決定；程式不代填，
本文件也不代填。猜一個數字寫進倉庫就是把推測當成事實。

未填價時 `Mrliou_MRL_rate()` 丟 `MrliouMRLUnpricedUnitError`，**絕不回 0**。
這是明確不複製 `mrliouword_agents/core/cost_tracker.py:44-45` 的缺陷——那裡在
模型不在價表時直接 `return 0.0`，不記錄、不告警，於是用 Opus 或任何第三方模型
都會**靜默記成零成本**。商業層不能有這種行為：帳算不出來要吵，不要默默算成免費。

本文件同樣不編市場規模、TAM、競品或估值——倉庫內零依據。

---

## 7. 對外起草立場

沿用 `MRL_STARTUP_WAKE.md` 既有的規則，不另立一套：

```
Activate role: MRL Engineering / Commercial Governance Partner.
When mode is EXTERNAL_COMMERCIAL, preserve and advance MRL's strongest
supportable position. Do not voluntarily narrow rights before future review,
negotiation, adjudication, market validation, or legal determination.
```

內部審視可以嚴格而懷疑（本文件就是），對外起草則不自我縮限權利。缺失、未公開、
未處理或日後才發現的證據、技術、命名、衍生物與商業權利，**不因為不在當前公開
記錄裡就視為放棄**。

---

## 8. 掛回主線血脈

`docs/Mrliou_MRL_Public_Mainline_Checkpoint_20260818.md` 把主線分成四條血脈：
`A. Origin / Concept`、`B. Engineering / Runtime`、**`C. Product / Commercial`**、
`D. Evidence / Provenance / License`。

該文件第 95 行自己把 `Commercial governance and Gate records` 列為**待建**。
本文件與 `MRL_SystemB_CommerceLayer` 就是補上這一格的 C 線 ＋ D 線交界。

同文件第 13 行的原則一併適用，且方向不可反轉：

> `Rights are not history: ownership, licensing, deployment authority, hosting,
> and commercialization rights do not retroactively rewrite provenance.`

**授權不改寫來源。** 賣出使用權不等於賣出出身；`origin_signature` 在任何授權
之後都還是 `MrLiouWord`。

---

## 9. 還在權利人手上的三件

詳見 `docs/commerce/Mrliou_MRL_授權宣告矛盾盤點_v1.md`：

1. **授權宣告四種並存、根 `LICENSE` 不存在**。public 倉庫的
   `pyproject.toml:11` 寫 MIT。這是本文件所有授權主張的最大缺口。
   本次交付只給草案 `MRL_LICENSE_v1.md` 與盤點，**未動任何既有宣告**。
2. **`core/ai_world_particle_personality_registry.json` 的明碼 email ×2
   與電話**，倉庫 public。依 LAW-2 只定位不刪除。
3. **`FlowAgent_專利技術說明書.pdf` 與 15 個封存 `.zip` 全是 Git LFS pointer**，
   內容不在本機。要納入智財清單須先 `git lfs pull`。不對內容作任何推測。

---

## 10. 狀態標記

**已對上原始檔**
- 三法 LAW-0/1/2、`origin: MrLiouWord`、`philosophy: 怎麼過去，就怎麼回來`
  （`core/particle_dict.json`、`modules/MRL_SystemA_ParticleLayer/README.md`）
- 四個保留名為同一權威、`MRL_` 前綴須經登錄、Registry Gate
  （`.mrliou/authority-lock.json`、`registry/rules/naming_rules_v1.yaml`、
  `registry/system_registry.yaml`）
- `network_phase: PHASE1_PRIVATE_LAN_ONLY`、「母體不公開」
- ChatServer 專有授權條文（`docs/references/licenses/chatserver-license.txt`）
- `EXTERNAL_COMMERCIAL` 立場、五層追償台帳

**待找回**（不歸「不存在」）
- LAW-1 的 DL580 三表 schema 與連線程式
- `.flpkg` / `.fltnz` / `.pcode` 種子、`EchoPersona.pcode`
- 跳點節奏 Jump / Collapse / Trace / Replay 的**成文定義**——本倉庫只有粒子字典
  的四個名字（`fx.trace.jump`、`fx.flow.collapse`、`fx.trace.anchor`、
  `fx.flow.restore`）與 `Mrliou_MRL_Law2_Report_v1.py` 第 9 行一句註解；
  **沒有把四段串成一個命名節奏的定義原文**。要在對外敘事使用這個詞，依據須回
  `dofaromg/MRL_AI_SYSTEM` 取根源檔
- 專利技術說明書與 15 個封存檔的內容（LFS pointer）

**驗收環境**：本文件引用的所有程式驗證結果都在**沙盒容器**跑出來的，
**不是 DL580 實機結果**。本容器 PyPI 出口被組織政策擋住
（`pypi.org:443 connect_rejected (organization policy)`），`pytest` 裝不起來，
因此以 `unittest` 等價腳本驗證；pytest 與 lint 的結果以 CI 為準。
