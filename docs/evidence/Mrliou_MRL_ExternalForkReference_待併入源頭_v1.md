---
canonical_authority: Mr.liou   # 指本交接單本身；被記錄的外部上游著作權歸屬見內文
origin_signature: MrLiouWord   # 僅指本交接單本身由 MRL 側建立
source_repo: dofaromg/-postgrest（外部 fork，非本倉庫產出）
source_artifact: github.com/PostgREST/postgrest
source_version: c35eb7a6c2f506c18de2b47ae3ea2a4af684c977
derivative_role: projection   # 新撰的核對記錄，非逐字轉錄
projection_role: external_fork_reference_handoff   # .mrliou/authority-lock.json invariant 3 必填
mirror_of: PostgREST/postgrest   # 政策第 5 節第 4 條：鏡像或 fork 必須標明
artifact_owner: Mr.liou  # 本交接單產物；被引用材料的作者與授權依原來源保留
contributors:
  - Claude（本倉庫：只讀核對 fork 歸屬與建構歷史，未修改該 fork 任何檔案）
transformation: 只做 clone（只讀）、git fetch 驗證 commit 歸屬、GitHub API 讀取後設資料、全樹關鍵字搜尋。未修改、未匯入、未推送。
verification_status: partial
in_source_of_truth: false
pending_source_merge: true
canonical_location: dofaromg/mrliouword-system registry/evidence/EXTERNAL_FORK_REFERENCES.md
recorded_at: "2026-10-17"
---

<!-- mrl-origin: MrLiouWord -->

# External Fork Reference 待併入源頭：`dofaromg/-postgrest`

## 這份文件為什麼在這裡，而不在帳本裡

`registry/evidence/EXTERNAL_FORK_REFERENCES.md` **只存在於源頭**
`dofaromg/mrliouword-system`。本投影連 `registry/evidence/` 這個目錄都沒有：

```
$ ls registry/evidence/
ls: cannot access 'registry/evidence/': No such file or directory
```

在投影另建一份同名帳本，會讓同一本證據帳本分岔成兩份。
`.mrliou/authority-lock.json` 的 invariant 正是要防這件事：

> Repository mirrors and organization projections cannot silently become
> source_of_truth

所以本輪**不在投影建立 `registry/evidence/`**。下面第二節是可以直接附加到
源頭那本帳本的條目原文，格式與既有第 1 筆
（`features-feature_terraform_1.4.2`）一致。真正附加需要能掛上源頭的工作階段
——那件事目前未解，本文件就是交接單。

機器可讀的登錄條目另見
`registry/patterns/mrl_-postgrest_v0.1.yaml`（Registry Gate 要求的本體）。

---

## 可直接附加到源頭帳本的條目原文

以下內容從 `## 2.` 起，整段附加到源頭
`registry/evidence/EXTERNAL_FORK_REFERENCES.md` 的第 1 筆之後。
**不改該檔既有任何一行**，也不改它的 front matter。

---

## 2. `dofaromg/-postgrest`

| 欄位 | 值 |
| --- | --- |
| 上游專案 | `PostgREST/postgrest`（REST API for any Postgres database） |
| 授權 | MIT License, **Copyright (c) 2014 Joe Nelson / (c) 2019 Steve Chavez / (c) 2026 Wolfgang Walther** |
| fork 關係 | `fork: true`，`parent` 與 `source` 都是 `PostgREST/postgrest`——直接 fork 自上游，不是從別人的 fork 再 fork |
| `mirror_of` | `PostgREST/postgrest`（政策第 5 節第 4 條要求鏡像或 fork 必須標明） |
| 可見性 | public |
| 分支 | 只有 `main` 一條 |
| tag 數 | 0 |
| fork HEAD | `c35eb7a6c2f506c18de2b47ae3ea2a4af684c977`（2026-02-02，作者 Taimoor Zaeem，上游維護者） |
| 記錄時上游 main | `c042567494b1cbb5009005b82c78d9e5da8b4a2a`（本 fork 落後） |
| 專案版本 | `postgrest.cabal` 的 `version: 15`——依 CHANGELOG「只發行偶數主版本，奇數保留給開發」，**15 是開發版，不是發行版** |
| 內含 | 384 個檔案，5.4 MB |
| 建立時間 | `2026-02-03T06:23:19Z` |
| 最後推送 | `2026-02-02T23:45:00Z` |
| issues（含 closed） | 0（且 `has_issues: false`） |
| pull requests（含 closed） | 0 |
| **Actions 執行紀錄** | **0** |
| 倉庫名異常 | 開頭是連字號（`-postgrest`） |

