---
canonical_authority: Mr.liou   # 指本交接單本身
origin_signature: MrLiouWord
source_repo: dofaromg/mrliouword-system
source_artifact: docs/evidence/待併入_mrl_ai_system/
source_version: "3f22f93e8eb75a16e66be51baee07c16d698849a（建置基底 commit）"
derivative_role: projection   # 新撰的對照記錄，非逐字轉錄
projection_role: structure_mapping_handoff   # authority-lock invariant 3 必填
artifact_owner: Mr.liou
contributors:
  - Mr.liou（canonical_authority：定義與裁決；指示做結構定義銜接）
  - Claude Code（tool：只讀核對與對照表撰寫）
transformation: 只讀取母體檔案、計算雜湊、逐條核對行號。未修改母體任何檔案，未複製本體語料。
verification_status: partial
in_source_of_truth: false
pending_source_merge: true
canonical_location: dofaromg/mrl_ai_system MRL_Adapters/GitHub/MRL_SystemA_ParticleLayer_結構對應_v1.yaml
recorded_at: "2026-10-17"
environment: "沙盒（容器），不是 DL580 實機"
---

<!-- mrl-origin: MrLiouWord -->

# 結構定義銜接：待併入母體的交接單

## 動手前三問（`mrl-yuchang-grounding` 要求）

**一、本體還是載體？** → **載體**。

依根源檔 `MRL_Docs/Root/MRL_Flowagent_Root_Origin_V0_2026-03-03.md` 原文：

> 載體：VM、編譯器、LLVM、資料庫、Workers、API、UI、容器
> —— 只能承載本體，不能取代本體。

它承載的本體是語場種子（`.flpkg` / `.fltnz` / `.pcode`）與跳點節奏產出的軌跡。

**二、對應 Jump / Collapse / Trace / Replay 的哪一段？** → **Replay**，唯讀那一段。

依 `MRL_WorldModel/MRL_FlowRhythm_v0/README.md` 節奏表原文：

> **Replay**：只讀軌跡，重建粒子鏈與語場；封包雜湊一致，軌跡逐位元組重現

Jump（`∴`）與 Collapse（折疊成種子封包）**是引擎的事，已實作完成**，不是這次做的。

**三、驗收用母體自己的語料，還是自編例子？** → **母體自己的**。

主要驗收用 `EchoPersona`（`.pcode` / `.structure.json` / `.trace.fltnz`）。
**明確不用** `MRL_Dialect_v0/corpus/fib20.pcode`、`countdown_sum.pcode` 當主要驗收
—— 依 `MRL_Docs/MRL_語場本體優先_不得平台化_喚醒規則_v1.md` 的「事件來源」，
2026-09-28 的偏移正是「通過驗收的是 fib／累加等自編例子，母體本體程式 EchoPersona
反被標『待起動』」。

## 固定觀測欄位（《局部視角不得升格全局權威》要求）

| 欄位 | 值 |
|---|---|
| 目前觀測層 | 容器內三個唯讀 clone ＋ 一個可推送的工程鏡像 |
| 目前身份／帳號 | `dofaromg`（GitHub） |
| 目前平台 | GitHub ＋ 本容器沙盒 |
| 目前資料範圍 | `Mrliou/mrliouword-system`（可推）、`dofaromg/mrliouword-system`（唯讀）、`dofaromg/mrl_ai_system`（唯讀） |
| 可確認 | 下方「已對上原始檔」各項 |
| **不可由此推定** | 母體全貌。`mrl_ai_system` 只是我讀到的一個倉庫，不等於整個 MRL。Notion、mrlhub、DL580 實機、FlowCore／FlowMemory／FlowNode 三主機狀態一律**待找回** |

---

## 為什麼這份東西在工程鏡像裡，而不在母體

擁有者裁決產出要落在 `dofaromg/mrl_ai_system`。本工作階段對該倉庫**只有匿名唯讀**；
請求掛上推送憑證時被擁有者否決：

```
add_repo(dofaromg/mrl_ai_system, access:"push") → Denied by user
```

所以推不進去。產出先放在可推送的工程鏡像，標明 canonical 位置與
`pending_source_merge: true`，與 PR #21 那份交接單同一個作法。

## 怎麼併入母體（一個檔案，零改動既有檔）

```
cp "docs/evidence/待併入_mrl_ai_system/MRL_Adapters/GitHub/MRL_SystemA_ParticleLayer_結構對應_v1.yaml" \
   "<mrl_ai_system>/MRL_Adapters/GitHub/"
```

