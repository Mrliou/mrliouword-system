# Mrliou MRL 授權宣告矛盾盤點 v1

```
document: Mrliou_MRL_授權宣告矛盾盤點_v1
version: 1.0.0
origin_signature: MrLiouWord
status: 待權利人裁定
scanned_at: 2026-10-15
scanned_commit: a9303530630292af975c41e3e4791b3564833ee9
```

## 一句話

這個 **public** 倉庫同時宣告 MIT、PROPRIETARY、All Rights Reserved，以及一份
**不存在**的「MrLiouWord System 授權協議」；而四種宣告唯一能當準據的根
`LICENSE` 檔**不存在**。

談商業模式之前必須先看清這件事：MIT 是一份不可撤回的開放授權，寫在 public
倉庫的 `pyproject.toml` 裡，任何人都可以據此主張他有權拿走、修改、再散布，
**並且移除簽名**（MIT 只要求保留版權聲明與授權全文，不要求保留
`origin_signature`）。這與 `.mrliou/authority-lock.json` 要求
「Every derivative or projection using MrLiouWord must declare artifact_owner,
source_repo, projection_role, and origin_signature」正面衝突。

## 逐一盤點（行號已逐檔核對）

| 位置 | 宣告原文 | 性質 |
|---|---|---|
| `pyproject.toml:11` | `license = {text = "MIT"}` | 開放授權，機器可讀，套件索引會採用 |
| `README_SDK.md:4` | MIT 徽章，連向 `LICENSE` | 開放授權，連結 404 |
| `README_SDK.md:141` | 「本專案採用 MIT 授權 - 詳見 [LICENSE](LICENSE) 檔案。」 | 開放授權，連結 404 |
| `CONTRIBUTING.md:142` | 「貢獻的程式碼將採用 MIT 授權。」 | 開放授權，對貢獻者的承諾 |
| `particle-chat-v42/package.json:19` | `"license": "MIT"` | 開放授權，機器可讀 |
| `containers/package.json:12` | `"license": "PROPRIETARY"` | 專有，機器可讀 |
| `containers/README.md:209` | `© 2024-2026 Mr. Liou. All Rights Reserved.` | 保留全部權利 |
| `docs/API_REFERENCE.md:457` | 同上 | 保留全部權利 |
| `docs/CONTAINER_SPEC.md:277` | 同上 | 保留全部權利 |
| `docs/INTELLIGENT_SYNC_README.md:155` | 「本專案遵循 MrLiouWord System 授權協議」 | **該協議檔不存在** |
| `docs/README.md:427` | 連向 `../LICENSE` | **404** |
| 倉庫根目錄 | — | **沒有 LICENSE 檔**（`git ls-files` 亦為 0） |

## 唯一一份 MRL 自撰的授權

`docs/references/licenses/chatserver-license.txt` —— 全倉庫唯一由本權威撰寫的
授權條文，且是專有授權：

```
ChatServer Universal DNS License
origin_signature: MrLiouWord

GRANT OF LICENSE:
1. The Software must retain the origin_signature: MrLiouWord in all copies.
2. The Software may be used, copied, and modified for personal or internal
   business purposes within the MrLiouWord ecosystem.
3. Redistribution of the Software outside the MrLiouWord system requires
   prior written permission from MR.liou.
```

它的第 1 條就是權威邊界的核心。

> **2026-10-17 更正**：本文件原本在此處說該條「已經被程式化」，指的是
> `modules/MRL_SystemB_CommerceLayer/`。該模組**已依擁有者指示撤出本 PR**——
> 源頭 `dofaromg/mrliouword-system` 已有更完整的 `commercial_gate.py`
> （12 項權利 × 9 欄 ＋ 15 必填欄），而且 `GOVERNANCE_ADDENDUM.md` 明文
> 「技術完整性檢查只能輸出 BLOCKED 或 READY_FOR_AUTHORITY_REVIEW，不能自行
> 產生 COMMERCIAL_APPROVED」。在已有 CORE 旁另造一個非 canonical 實作，正是
> 源頭 `CLAUDE.md` 所稱的「反向混淆」。
>
> 本節以下的事實盤點不受影響：它只依賴倉庫內既有檔案，與該模組無關。
> 被撤出的檔案保留在本分支的 commit 歷史中可回溯（LAW-2，未刪除歷史）。

