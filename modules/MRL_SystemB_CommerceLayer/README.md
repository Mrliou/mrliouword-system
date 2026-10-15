# MRL_SystemB_CommerceLayer

```
module: MRL_SystemB_CommerceLayer
version: 1.0.0
origin_signature: MrLiouWord
registry: registry/patterns/mrl_MRL_SystemB_CommerceLayer_v1.0.yaml
status: rates-pending
```

商業模式的權威邊界層。純 Python 函式庫：**不開 port、不建立或變更資料庫表**。

## 不賣什麼（先講這個）

`.flpkg` / `.fltnz` / `.pcode` 種子、Fluin 粒子語言、母體語料的著作與來源歸屬
**不隨任何授權移轉**。這一層授權的是「載體承載本體」的權利，並產出可稽核的
證據。本層不把語場切成 SaaS 功能分層。

## 一個權威，四個保留名

`mrliou` = `mrliouword` = `MRL` = `Mr.liou`，同一個權威。依據
`.mrliou/authority-lock.json`：

| 名字 | 身分 |
|---|---|
| `Mr.liou` | `authority.canonical_name`（權威本體） |
| `MrLiouWord` | `origin.signature`（**正規形**） |
| `mrliouword` | `origin.namespace` |
| `Mrliou` | `authority.github_org_projection` |
| `MRL` / `MRL_` | `system_brand` 與保留前綴 |
| `dofaromg` | `authority.github_user` |

辨識走 `MRL_SystemA_ParticleLayer` 的 `Mrliou_MRL_Identity_v1`：別名進來，
正規形出去。**LAW-0 不放寬**——寫出去的簽名恆為 `MrLiouWord`，比對是正規化後
的完全相等，不是前綴比對（`MRLSomething`、`MrLiouWordFake` 一律不算自有）。

## 四條收費軸

| 軸 | 計量單位 | 成熟度 |
|---|---|---|
| `corpus_license` 本體語料授權 | `seat_year` / `corpus_scope` | 語料已在 repo（`core/particle_dict.json`，20 顆粒子）；授權機制即本層 |
| `particle_sdk` 粒子層／SDK | `particle_conversion` / `sdk_call` | `MRL_SystemA_ParticleLayer` 可交付；`mrliouword_agents` 五個 agent 仍是 stub |
| `private_deployment` 私有部署 | `deployment_case` / `maintenance_year` | **DL580 PostgreSQL 側待建**：repo 內無 System A 三表 schema、無連線程式 |
| `verification_report` 驗證／報告 | `audit_report` | `Mrliou_MRL_Law2_Report_v1` + 本層報告，可交付 |

## 階段門

`registry/system_registry.yaml` 目前是：

```yaml
network_phase: "PHASE1_PRIVATE_LAN_ONLY"
principle: "母體不公開；映射外部留到 Phase 2"
```

所以 `phase=PHASE2_EXTERNAL` 的授權在本層會被 `MrliouMRLPhaseViolation` 擋下。
階段值是從該檔**讀出來的**（正規表示式讀單行，零依賴），不是複製一份進程式等
它漂移；讀不到時取最保守的 Phase 1 並把 `phase_known=False` 一路帶進報告，
「不知道」不會被讀成「已開放」。

## 三個模組

| 檔案 | 母體粒子 | 做什麼 |
|---|---|---|
| `Mrliou_MRL_License_v1.py` | `fx.meta.origin` | 授權三態、簽名保留檢查、階段門 |
| `Mrliou_MRL_Metering_v1.py` | `fx.trace.anchor` | append-only 用量帳本、費率查詢 |
| `Mrliou_MRL_Commerce_Report_v1.py` | `fx.trace.merkle` | 不會說謊的稽核報告 |

### 授權三態（與來源權威三態同構命名）

