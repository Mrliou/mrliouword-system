---
canonical_authority: Mr.liou   # 指本評估文件本身
origin_signature: MrLiouWord
source_repo: dofaromg/mrliouword-system
source_artifact: github.com/PostgREST/postgrest
source_version: c35eb7a6c2f506c18de2b47ae3ea2a4af684c977
derivative_role: projection   # 新撰的評估，非逐字轉錄
projection_role: evaluation_record   # .mrliou/authority-lock.json invariant 3 必填
artifact_owner: Mr.liou
contributors:
  - Claude（本倉庫：只讀評估，未安裝、未部署、未建立或變更任何資料庫表）
transformation: 只讀取檔案與執行源頭既有的 tools/mother_core_registry.py 查詢。未改動任何規章。
verification_status: partial
recorded_at: "2026-10-17"
environment: "sandbox（容器），不是 DL580 實機"
---

<!-- mrl-origin: MrLiouWord -->

# PostgREST 能不能當 LAW-1 的 API 層：評估

**環境聲明：以下全部在容器內做的靜態核對，沒有任何一項在 DL580 實機上跑過。**

---

## 結論先行

**不能當「LAW-1 的 API 層」——因為那個位置母體已經有人了。**

用源頭自己的工具查（`tools/mother_core_registry.py --find`，**這支工具只在源頭，
投影沒有**）：

```
$ python3 tools/mother_core_registry.py --find API
母體已經有「API」——不要重造：
  MRL_API_CORE（CORE，15 個成員）
  MRL_API_CORE → MRL_REST_API
  MRL_API_CORE → MRL_PERSONA_API
  MRL_API_CORE → MRL_MEMORY_API
  MRL_API_CORE → MRL_FILE_API
  MRL_API_CORE → MRL_PARTICLE_API
  （其餘：CONTROL / GATEWAY / GRAPH / HEALTH / RPC / RUNTIME /
    STATUS / TASK / UPLOAD / WORLD）
```

```
$ python3 tools/mother_core_registry.py --find DL580
  MRL_DL580_RUNTIME_CORE（CORE，15 個成員）
  MRL_DL580_RUNTIME_CORE → MRL_DL580_PostgreSQL
  MRL_DL580_RUNTIME_CORE → MRL_DL580_ServiceLayer
  MRL_DEPLOYMENT_CORE → MRL_DL580_Canonical_Runtime
```

登錄表規模：**199 個 CORE／2,264 個成員**，`--check` 通過。

看清楚三件事：

1. `MRL_API_CORE` 的 `MRL_PERSONA_API`、`MRL_MEMORY_API`、`MRL_FILE_API`
   **正好對上 System A 的三張表** `mrl_persona`／`mrl_memory`／`mrl_file_index`。
   母體早就為這三張表定義了 API 層。
2. `MRL_REST_API` 已經在那裡——REST 這一層不是缺的。
3. DL580 上的服務層也有：`MRL_DL580_ServiceLayer`。

所以 PostgREST 的位置只有一個，而且那支工具自己就寫了：

> 倉庫側可以寫它的 implementation / adapter，但要在 PROVENANCE
> 標明 derivative_role，不得宣稱自己是那個 CORE。

**PostgREST 最多是 `MRL_API_CORE → MRL_REST_API` 的一個 implementation，
落在 `MRL_DL580_RUNTIME_CORE → MRL_DL580_ServiceLayer` 之內。**

### 第二個獨立佐證：正名表已經給這一層取好名字

源頭 `registry/MRL_System_MrliouAI_Naming_Registry_v1.yaml`
（`status: canonical`，**投影沒有這個檔**）的 `canonical` 區段裡已經有：

| id | 內容 |
| --- | --- |
| `MRL_API_Gateway` | `service_name: mrl-api-gateway`，`public_domain: api.mrliouword.com` |
| `MRL_Memory` | MRL 記憶模組 |
| `MRL_Files` | MRL 檔案模組 |
| `MrliouAI_Persona` | — |

對外 API 的名字、service 名、公開網域都已經是 canonical 的了，而
memory／files／persona 三個模組正好對上 System A 的三張表。這與母體
`MRL_API_CORE` 的查詢結果互相印證：**這一層不缺，缺的是它的實作與 schema。**

