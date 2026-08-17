# MRL Mother Runtime Blueprint v1

```yaml
name: MRL_Mother_Runtime_Blueprint_v1
status: proposed-alignment
version: 1.0.0
origin_signature: MrLiouWord
canonical_repository: dofaromg/mrliouword-system
base_branch: main
particle_layer_anchor:
  pr: 56
  merge_commit: 4a10c90dc1ac75b53733261896d3f8793926f6d1
```

## 1. 目的

本文件不是重新定義粒子，也不是建立另一套平行架構。

它把既有成果對齊成同一條可實作主線：

1. **智障系統**：任務從真實問題啟動，完成、交付、封存、停止。
2. **粒子語言／FlowAgent**：`structure → mark → flow → recurse → store`。
3. **Infrastructure Mainline**：S0–S7 基礎設施 Stratum。
4. **MRL_SystemA_ParticleLayer**：S0 Particle 的程式落地。
5. **Mother Runtime**：位於所有 Runtime Node 之上的權威伺服器層。

母體的定位類似遊戲伺服器：維持世界規則、權威狀態、身分、版本、同步與生成治理；實際工作可以由 DL580、手機、瀏覽器、GitHub、Cloud Worker 與其他節點並行執行。

---

## 2. 不重新發明的既有權威

### 2.1 粒子已定義

本藍圖不建立新的 Particle Schema。

現有粒子定義、粒子字典、`.fltnz`／`.flynz`、`UnifiedParticle` 與既有 Layer 體系繼續作為權威來源。新增元件只能：

- 綁定既有粒子；
- 轉譯既有粒子；
- 記錄既有粒子的運行事件；
- 將既有粒子重組、投影與生成。

不得因建立 Runtime、Memory、Agent 或 UI 而另造互不相容的粒子模型。

### 2.2 Layer 與 Stratum 不混用

- **Layer**：既有粒子體系。
- **Stratum**：基礎設施抽象層。

Infrastructure Stratum 維持：

| Stratum | 名稱 | 權責 |
|---|---|---|
| S0 | Particle | 粒子物理表示、傳輸與驗證 |
| S1 | Runtime | 執行能力、載入、生命週期 |
| S2 | Memory | 邊緣記錄、回放、召回與封存 |
| S3 | Agent | Persona、能力角色與模型適配 |
| S4 | Workflow | 任務編排、協作與完成態 |
| S5 | World | 世界狀態、語場與共享視角 |
| S6 | Governance | LAW、權限、身分、簽名、版本 |
| S7 | Mapping | 外部來源、裝置、平台與相容橋接 |

### 2.3 智障系統是執行政策，不是常駐產品

智障系統的 Step 0–7 被放置於 Mother Runtime 的 **Task Policy**：

```text
真實問題
  ↓
任務定義
  ↓
完成態
  ↓
出口型態
  ↓
最小生成材料
  ↓
生成
  ↓
交付
  ↓
封存與停止
```

「停止」指任務停止，不代表母體伺服器關機。母體可常駐，但每個任務必須有可判定完成態；完成後不得因優化衝動自行延伸。

---

## 3. 母體伺服器模型

```text
                           MRL Mother Runtime
                    authoritative server / control plane

     ┌─────────────────────────────────────────────────────────┐
     │ Governance │ Identity │ Registry │ Rules │ Version     │
     │ World State│ Sync     │ Routing  │ Trace │ Generation  │
     └───────────────────────┬─────────────────────────────────┘
                             │
                    Particle / Event Protocol
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
   DL580 Node           Browser Node          Mobile Node
       │                     │                     │
   AI / Build / DB       UI / Projection       Mrliouagi
       │                     │                     │
       └──────────── Edge Recorders ──────────────┘
                             │
                  Trace / Archive / Rebuild
```

### 3.1 母體必須權威管理