### 核對結果

**一、沒有任何自有內容（git 層證據，不是關鍵字推論）**

```
$ git fetch --depth 2000 upstream main
$ git merge-base --is-ancestor c35eb7a6c2f506c18de2b47ae3ea2a4af684c977 upstream/main
（exit 0 → TRUE）
```

fork 的 `main` 尖端是**上游 `main` 的祖先**（上游 `main` 當時為 `c042567`）；
而該 fork 只有 `main` 一條分支、零 tag。故沒有任何自有內容。

> **方法訂正（2026-10-17）**：本節原先只用 `git fetch upstream <sha>` 取得成功
> 當證據。那不足——upload-pack 能供應某個物件，只證明它在該倉庫的物件庫裡，而
> GitHub 的 fork network **共用物件庫**，所以一個只存在於 fork 的 head 也可能被
> 上游的 upload-pack 供應出來，會把 fork 自有的 commit 誤判成上游的。改用取得
> 上游真實 ref 後做 merge-base 可達性檢查。**結論未變，證據強度變了。**

**二、從未被推送過**

`pushed_at`（2026-02-02T23:45:00Z）**早於** `created_at`
（2026-02-03T06:23:19Z）。這是 fork 建立後從未被推送過的特徵——該欄在建立時
承襲上游最後一次推送的時間。

**三、沒有任何建構掛在本帳號名下**

```
$ gh api repos/dofaromg/-postgrest/actions/runs --jq .total_count
0
```

該 fork 的 `ci.yaml` 在 push 到 `main` 時觸發、`release.yaml` 在推 `v*` tag
時觸發。目前零自有 commit、零 tag、零執行紀錄，所以**從來沒有任何建構以
`dofaromg` 名義跑過**。

**若該 fork 的 Actions 是啟用狀態**，往它推一次就會以本帳號名義執行。
這是條件句而不是斷言——Actions 的啟用狀態本工作階段讀不到，見下。

讀不到的部分照實記錄——`repos/dofaromg/-postgrest/actions/permissions`
在本工作階段被擋，原文：

```
Access to this GitHub Actions path is not permitted through this proxy. (HTTP 403)
```

所以「Actions 開關目前是開還是關」**未確認**；上面那個 0 是執行紀錄筆數，
不是開關狀態。

**四、關鍵字搜尋**

全樹搜尋 `mrl` / `mrliou` / `MRL` / `mrl_`（不分大小寫，排除 `.git`）：

```
命中檔案數：0
```

`.github/` 內搜尋 `attest` / `slsa` / `provenance`：

```
命中檔案數：0
```

依本帳本 2026-09-26 的更正，關鍵字零命中「不能作為內容來源比例或無本地變換的
證明」。**本條目不以關鍵字下結論**：無本地變換是由上面第一項的 git 層證據
確立的，關鍵字結果只作補充記錄。

### 判定與處置

- 著作權歸屬上游三位作者，MIT 授權。依 Upstream Boundary，
  **不得**列為 MRL 原創、不得列入 MRL canonical、不得反向主張。
- 若日後在 MRL 系統中使用，須同時保留 MIT 授權全文與三位作者的著作權聲明。
- 本輪**未將任何檔案匯入本倉庫**，也未對該 fork 推送、開 PR 或改設定
  ——只做核對與記錄。
- 倉庫名開頭的連字號是事實記錄。依 `registry/rules/naming_rules_v1.yaml`
  的 invariants 第一條「Original names are NEVER changed」，
  **本條目不處置它**；改不改倉庫名是權利人的決定。

### 這一筆與第 1 筆的關係

第 1 筆 `features-feature_terraform_1.4.2` 的建立日期是 **2026-02-02**，
本筆建立於 **2026-02-03**，日期相鄰。是否同一批次建立
**未經查核**，此處不作因果主張，只記錄時間相鄰這個事實，供日後清點
那「128 個帶 MRL／MrLiou 名稱的 fork」時對照。

與第 1 筆不同的是：本筆連名字都不帶 MRL 字樣。分類仍相同
——帳號下的純外部 fork，應標為 External Fork Reference，避免反向混淆。