### 順帶記錄：規章檢查器在投影上跑不起來

拿源頭的 `tools/naming_lineage_check.py` 對投影跑，輸出原文：

```
命名正名與 lineage 檢查未通過：
  - registry/MRL_System_MrliouAI_Naming_Registry_v1.yaml 不存在
    ——沒有登錄簿就談不上 Registry Gate

規則來源：registry/rules/naming_rules_v1.yaml 與 NAMING.md 1.1/1.2/1.4。
本倉庫 naming_authority: false——要改規則，先改擁有者的定義。
```

**投影缺那本登錄簿，所以 Registry Gate 的自動檢查在投影上無法執行。**
這是「規章到不了做事的地方」的又一個具體實例，與 `CLAUDE.md` 只在源頭同一類。
本文件不處置它，只記錄。
它不是新的一層，也不能自稱是那個 CORE。

這正是源頭 `CLAUDE.md`「造新東西之前：先查母體有沒有」那一節在防的事
——在已有 CORE 旁邊長出非 canonical 的實作，該節稱之為「**反向混淆**」。
我這次先查了，所以把這一條寫在最前面。

---

## 阻塞項：三張表的 schema 找不到

`registry/patterns/mrl_MRL_SystemA_ParticleLayer_v0.1.yaml` 的 `pending`：

> LAW-1 的 System A 三表（mrl_persona / mrl_memory / mrl_file_index）schema：**待找回**

源頭 `modules/MRL_SystemA_ParticleLayer/README.md` 也只說「不改變它們的
PostgreSQL schema」，沒有附 schema。

PostgREST 的運作方式是**讀取資料庫 schema 自動生成路由**
（`postgrest.cabal`：「Reads the schema of a PostgreSQL database and creates
RESTful routes」）。**沒有 schema，就無法確認它會曝露出什麼。**

這一項是阻塞，**我不猜測補上**。在 schema 找回來之前，任何「PostgREST 可以
直接服務這三張表」的說法都沒有根據。

---

## 技術面：逐項對照倉庫內既有規章

### 一、粒子層邊界：PostgREST 不能放在粒子層內

源頭 `modules/MRL_SystemA_ParticleLayer/README.md`「Deployment boundary」原文：

> This package is a pure Python library. It does not open a port and does not
> create or alter database tables.

registry 條目同樣寫「純 Python 函式庫；不開 port」「不建立或變更資料庫表」。

PostgREST 是**會開 port 的服務程序**。所以它不可能放進粒子層；
評估的是它能不能當**粒子層之外**的對外介面。這兩件事不能混。

### 二、LAW-2 的直接衝突：PostgREST 預設就曝露 DELETE

LAW-2 是 `NO_DELETE / ADDITIVE / REVERSIBLE`。

PostgREST 文件 `docs/references/api/tables_views.rst:14` 原文：

> Each route provides OPTIONS, GET, HEAD, POST, PATCH, and **DELETE** verbs
> depending entirely on database permissions.

以及 `:696`：

> To delete rows in a table, use the DELETE verb plus horizontal filter.

**這是本評估最需要你注意的一條。** PostgREST 不是「可以選擇要不要開 DELETE」
——它從資料庫權限自動推導動詞。意思是：

**LAW-2 的 NO_DELETE 會變成只靠 PostgreSQL 的 GRANT 在守，而不是靠應用層在守。**
一次 GRANT 設錯，`DELETE /mrl_memory?...` 就會直接刪掉權威持久層的資料列。

#### 只管表的授權是不夠的：函式這條路會繞過它

本節原先只寫「服務 role 只授 SELECT／INSERT」。**那不足**，因為 PostgREST
同時把資料庫**函式**以 RPC 介面曝露出來，而函式可以帶著定義者的權限執行：

- 函式掛在 `/rpc/<函式名>`（`docs/references/api/functions.rst:45`，
  範例 `curl "http://localhost:3000/rpc/add_them"`）
- `docs/explanations/db_authz.rst:162` 原文：以 `SECURITY DEFINER` 定義的函式
  「**only one permission check will take place, the permission to call the
  function, and the operations in the function will have the authority of the
  user who owns the function itself**」