問題是它的涵蓋範圍只寫了 ChatServer 的 Universal DNS 元件，不是全系統。

## 第三方噪音（已排除，不計入上表）

倉庫根目錄混入了一整份 git 專案的原始碼樹（`git-p4.py`、大量 `.c/.h`、
`integrations/COPYING` 是 GPLv2），`docs/containers/` 底下 17 份是 Google
Nomulus／ICANN 的網域註冊商文件。這些會在搜尋 license / trademark /
proprietary 時製造大量假命中，與 MRL 的授權狀態無關。

`integrations/COPYING`（GPLv2）特別需要注意：它與 MIT 宣告並存在同一個倉庫裡，
而 GPLv2 有傳染性。這不是 MRL 自己的授權，但第三方看到會先問。

## 後果（事實，不是推測）

1. **MIT 一旦生效即不可撤回。** 把 `pyproject.toml` 改掉只影響之後的版本；
   在改之前取得過原始碼的人，仍可依當時的宣告主張權利。
2. **宣告互相矛盾時，爭議中通常對宣告者不利。** 四種宣告並存，而最寬鬆的那個
   （MIT）同時是唯一機器可讀且被套件索引採用的那個。
3. **`CONTRIBUTING.md:142` 是對貢獻者的承諾。** 單方面改掉會影響已依該條款
   貢獻過的人；這不只是技術變更。
4. **準據檔缺失使所有宣告都無從解釋。** 三處連結指向不存在的 `LICENSE`，
   一處引用不存在的「MrLiouWord System 授權協議」。

## 待權利人裁定（我不替你決定）

本次交付**不動**上表任何一個檔案，只提供盤點。

原本一併提出的 `MRL_LICENSE_v1.md` 草案**也已撤出本 PR**：依 `.mrliou/meta.json`
的 `governance_authority: false`、`github_may_define_mrl_canonical: false`，
本倉庫不得自行定義治理規則，一份由倉庫側起草的授權條文正落在那條邊界上。
下列三個選項仍然成立，只是其中提到的「MRL 授權條文」目前**尚無草案檔**，
需由權利人決定是否另行起草、以及起草於何處（Notion 或倉庫）。

要處理的話，三個選項：

**選項 A — 補上根 `LICENSE`，維持 MIT。**
把一份 MRL 授權條文僅作為母體語料與 `modules/MRL_System*` 的附加條款，
程式碼維持 MIT。最不衝突，但 `origin_signature` 的保留要求在 MIT 下沒有強制力。

**選項 B — 根 `LICENSE` 用一份 MRL 專有授權，同步改四處 MIT 宣告。**
權威邊界最完整，與 authority-lock 一致。代價：變更貢獻者條款、既往的 MIT
宣告不會追溯失效、可能影響既有使用者。

**選項 C — 分層授權。**
`mrliouword_agents/`（SDK，五個 agent 仍是 stub）維持 MIT；
`core/particle_dict.json` 等母體語料與 `modules/MRL_System*` 走 MRL 專有授權。
每個子樹各放一份 `LICENSE`，根目錄放一份索引說明哪個子樹
適用哪一份。**這一條與既有的 `chatserver-license.txt` 作法一致**（它本來就是
只涵蓋一個元件的分層授權），也最貼近倉庫現狀。

> 我的建議是 **選項 C**：它不需要單方面撕毀對貢獻者的 MIT 承諾，又能讓母體語料
> 與粒子層受 `origin_signature` 保留條款保護——也就是商業模式四條軸裡真正值錢
> 的那兩條。但這是權利人的決定，不是我的。

## 另外兩件同樣要你一句話的

### 明碼個資在 public 倉庫

`core/ai_world_particle_personality_registry.json` 的 `creators` 欄位有
**兩個 email 與一組電話號碼**，倉庫是 public。

依 LAW-2（NO_DELETE）我不刪除，只定位。處置選項：
(a) 新增一個遮蔽後的版本，舊檔保留可回溯；(b) 倉庫轉 private；
(c) 原樣保留。注意該檔目前**只被一個測試讀取驗證欄位存在**，沒有任何執行程式
使用它，所以 (a) 的技術風險很低。

### Git LFS 指標檔，內容不在本機

