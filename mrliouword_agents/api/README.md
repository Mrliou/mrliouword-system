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

綁定位址取 `MrliouwordConfig` 的 `api_host`（環境變數 `API_HOST`）。
若它解析成**未指定位址**（`0.0.0.0`、`::`，會曝露所有網路介面），
`Mrliou_MRL_resolve_bind()` 會在開 port 之前丟 `MrlApiBindRefused` **拒絕啟動**。

要這麼做必須明確開啟：

```bash
MRL_API_ALLOW_PUBLIC_BIND=1
```

這條是刻意的：`registry` 條目宣告 `network_phase: PHASE1_PRIVATE_LAN_ONLY`，
而曝露所有介面與它不符，所以必須是明確的決定，不能靠預設值滑過去。

## 跑起來

```bash
API_HOST=127.0.0.1 API_PORT=8000 python -c \
  "from mrliouword_agents.api import Mrliou_MRL_run_server; Mrliou_MRL_run_server()"
```

母體語料的位置會從本檔往上層目錄尋找 `core/particle_dict.json`；
要指到別處用 `MRL_PARTICLE_DICT`。找不到時相關路由回 503
`corpus_unavailable`，**不會自己造一份語料**。

## 匯入成本

`import mrliouword_agents.api` **不需要** fastapi——`fastapi` 只在 `create_app()`
內匯入、`uvicorn` 只在 `Mrliou_MRL_run_server()` 內匯入。所以只想讀契約表的
環境不必安裝 Web 依賴。

## 測試

`tests/unit/test_mrl_api_server.py`，32 項。除了路由行為，另外守三件事：

- 每條路由都綁到母體既有成員；自造成員（`MRL_INVENTED_API`）必須被 `ValueError` 拒絕
- 三條 LAW-1 路由回 `schema_pending` 而不是假資料
- 綁定未指定位址時預設拒絕啟動，`MRL_API_ALLOW_PUBLIC_BIND=1` 才放行