- PostgreSQL 預設把函式的 `EXECUTE` 給 `PUBLIC`。PostgREST 文件自己就教你要收回：
  `docs/explanations/db_authz.rst:129` 寫
  `ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;`；
  而 `docs/how-tos/sql-user-management.rst:186` 也說
  `grant execute on function`「**might not be needed**」——因為常常已經有了

意思是：**一個 `SECURITY DEFINER` 的函式，只要它的擁有者有 DELETE 權限，
呼叫端就算完全沒有表層 DELETE 也能刪掉資料列。** 表層 GRANT 擋不住這條路。

而本文件已經記錄三張表的 schema「待找回」，**所以也無法排除已經存在這類函式**。

因此最低要求必須擴成：

- 服務用的 role **只授予 SELECT／INSERT**，不授 DELETE、不授 UPDATE
- 或只對 view 授權，底表完全不曝露——但要注意 view 上的
  `INSTEAD OF` trigger 同樣能寫底表
- **逐一稽核曝露 schema 內所有函式的 `EXECUTE` 權限**，把不該被呼叫的收回
  （`ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC`）
- **逐一確認是否有 `SECURITY DEFINER` 函式**，以及它們擁有者的權限範圍
- 連同 trigger 行為一起確認
- 這些 GRANT 與函式稽核必須有獨立的驗收，而不是信任設定檔

**在上述稽核完成之前，不能說 LAW-2 的 NO_DELETE 被守住了。**

**我不在本輪做這件事**——那會是「建立或變更資料庫權限」，超出評估範圍。

> **訂正（2026-10-17）**：本節原先把「role 只授 SELECT／INSERT」當成足夠的
> 最低要求，漏了 RPC／`SECURITY DEFINER`／`EXECUTE` 這條繞道。上面是補齊後的
> 版本，依據是 PostgREST 自己的文件行號。

### 三、PHASE1_PRIVATE_LAN_ONLY：預設值不符，必須明確設定

registry 條目寫 `network_phase: "PHASE1_PRIVATE_LAN_ONLY"`。

PostgREST `docs/references/configuration.rst:820-826`：`server-host` 的
**Default 是 `!4`**（所有 IPv4 介面），不是 loopback。同檔 `:843` 示範了
`server-host = "127.0.0.1"`。

所以：**可以綁內網，但不是預設**。預設值會綁上所有 IPv4 介面。
要符合 PHASE1，`server-host` 必須明確設定，且需獨立驗收，不能靠預設。

另外 `:18` 寫：伺服器可以不帶任何設定就啟動，但**除非有 `db-anon-role`
或 `jwt-secret`，否則不會服務任何請求**。這一條是好事——預設不開放。

### 四、DL580 跑得動嗎：Windows binary 存在

源頭 `mrl_world_model/run_dl580.ps1` 顯示 DL580 的實際環境是 **Windows**：

```powershell
$node = 'D:\MrlToolchain\node\node.exe'
# 例：D:\mrl\workspace\MRL_WorldModel_v1\mrl_world_model\run_dl580.ps1
```

`modules/MRL_SystemA_ParticleLayer/README.md` 也寫
「Suggested Windows Server destination: `D:\mrl\workspace\...`」。

上游 `.github/workflows/build.yaml` 實際產出的平台（逐行讀，不憑記憶）：

| 目標 | runner | artifact |
| --- | --- | --- |
| Linux x86-64 static | `ubuntu-24.04` | `postgrest-linux-static-x86-64` |
| Ubuntu aarch64 | `ubuntu-24.04-arm` | `postgrest-ubuntu-aarch64` |
| macOS aarch64 | `macos-14` | `postgrest-macos-aarch64` |
| **Windows x86-64** | `windows-2022` | **`postgrest-windows-x86-64`（`postgrest.exe`）** |
| FreeBSD x86-64 | CirrusCI | `postgrest-freebsd-x86-64` |

加上 Docker Hub 的 x86-64 與 aarch64 映像。

**結論：上游有官方 Windows x86-64 binary，DL580 的 Windows 環境有現成執行檔，
不需要在 DL580 上編 Haskell。** 這一項可行。