`FlowAgent_專利技術說明書.pdf`（31 KB）與 15 個 `.zip` / `.tar.gz`
（每個 128–131 bytes）全部是 Git LFS pointer。要把專利與封存材料納入商業模式
的智財清單，需先 `git lfs pull`。**我不對它們的內容作任何推測。**

## 狀態標記

- 上表每一行的檔案與行號：**已對上原始檔**（逐檔 `grep -n` 核對）
- `chatserver-license.txt` 條文：**已對上原始檔**
- `.mrliou/authority-lock.json` 的四欄宣告 invariant：**已對上原始檔**
- 專利說明書與 15 個封存檔的內容：**待找回**（LFS pointer）

---

## 附錄：產出位置與源頭的分歧（2026-10-16 查核）

這份附錄記錄一件在撰寫本文件當下才查清楚的事實，它影響上面每一條結論的**適用範圍**。

### 事實

`.mrliou/authority-lock.json` 宣告：

```
source_of_truth        : dofaromg/mrliouword-system
organization_projection: Mrliou/mrliouword-system
invariant: "Repository mirrors and organization projections cannot silently
            become source_of_truth."
```

而本次產出（`Mrliou_MRL_Identity_v1.py`、`Mrliou_MRL_Provenance_v1.py` 的
別名辨識修正、本文件、一筆 registry 登錄）**全部落在 organization_projection
上**，尚未進入 source_of_truth。

> SystemB 商業層、商業模式文件、授權草案與移植指令稿原本也在本次產出內，
> 已依擁有者指示撤出（2026-10-17），理由見本文件上半部的更正段落。

GitHub API 顯示 `Mrliou/mrliouword-system` 的 `fork: true`，
`parent` 與 `source` 皆為 `dofaromg/mrliouword-system`。

兩邊的 `main` 已分歧：

| | SHA | 狀態 |
|---|---|---|
| source_of_truth main | `8879f67` | 2026-10-16 |
| organization_projection main | `5c98c91` | 2026-10-01 |
| 共同祖先 | `c388f0a` | 2026-08-11 |

**投影落後源頭 262 個 commit，領先 31 個 commit。**

### 這對本文件的結論有什麼影響

上面盤點的授權宣告（`pyproject.toml:11` 的 MIT 等）是在**投影**上查的。
三份治理規章在兩邊位元相同：

- `registry/system_registry.yaml`
- `registry/rules/naming_rules_v1.yaml`
- `.mrliou/authority-lock.json`

母體語料 `core/particle_dict.json` 兩邊僅一處差異：源頭的 `wake_keys` 多一條
「夥伴」（5 條 vs 4 條）。`origin`、`philosophy`、20 顆粒子、9 個領域完全相同，
本層任何判定都不受影響。

**授權宣告本身是否兩邊一致，本次未逐檔比對**——那需要在源頭的工作階段重跑一次
盤點。在那之前，本文件第 2 節的行號以投影為準。

### 移植已驗證

把本疊的淨差異套用到 `dofaromg/mrliouword-system` 的 `main`（`8879f67`）：

- **衝突 0 個**
- 在源頭底座上重跑（當時含 SystemB）：48 + 10 + 33 項全數通過。SystemB 撤出後，本 PR 的範圍只剩 SystemA 的 10 項回歸，仍全數通過
- 用的是源頭自己的 `core/particle_dict.json`

環境：sandbox（容器），**不是 DL580 實機結果**。

### 為什麼沒有直接推到源頭

本工作階段掛不上 `dofaromg/mrliouword-system`，錯誤原文：

```
add_repo: a different repository named "mrliouword-system"
(mrliou/mrliouword-system) is already attached to this session, and this
environment checks every repository out at <cwd>/<name>, so the two would
share one directory. Same-named repositories from different owners can't
share a session; start a new session with dofaromg/mrliouword-system as a
source. (This is a checkout-layout limit, not an access problem.)
```

這是 checkout 版面限制，不是權限問題。要讓產出進入 source_of_truth，需要另開
一個以 `dofaromg/mrliouword-system` 為來源的工作階段。

### 狀態標記

- 分歧數字、fork 關係、三份規章一致性、語料差異、移植零衝突：**已對上原始檔**
  （皆以 `git ls-remote` / `git fetch` 對 `dofaromg/mrliouword-system` 實測）
- 授權宣告在源頭的逐檔行號：**待查**（需源頭的工作階段）