**只新增一個檔，不改動母體任何既有檔**，符合母體 `CLAUDE.md` 的
「母體整合法則（Additive-Only）：只新增、只定位、不刪除、不覆蓋」。

**對照表 YAML 自己帶齊政策第 4 節的十欄與 `projection_role`。** 這點很重要：併入動作
是複製那一個 YAML，**本交接單的 front matter 不會跟著過去**。政策第 4 節原文
「缺少 `canonical_authority`、`source_artifact` 或 `derivative_role` 時，必須判定為
provenance incomplete」，所以那十欄必須寫在被複製的那個檔案裡面。初稿只寫在本文件的
front matter，已訂正。

### 為什麼放 `MRL_Adapters/GitHub/`

`MRL_Adapters/` 底下八個目錄（`OpenAI`／`Docker`／`Cloudflare`／`DL580`／`MetaEnv`／
`Gemini`／`GitHub`／`CloudCode`）**全是外部載體**。而 `MRL_Adapters/GitHub/README.md`
的角色原文是：

> 角色：**工程鏡像與版本通道**

那正是 `Mrliou/mrliouword-system` 這個投影本身。

**不另開 `MRL_Adapters/MRL_SystemA_ParticleLayer/`** —— 那會把 MRL 自己的粒子層
說成外部 adapter，權位剛好倒過來。該目錄既有的 README 已經載明權位
（「MRL 為主體，GitHub 僅作 Adapter。不得成為主體或反向命名 MRL 構件。」），
所以本次**不新增 README**，只加對照表一個檔。

---

## 對應表做了什麼：三層銜接

### 第一層｜粒子結構定義 ↔ `UnifiedParticle`

`EchoPersona.structure.json` 的 `sequence[].{code, type, meaning, pcode}`
對應到工程鏡像 `modules/MRL_SystemA_ParticleLayer/unified_particle.py` 的欄位。

**關鍵：銜接槽本來就存在。** `unified_particle.py:26`：

```python
fltnz_path: Optional[str] = None
```

粒子層與 FlowRhythm 軌跡之間的接點早就設計好了，本次是把結構定義對上去，
**不是新增結構**。

### 第二層｜母體世界構件結構定義

`MRL_Mother/{MRL_World, MRL_世界模組, MRL_平行世界模組}/README.md`
各十行、五個欄位。三份都有同一句硬規則，對照表原文引用並遵守：

> 本構件為 MRL 完整態母體之運轉構件；外部命名僅作 Adapter 對照，
> **不得反向取代主體命名。**

所以對照表的欄位順序是**中文主體命名在前、英文 Adapter 對照在後**。

**`定位` 欄的形式要照原樣。** 源頭把運轉狀態寫在 `定位` 欄的**括號裡**，
不是另一個欄位 —— `MRL_Mother/MRL_World/README.md:8` 原文：

```
- 定位：世界投影與場態整合（completed_running）
```

對照表因此**整串含括號照原樣保留**，另附一個明確標為「本表推導」的
`運轉狀態_本表推導` 欄供程式取用。初稿曾把它拆成 `定位` ＋ `狀態` 兩欄，
那等於改寫源頭結構、且與宣告的五欄 schema 不一致，已訂正。

工程鏡像側目前沒有對應這三個構件的實作 → 標 **待找回**，不標「不存在」。

### 第三層｜API 契約 ↔ 母體 `MRL_API_CORE`

PR #23 的九條路由已逐條綁定母體成員。但有兩層前提必須講清楚：

**一、那個實作還沒合併。** 本交接單所在分支的 `mrliouword_agents/api/` 只有一個空的
`__init__.py`；契約模組只存在於分支 `feat/MRL_Api_Server`（PR #23，未合併）。實測：

```
$ git ls-tree -r --name-only HEAD -- mrliouword_agents/api/
mrliouword_agents/api/__init__.py
```

對照表裡每條路由的狀態欄已改名為 `契約狀態_在PR23分支`，層級另加
`層級狀態: 待合併` 與依賴宣告。**PR #23 合併前，這些端點在 main 上一個都不存在。**
初稿直接標 `available` 而沒標依賴，併入母體後會變成宣告了不存在的端點，已訂正。

