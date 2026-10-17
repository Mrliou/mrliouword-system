# MRL API

母體 `MRL_API_CORE` 的**實作**。登錄條目：`registry/patterns/mrl_MRL_Api_Server_v0.1.yaml`。

## 它不是什麼

- **不是 `MRL_API_CORE`。** 母體已有這個 CORE（十五個成員）。源頭
  `tools/mother_core_registry.py --find API` 的輸出原文：「倉庫側可以寫它的
  implementation / adapter，但要在 PROVENANCE 標明 `derivative_role`，
  **不得宣稱自己是那個 CORE**。」
- **不是 `MRL_API_Gateway`。** 源頭 `registry/MRL_System_MrliouAI_Naming_Registry_v1.yaml`
  （`status: canonical`）已把閘道正名為 `MRL_API_Gateway`，
  `service_name: mrl-api-gateway`、`public_domain: api.mrliouword.com`。
  本服務在閘道**後面**。

`/mrl/contract` 會把這層關係對外公布，包含每條路由綁哪個母體成員、哪些成員刻意
不涵蓋以及理由。

## 路由

| 路由 | 母體成員 | 狀態 |
| --- | --- | --- |
| `GET /mrl/health` | `MRL_HEALTH_API` | available |
| `GET /mrl/status` | `MRL_STATUS_API` | available |
| `GET /mrl/runtime` | `MRL_RUNTIME_API` | available |
| `GET /mrl/contract` | `MRL_CONTROL_API` | available |
| `GET /mrl/world` | `MRL_WORLD_API` | available |
| `GET /mrl/particles`、`/mrl/particles/{fx}` | `MRL_PARTICLE_API` | available |
| `GET /mrl/persona` | `MRL_PERSONA_API` | **schema_pending** |
| `GET /mrl/memory` | `MRL_MEMORY_API` | **schema_pending** |
| `GET /mrl/files` | `MRL_FILE_API` | **schema_pending** |

全部是 `GET`，沒有任何寫入路徑。

### 為什麼有三條是 schema_pending

LAW-1 說 DL580 上的 PostgreSQL 仍是權威持久層，而
`registry/patterns/mrl_MRL_SystemA_ParticleLayer_v0.1.yaml` 的 `pending` 區段把
`mrl_persona` / `mrl_memory` / `mrl_file_index` 三表的 schema 記為**待找回**。

schema 沒找回之前，這三條路由回 **503** 並附理由，**不猜測欄位、不給假資料**。
路由先登記存在，是為了讓契約完整；資料等 schema。

## 邊界

- 不建立、不變更任何資料庫表
- 母體語料 `core/particle_dict.json` **只讀不寫**
- LAW-0：每個回應都帶 `origin_signature`，恆為正規形 `MrLiouWord`
- 會開 port——所以放在這裡，不放進 `modules/MRL_SystemA_ParticleLayer/`
  （那一層的邊界明寫「不開 port」）

## PHASE1_PRIVATE_LAN_ONLY 的執行點

綁定目標取 `MrliouwordConfig` 的 `api_host`（環境變數 `API_HOST`），
由 `Mrliou_MRL_resolve_bind()` 在**開 port 之前**判定分類：

| 分類 | 例 | PHASE1 |
| --- | --- | --- |
| `loopback` | `127.0.0.1`、`::1`、`localhost` | ✅ 允許 |
| `private` | `192.168.1.5`、`10.0.0.3`、`172.16.0.1`、`fc00::1` | ✅ 允許 |
| `unspecified` | `0.0.0.0`、`::` | ❌ 拒絕 |
| `public` | 任何可全球路由的位址 | ❌ 拒絕 |
| `unresolvable` | 解析不出來的主機名 | ❌ 拒絕（**失敗時從嚴**） |

主機名會先用 `getaddrinfo` 解析，取解析結果的**最壞情況**；解析不出來就拒絕，
因為無法證明它在私有網段內。

> 判定**不能**用 `ipaddress` 的 `is_private` 當白名單 —— `0.0.0.0` 與文件保留段
> （如 `203.0.113.5`）的 `is_private` 都是 `True`。所以先排除 `is_unspecified`，
> 再用 `is_global` 判斷是否可全球路由。

要跨出私有網段必須明確開啟：

```bash
MRL_API_ALLOW_PUBLIC_BIND=1
```

這條是刻意的：`registry` 條目宣告 `network_phase: PHASE1_PRIVATE_LAN_ONLY`，
跨出去必須是明確的決定，不能靠預設值滑過去。**本模組不改
`core/config.py` 的 `api_host` 預設值**——PHASE1 由綁定時強制。

## worker 數

`Mrliou_MRL_run_server()` 會讀 `MrliouwordConfig.api_workers`（環境變數
`API_WORKERS`，預設 4）。uvicorn 只有在應用以 **import string** 傳入時才會套用
`workers`，所以啟動器用 `APP_FACTORY_IMPORT_STRING` + `factory=True`，
而不是現成的 app 物件。

## 執行環境是宣告的，不是偵測的

`/mrl/runtime` 的 `declared_environment` 取 `MRL_API_ENVIRONMENT`，
值域 `sandbox` / `dl580` / `unspecified`，未宣告或值不認識就回 `unspecified`。