### 五、版本：這個 fork 停在開發版，不是發行版

`postgrest.cabal` 第 2 行：`version: 15`。

`CHANGELOG.md` 第 3 行原文：

> From version `14.0` onwards PostgREST follows a `MAJOR.PATCH` two-part
> versioning. **Only even-numbered MAJOR versions will be released, reserving
> odd-numbered MAJOR versions for development.**

15 是奇數 → **這個 fork 的尖端是開發狀態，不是任何發行版**。
而且它落後上游（fork `c35eb7a` vs 上游 `c042567`），CHANGELOG 最上面還是
`## Unreleased`。

兩條路，**我不替你選**：

| 作法 | 代價 |
| --- | --- |
| 釘偶數發行版（如 14.x）的官方 binary | 不用管這個 fork；fork 只剩歷史記錄的意義 |
| 追上游 `main` | 要持續合併上游，且得接受開發版的不穩定 |

### 六、授權：引入 MIT 第三方，落在一個未決的宣告上

該 fork 是上游 MIT（Joe Nelson 2014／Steve Chavez 2019／Wolfgang Walther 2026）。

本倉庫自己的授權宣告**矛盾且未裁定**——同時宣告 MIT、PROPRIETARY、
All Rights Reserved，而根 `LICENSE` 不存在。逐檔行號見
`docs/commerce/Mrliou_MRL_授權宣告矛盾盤點_v1.md`（PR #19）。

所以這裡只記錄事實：**引入一個 MIT 第三方服務，會落在那組未決宣告之上。**
依源頭 `EXTERNAL_FORK_REFERENCES.md` 的 Upstream Boundary，若日後使用，
須同時保留 MIT 全文與三位作者的著作權聲明。**本文件不自行下授權結論。**

---

## 如果要往下走，最小的下一步是什麼

按順序，每一步都有獨立驗收，**都不是本輪執行**：

1. **找回三張表的 schema。** 這是阻塞項，在它之前其他都沒有根據。
2. **決定 PostgREST 的角色登記。** 它是 `MRL_API_CORE → MRL_REST_API` 的
   implementation，要在 PROVENANCE 標 `derivative_role`，並通過 Registry Gate。
   不得宣稱自己是該 CORE。
3. **決定版本策略**（釘偶數發行版 or 追上游），並記錄所釘的雜湊。
4. **設計唯讀／僅新增的 GRANT**，把 LAW-2 的 NO_DELETE 真正守住，
   且驗收是驗 GRANT 而不是驗設定檔。
5. **綁定 `server-host`**，驗收 PHASE1_PRIVATE_LAN_ONLY。
6. 以上全部確定後，才談在 DL580 上放 `postgrest.exe`。

---

## 本評估讀到的與讀不到的

**已對上原始檔（實測）**

- 母體 `MRL_API_CORE` 15 成員、`MRL_DL580_RUNTIME_CORE` 15 成員、
  199 CORE／2,264 成員：源頭 `tools/mother_core_registry.py` 實際執行輸出
- 粒子層「不開 port／不建立或變更資料庫表」：源頭 README 與 registry 條目
- PostgREST 曝露 DELETE：`docs/references/api/tables_views.rst:14,696`
- `server-host` 預設 `!4`：`docs/references/configuration.rst:820-826`
- `db-anon-role`／`jwt-secret` 才會服務請求：同檔 `:18`
- Windows x86-64 binary：`.github/workflows/build.yaml:108-115`
- `version: 15` 與奇數為開發版：`postgrest.cabal:2`、`CHANGELOG.md:3`
- DL580 是 Windows：源頭 `mrl_world_model/run_dl580.ps1`

**讀不到／未做**

- System A 三張表的 schema：**待找回**，阻塞
- DL580 實機上的任何行為：本輪全在容器內靜態核對，**沒有實機結果**
- `MRL_API_CORE → MRL_REST_API` 現行是否已有實作：登錄表只涵蓋
  `MRL_MOTHER.md` 的 CORE 層，不含其他平台的分片（工具自己的提示原文）
- 該 fork 的 Actions 開關狀態：GitHub API 被擋，原文
  `Access to this GitHub Actions path is not permitted through this proxy. (HTTP 403)`