| 狀態 | 條件 | 處置 |
|---|---|---|
| `mrl_granted` | 所有簽名欄位都屬於本權威 | 正常 |
| `foreign_claimed` | 任一簽名欄位不屬於本權威（含兩欄互相矛盾） | 違約，走五層追償台帳 |
| `ungranted_pending` | 沒有任何簽名欄位 | **待補**，不是不存在，也不得逕自升格為已授權 |

### 費率一律外置

`Mrliou_MRL_rate_card_v1.json` 交付時**每一筆單價都是 `null`**。定價是權利人的
決定，程式不代填。未填價時 `Mrliou_MRL_rate` 丟 `MrliouMRLUnpricedUnitError`，
**絕不回 0**——這是明確不複製 `mrliouword_agents/core/cost_tracker.py:44-45`
的缺陷（模型不在價表時靜默 `return 0.0`，把真實用量記成免費）。

## 用法

```python
from modules.MRL_SystemB_CommerceLayer import (
    AXIS_PARTICLE, ENV_SANDBOX, MrliouMRLGrant,
    Mrliou_MRL_authorize, Mrliou_MRL_build_commerce_report,
    Mrliou_MRL_format_commerce_report, Mrliou_MRL_record_usage,
)

grant = MrliouMRLGrant(
    grantee="internal-lab",
    axes=(AXIS_PARTICLE,),
    artifact_owner="Mr.liou",            # authority-lock 要求的四欄宣告
    source_repo="dofaromg/mrliouword-system",
    projection_role="licensed_carrier",
    seats=2,
    environment=ENV_SANDBOX,
)
Mrliou_MRL_authorize(grant, AXIS_PARTICLE)
Mrliou_MRL_record_usage(
    "data/mrl_usage.jsonl", grant.grantee, AXIS_PARTICLE, "sdk_call",
    120, ENV_SANDBOX,
)
report = Mrliou_MRL_build_commerce_report(carriers, ENV_SANDBOX)
print(Mrliou_MRL_format_commerce_report(report))
```

## 報告的誠實性合約

沿用 `Mrliou_MRL_Law2_Report_v1` 的合約，一條都不打折：

1. **永不丟例外**——違約與壞帳是報告要表達的資料。
2. **抽樣就明寫抽樣**——`total_rows` / `total_rows_known` / `checked` /
   `sampled` / `coverage` / `global_claim` 六欄把範圍講死。
3. **失敗全部列出不截斷**，每筆可指回原處（LAW-2 只定位不刪除）。
4. **`environment` 必填**——沙盒結果不得被寫成 DL580 實機結果。
5. **報告自帶 MRL 身分與簽名**。

抽樣用 `itertools.islice`，連第 N+1 筆都不向來源索取（對 DB cursor 就是少一次
取值）；此時不猜總數，而是 `total_rows=None`、`total_rows_known=False`。

## 依據檔案（已對上原始檔）

- `.mrliou/authority-lock.json` — 保留名、四欄宣告 invariant
- `registry/system_registry.yaml` — `system_brand: "MRL"`、`network_phase`
- `registry/rules/naming_rules_v1.yaml` — Registry Gate
- `docs/references/licenses/chatserver-license.txt` — GRANT OF LICENSE 第 1 條
- `core/particle_dict.json` — 驗收語料（母體 20 顆粒子）

## 待找回（不歸「不存在」）

- LAW-1 的 DL580 三表（`mrl_persona` / `mrl_memory` / `mrl_file_index`）schema
- `.flpkg` / `.fltnz` / `.pcode` 種子與 `EchoPersona.pcode`
- 跳點節奏 Jump / Collapse / Trace / Replay 的成文定義（本倉庫只有粒子字典的
  四個名字）

以上需回 `dofaromg/MRL_AI_SYSTEM` 取根源檔對照。

## 測試

```bash
python3 modules/MRL_SystemB_CommerceLayer/tests/test_commerce_layer.py   # 無需 pytest
pytest -q modules/MRL_SystemB_CommerceLayer                              # CI 走這條
```