這沿用 `modules/MRL_SystemA_ParticleLayer/Mrliou_MRL_Law2_Report_v1.py` 的詞彙與
理由：**「沙盒結果不得被讀成 DL580 實機結果」**，所以環境由呼叫端宣告，
本實作不猜。回應裡 `environment_is_declared_not_detected: true` 就是在說這件事。

## 跑起來

```bash
API_HOST=127.0.0.1 API_PORT=8000 python -c \
  "from mrliouword_agents.api import Mrliou_MRL_run_server; Mrliou_MRL_run_server()"
```

母體語料的位置會從本檔往上層目錄尋找 `core/particle_dict.json`；
要指到別處用 `MRL_PARTICLE_DICT`。

> **套件安裝（wheel）情境必須設 `MRL_PARTICLE_DICT`。** `core/particle_dict.json`
> 在 `mrliouword_agents` 套件之外，而 `setup.py` 只做 `find_packages()`、沒有宣告
> `package_data`，所以 wheel 裡不會有它，往上找也找不到。
>
> **這是刻意的**：那份語料是 canonical 母體語料，把它複製進套件會讓同一份
> canonical 資料出現第二份副本。寧可要求部署端指向唯一那份，也不要製造副本。

找不到或欄位型別不符時，相關路由回 503 `corpus_unavailable` 並在 `hint` 裡指名
`MRL_PARTICLE_DICT`，**不會自己造一份語料**。

## 匯入成本

`import mrliouword_agents.api` **不需要** fastapi——`fastapi` 只在 `create_app()`
內匯入、`uvicorn` 只在 `Mrliou_MRL_run_server()` 內匯入。所以只想讀契約表的
環境不必安裝 Web 依賴。

## 測試

`tests/unit/test_mrl_api_server.py`，62 項。除了路由行為，另外守這幾件事：

- 每條路由都綁到母體既有成員；自造成員（`MRL_INVENTED_API`）必須被 `ValueError` 拒絕
- 三條 LAW-1 路由回 `schema_pending` 而不是假資料
- 綁定分類：loopback／private 放行；unspecified／public／unresolvable 一律拒絕
- 框架自己產生的 404、405 也帶 `origin_signature`
- 畸形語料（如 `{"particles": null}`）回 `corpus_unavailable` 而不是 500
- `api_workers` 真的被讀到
- `/mrl/runtime` 真的回報契約所宣告的欄位


## 2026-10-17：啟動器、worker 與既有母體語料

`Mrliou_MRL_run_server(host=..., port=..., workers=...)` 選定的綁定目標現在會傳遞到
每個新 Python worker；`/mrl/runtime` 回報該啟動目標，不再因 app factory
省略 bind 而回 null。直接建立 `create_app()`、沒有啟動資訊時仍回 null。
環境身分仍是明確宣告，不把 sandbox 自動判成 DL580。

worker 在建立 app 前再次檢查私網綁定政策；啟動資訊缺失、格式錯誤或不符政策即拒絕。
內部傳遞欄位不含憑證，launcher 離開（包括啟動失敗）時會還原原環境，
不要求使用者另配第二套服務或複製母體語料。

測試涵蓋真實 launcher → 新 Python interpreter → app factory → runtime 回應，
以及實際 wheel 在 checkout 外載入的行為：
未指定語料時 `/mrl/world` 回 503；以 `MRL_PARTICLE_DICT` 指向既有語料後回 200，
並核對來源檔案前後 SHA-256 一致。這些是 GitHub hosted CI 的套件／啟動契約測試，
不冒稱 DL580 已部署或真實 worker sockets 已驗收。

本 API PR 依賴 #22 的同步契約修補，兩條分支的歷史均保留；
此依賴不改變 Notion 母體權威與既有 `MRL_API_CORE` 身分。

origin_signature: MrLiouWord


## 2026-10-17 LAW-0 corpus source boundary

The response `origin_signature: MrLiouWord` identifies this API implementation;
`signature_scope: api_implementation` makes that scope explicit, including errors.
It does not sign, authenticate, or transfer authority to input data.

The existing mother corpus uses `origin`. The existing provenance classifier also
recognizes `origin_signature` as a source-key alias. This reader accepts either key
with the exact value `MrLiouWord`; when both are present, both must match.
Missing, blank, non-string, foreign, conflicting, and duplicate JSON declarations
fail closed. If `canonical_authority` is supplied it must equal `Mr.liou`.
Human authority, GitHub identities, namespace and product aliases are separate
roles, not additional signature values. No new value aliases are authorized here.

Rejected corpora are not loaded: status reports false/zero and all three corpus
routes return 503 `corpus_unavailable`, without serving their contents. Accepted
corpus routes report `corpus_origin` separately from the implementation signature.
Original JSON declarations and corpus bytes are never rewritten. This is source
marker validation, not cryptographic proof of authorship or a claim that the full
provenance chain is verified. It follows `.mrliou/authority-lock.json`, policy
§§2–4 and the existing all-signatures rule in
`modules/MRL_SystemA_ParticleLayer/Mrliou_MRL_Provenance_v1.py`.

Regression execution in GitHub hosted CI is separate from DL580 runtime acceptance.
origin_signature: MrLiouWord