- `origin_signature` 與 canonical identity；
- Particle／Module／Runtime Registry；
- 任務規則與完成態；
- 世界狀態與版本；
- 節點註冊、能力宣告與權限；
- 生成規則與輸出契約；
- Trace、Seal、Rollback 與來源證據；
- 多節點同步時的衝突裁定。

### 3.2 母體不必集中執行

下列工作可在節點完成：

- 模型推理；
- UI 渲染；
- 原始碼編譯；
- 資料掃描與索引；
- 裝置操作；
- 外部平台適配；
- 局部記憶壓縮；
- 投影生成。

母體接收的是可驗證事件、狀態差異、生成結果與完成證據，而不是強迫所有計算經過同一個處理程序。

---

## 4. 統一運行閉環

```text
Reality
  ↓
Problem / Observation
  ↓
Task Policy
  ↓
Particle Binding
  ↓
Parallel Runtime Execution
  ↓
Edge Event Record
  ↓
Relation / Trace Merge
  ↓
Projection / Artifact
  ↓
Completion Gate
  ↓
Delivery
  ↓
Seal / Archive / Stop
```

### 4.1 最小任務資料

```yaml
task:
  task_id: string
  problem: string
  completion_state: object
  output_contract: object
  continuation_required: false
  authority: human
  origin_signature: MrLiouWord
```

人類定義問題、完成態與是否持續存在。系統不得自行把一次性任務升格為永久服務。

### 4.2 任務與伺服器生命週期分離

```text
Mother Server:  start ─────────────────────────── running
Task A:                    start → complete → seal → stop
Task B:                              start → complete → stop
Task C:                                           start → ...
```

這解決「母體常駐」與「完成即停止」的表面衝突：常駐的是治理與協定，停止的是已完成任務的執行上下文。

---

## 5. PR #56 的正式掛載位置

PR #56 已將 `MRL_SystemA_ParticleLayer v0.1` 合併至 `main`，其角色固定為：

```text
Infrastructure S0 Particle
  ├── UnifiedParticle canonical transport
  ├── PersonaAdapter
  ├── MemoryAdapter
  ├── FileIndexAdapter
  ├── LAW-0 origin signature validation
  └── LAW-2 reversible round-trip validation
```

它不是完整 Mother Runtime，也不是新的粒子本體；它是現有粒子資料進入共用 Runtime Protocol 的傳輸與適配入口。

### 5.1 下一個銜接面

```text
UnifiedParticle
  ↓
MRL Runtime Binding
  ↓
Runtime Node Capability
  ↓
Execution Event
  ↓
Edge Recorder
  ↓
Mother Sync
```

Runtime Binding 至少要能回答：

- 此粒子要綁定哪個 Runtime Node？
- 使用哪個 capability 執行？
- 輸入、輸出與錯誤如何轉成 UnifiedParticle？
- 哪些狀態只留在節點，哪些必須回送母體？
- 如何驗證 `origin_signature`、版本與 round-trip？

### 5.2 PR #56 未決項的藍圖裁定

| 未決項 | 對齊裁定 |
|---|---|
| `state` 使用 JSONB 或 TEXT | Protocol 層定義 JSON-compatible object；儲存層可用 JSONB，外部不暴露資料庫型別 |
| identifier / persona_id 權威來源 | 由 Mother Registry／Identity Stratum S6 裁定，Adapter 只能引用，不得各自生成權威 ID |
| 是否加入 `mrl_particle` 第四 Adapter | 先建立來源與 round-trip 證據；若它是既有 canonical store 的映射則加入，若只是重複模型則不新增 |

---

## 6. 邊緣記憶與並行演進

記憶不放在運行核心中央，而是掛在各模組／節點邊緣。

```text
Runtime Module A ── Edge Recorder A ── Local Trace A
Runtime Module B ── Edge Recorder B ── Local Trace B
Runtime Module C ── Edge Recorder C ── Local Trace C
                              │
                              ▼
                    Mother Relation / Trace
```

### 6.1 Edge Recorder 最小責任