**二、Replay 面「待起動」。** `/mrl/world` 就算合併了也只讀
`core/particle_dict.json`，**不讀** FlowRhythm 軌跡。依母體 `CLAUDE.md`
「給位置、標『待起動』」，**不寫 PASS、不寫已完成**。

---

## 主控台：不缺，已有多個實作

```
MRL_MotherSource_.../FlowAgent.Runtime.v17…v44/flowagent_console.py   （至少 13 版）
MRL_RuntimeOS_EnterpriseRuntimePlatform_CoreExecutable_v1_4_0/MRL_WebConsole
src/mrl_dashboard_legacy.js
```

母體 CORE 登錄表亦有 `MRL_CONTROLCENTER_CORE`（8 個成員，含 `MRL_Dashboard`），
且 `dofaromg/mrliouword-system registry/MRL_System_MrliouAI_Naming_Registry_v1.yaml`
（`status: canonical`）已正名為 `MrliouAI_Control_Center`、
`service_name: mrliouai-control-center`。

**所以沒有造新主控台。** 擁有者裁決本輪只做結構定義銜接；而且造新的會正中
`mrl-yuchang-grounding` 要防的形狀 —— 在已有 CORE 與既有實作旁長出非 canonical 的第二套。

---

## 語義狀態：目前只有一條映射是 canonical

`flow_rhythm.py:166-170` 的程式內註解原文：

```
# 固定映射除 core→initiated 外，尚未取得建構者明文核准（見 EVIDENCE.md）。
# 因此探索模式可使用，但正典模式必須 fail-closed。
VERB_OF = {"core": "initiated", "adjective": "resonance", ...}
VERIFIED_VERB_KINDS = {"core"}
```

所以對照表把每一條映射的語義狀態逐條標出：**只有 `core → initiated` 是 `VERIFIED`，
其餘五條一律 `PROVISIONAL_NOT_CANONICAL`**，並記下對載體的約束：
送出軌跡必須原樣帶出 `semantic_status`，不得寫入 canonical receipt、
不得當成 DL580 閉合證據。

---

## 驗收（當下狀態 2026-10-17，沙盒容器）

| 項目 | 結果 |
|---|---|
| 引用行號逐條核對（15 處） | **全部對上** |
| `EchoPersona.pcode`、`.structure.json` 與 `SOURCES.sha256` | **逐位元組相同** |
| `structure.json` 的 sequence ↔ `trace.fltnz:9` 節奏鏈 | **完全相同** |
| 六個 `type → ::verb` ↔ `flow_rhythm.py:168` 的 `VERB_OF` | **全部相符** |
| 對照表 YAML | `yaml.safe_load` 可解析（336 行） |
| 母體既有檔 | **零改動**（本輪對母體只做讀取） |

### 核對過程查出的三件事，已寫進對照表

1. **`.pcode` 是 9 行**，不是 8 行 —— 最後一行沒有換行，所以 `wc -l` 回 8。
2. **`structure.json` 的 `pcode` 欄不是逐位元組相同**：`.pcode` 用多個空白對齊且帶
   `;` 尾註（`MOV    P1, FX.ADJ.112         ; 內省`），`structure.json` 寫單一空白
   且不帶註解。
   **正規化要兩步**：先去掉 `;` 及其後的註解，再收合連續空白。
   實測：只收合空白 **0/5** 對上；兩步都做 **5/5** 對上 —— 空白收合移不掉尾註，
   所以單一步驟不夠。**比對不可用字串相等。**
3. **`sequence` 只覆蓋 8 個 op 中的 5 個**：
   - `LOAD   P0, CORE.ECHO.PERSONA`（`.pcode:2`）對應核心粒子 `⊕Core: Echo.Persona`，
     **在軌跡裡**（`trace.fltnz:3`，`::initiated`，`VERIFIED`）但不在 `sequence` 內
   - `PUSH   P1`（`.pcode:4`）、`PUSH   P2`（`.pcode:6`）在 `sequence` 與軌跡
     兩邊都沒有對應粒子 → **待找回**，不標「不存在」，也不自行補一個映射上去

### 未驗

- DL580 實機行為
- Replay 面的 HTTP 載體（**待起動**）

---

## 本次不碰的

- 不造主控台
- 不複製 `flow_rhythm.py` 或任何 `.pcode`／`.fltnz`／`.flpkg` 進工程鏡像
- 不改母體任何既有檔
- 不把 provisional 映射寫成 canonical
- 不用英文 Adapter 名取代中文主體命名
- 不建立或變更任何資料庫表