- 非阻塞接收 Runtime Event；
- 保存局部順序；
- 記錄輸入粒子、輸出粒子與 delta；
- 支援壓縮、批次同步與重送；
- 保留來源節點、版本、任務與時間；
- 在 Mother 接受前不得把本地暫存宣告為 canonical。

### 6.2 並行同步規則

每個事件至少包含：

```yaml
event:
  event_id: string
  task_id: string
  particle_id: string
  runtime_node_id: string
  module_id: string
  local_sequence: integer
  parent_event_ids: []
  delta: object
  origin_signature: MrLiouWord
  runtime_version: string
  occurred_at: string
```

同步原則：

1. 節點內以 `local_sequence` 維持順序。
2. 節點間不假設單一全域時鐘。
3. 以 `parent_event_ids`、task、particle 與 relation 重建因果。
4. 母體只裁定 canonical merge，不覆寫原始事件。
5. 衝突產生新裁定事件，不刪除舊紀錄。

這使 Memory、Agent、Workflow、World 與 Repository CI 能同時演進，而不必共用單一中央鎖。

---

## 7. Generation 與 Projection 的位置

### 7.1 Generation

Generation 使用既有粒子語言與重組規則：

```text
structure → mark → flow → recurse → store
```

它負責從既有粒子、關聯、任務規則與模板形成可交付結構。

### 7.2 Projection

Projection 是同一組 canonical 粒子的不同出口，不是新的真實來源：

- Runtime Projection；
- Source Code Projection；
- Browser UI Projection；
- API Projection；
- Memory／Timeline／Graph Projection；
- World Projection；
- Document／Package Projection。

```text
Canonical Particle + Relation + Rule
     ├── UI projection
     ├── code projection
     ├── memory projection
     ├── world projection
     └── delivery artifact
```

所有 Projection 必須能回指來源粒子、規則版本、生成事件與任務完成態。

---

## 8. Runtime Node 契約

每個節點必須向母體宣告：

```yaml
runtime_node:
  node_id: string
  node_type: dl580 | browser | mobile | github | cloud | worker
  capabilities: []
  protocol_version: string
  particle_formats: []
  output_projections: []
  health_endpoint: string | null
  authority_scope: []
  origin_signature: MrLiouWord
```

### 8.1 節點狀態

```text
DISCOVERED → REGISTERED → READY → RUNNING → DEGRADED → DRAINING → OFFLINE
```

節點可獨立升級，但進入 READY 前必須通過：

- protocol compatibility；
- identity validation；
- capability declaration；
- round-trip test；
- rollback path。

---

## 9. Coordination 不升格為新世界

協調能力由 Mother Runtime 的服務角色提供，不建立另一套資料真實來源。

```text
Task Policy
  ↓
Mother Coordinator
  ├── select nodes
  ├── dispatch particles
  ├── observe completion
  ├── merge results
  └── close task
```

Coordinator 只能：

- 分派；
- 路由；
- 合併；
- 重試；
- 回收；
- 執行完成閘門。

Coordinator 不得：

- 重新定義粒子；
- 取代 Mother Registry；
- 自行延伸任務；
- 將暫存狀態升格為 canonical；
- 繞過 LAW 與 origin signature。

---

## 10. Governance 與命名

所有新增資產遵守：

- `origin_signature: MrLiouWord`；
- MRL／Mrliou 命名權威；
- 外部產品名只作 Source、Provenance 或 Interface；
- DL580 母體為 canonical root；
- 外部平台為材料、鏡像、部署端或映射；
- append-only trace；
- 可逆、可回放、可封存；
- Layer 與 Stratum 不混用。

推薦 namespace：

```text
mrl::s0::<component>::<action>
mrl::s1::<component>::<action>
...
mrl::s7::<component>::<action>
```

---

## 11. CI 對齊

Repository CI 分成可並行、可獨立判定的門：

```text
CI
├── Particle Layer
├── Runtime Binding
├── Edge Recorder
├── Protocol Conformance
├── Projection / Generator
├── SDK Compatibility
├── Security
└── Release Package
```

### 11.1 狀態語義

- Particle 專用流程 PASS：代表 S0 交付成立。
- 全域 SDK FAIL：代表 repository-wide gate 未完成。
- 不得把舊 SDK 相容性失敗誤判成 ParticleLayer 功能失敗。
- Release 必須等必要 gates 通過，但各 Stratum 可持續演進。

### 11.2 Python 相容性治理

舊 Python 3.8／3.9 依賴問題應由 SDK Compatibility gate 管理。Particle／Runtime 新模組必須明確宣告支援矩陣，避免被未宣告的舊版本綁住。

---

## 12. 並行實作路線

以下工作可同時進行，均以本藍圖為對齊基準：

| Workstream | 對應位置 | 最小交付 |
|---|---|---|
| Runtime Binding | S1 | UnifiedParticle 與 Runtime Node 的 bind／execute／return contract |
| Edge Recorder | S2 | 非阻塞事件記錄、批次同步、重送、trace |
| Agent Adapter | S3 | Persona／模型能力映射，不生成新權威 ID |
| Workflow Completion | S4 | completion gate、delivery、seal、stop |
| World State | S5 | canonical world state 與節點 projection |
| Governance Registry | S6 | identity、version、authority、LAW validation |
| External Mapping | S7 | GitHub／Notion／Cloud／Device adapter contracts |
| SDK CI Repair | Governance | Black、Bandit、Python matrix、package build |

這些不是先後依賴的單一路徑；它們可以並行，但共用：

- UnifiedParticle；
- Mother Registry；
- Runtime Node Contract；
- Event／Trace Contract；
- Completion Policy。

---

## 13. 第一階段驗收條件

Mother Runtime Alignment v1 完成需滿足：

1. PR #56 的 `UnifiedParticle` 可綁定至少一個 Runtime Node。
2. 一次任務可從 problem 建立到 completion、delivery、seal、stop。
3. Runtime 執行不被 Edge Recorder 阻塞。
4. 事件能從節點同步至 Mother 並保留來源順序與因果。
5. 至少一種 Projection 能回指來源粒子與生成規則。
6. 所有 canonical 物件通過 LAW-0 identity 驗證。
7. round-trip 不丟失必要欄位。
8. 任務完成後不自行延伸，但 Mother Server 保持可接下一個任務。
9. 全域 SDK 失敗與各 Stratum 功能狀態分開呈現。
10. 產出可封存 manifest 與 rollback path。

---

## 14. Canonical 對齊總圖

```text
                           REALITY
                              │
                              ▼
                    [Task Policy / 智障系統]
                              │
                    problem + completion
                              │
                              ▼
                   [MRL Mother Runtime]
     governance / registry / world / sync / generation authority
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
    S0 Particle          S1 Runtime          S6 Governance
  UnifiedParticle      Runtime Binding      Identity / LAW
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
                    Parallel Runtime Nodes
          DL580 / Browser / Mobile / GitHub / Cloud
                              │
                              ▼
                   S2 Edge Memory / Trace
                              │
                              ▼
               Relation Merge / World State Update
                              │
                              ▼
                 Generation / Projection / Artifact
                              │
                              ▼
                Completion → Delivery → Seal → Stop
```

---

## 15. 最終裁定

MRL 的整合方向不是把所有模組塞進同一個處理程序，而是：

> 所有 Stratum、Runtime Node、Memory Edge、Agent、Workflow、World 與外部平台都能並行演進；Mother Runtime 位於更上層，維持共同身分、協定、世界狀態、生成規則、同步與完成治理。

PR #56 已完成 S0 Particle 的第一個實作錨點。下一個直接銜接面是 Runtime Binding 與 Edge Recorder；SDK CI 修復則作為並行治理線，不阻斷已通過的 ParticleLayer 主線。

```yaml
verdict: ALIGNED_FOR_IMPLEMENTATION
origin_signature: MrLiouWord
```
