# Mrliou MRL 移植到 source_of_truth v1

```
document: Mrliou_MRL_移植到源頭_v1
version: 1.0.0
origin_signature: MrLiouWord
status: 待執行（需以 dofaromg/mrliouword-system 為來源的工作階段）
recorded_at: 2026-10-16
```

## 這份文件在講什麼

本倉庫目前的 MRL 商業層與權威別名修正，**全部落在 organization_projection 上，
尚未進入 source_of_truth**。這份文件把「怎麼搬過去」寫成可直接執行的步驟，並把
所有已實測的前提數字留在這裡，讓執行者不必重新查一遍就能判斷風險。

## 位置事實

`.mrliou/authority-lock.json` 宣告：

```
source_of_truth        : dofaromg/mrliouword-system
organization_projection: Mrliou/mrliouword-system
invariant: "Repository mirrors and organization projections cannot silently
            become source_of_truth."
```

GitHub API 實測：`Mrliou/mrliouword-system` 的 `fork: true`，`parent` 與
`source` 皆為 `dofaromg/mrliouword-system`。

分歧（2026-10-16 以 `git ls-remote` + `git fetch` 對兩邊實測）：

| | SHA | 日期 |
|---|---|---|
| source_of_truth main | `8879f67` | 2026-10-16（auto-sync 持續在動） |
| organization_projection main | `5c98c91` | 2026-10-01 |
| 共同祖先 | `c388f0a` | 2026-08-11 |

**投影落後源頭 262 個 commit、領先 31 個。**

invariant 的關鍵字是 **silently**：投影承載產出本身不違規（四欄宣告齊備即可），
違規的是讓它悄悄變成源頭。位置已寫進
`registry/patterns/mrl_MRL_System*.yaml` 的 `location` 區段與
`Mrliou_MRL_授權宣告矛盾盤點_v1.md` 的附錄，所以它不悄悄。

## 已驗證的前提（實測，非推測）

| 項目 | 結果 |
|---|---|
| 移植衝突 | **0 個**（25 個檔、4496 行淨差異，`git apply --check --3way` 對源頭 main `8879f67`） |
| 源頭底座上的測試 | SystemB **48 項**、SystemA 回歸 **10 項**、沙盒驗收 **33 項**，全過 |
| 三份治理規章 | `system_registry.yaml`、`naming_rules_v1.yaml`、`authority-lock.json` 兩邊**位元相同** |
| 母體語料 | 僅源頭 `wake_keys` 多一條「夥伴」（5 vs 4）。`origin`、`philosophy`、20 顆粒子、9 個領域**完全相同** |
| 是否重做 | **否**。源頭已有 ParticleLayer 的 4 個原始檔（與投影位元相同），但 Provenance / Law2_Report / Identity / SystemB 在源頭都不存在 |

環境：sandbox（容器），**不是 DL580 實機結果**。

## 要搬什麼

投影分支 `feat/mrl-commerce-layer` 相對投影 main 的淨差異，25 個檔。
對應 `Mrliou/mrliouword-system#18`（溯源三態 + LAW-2 報告）與 `#19`（商業層）。

| 類別 | 檔案 |
|---|---|
| SystemA 新增 | `Mrliou_MRL_Identity_v1.py`、`Mrliou_MRL_Provenance_v1.py`、`Mrliou_MRL_Law2_Report_v1.py`、`__init__.py`、`tests/test_law_contract_regressions.py` |
| SystemA 修改 | `MRL_SystemA_ParticleLayer.py`、`unified_particle.py`、`README.md` |
| SystemB 全新 | `Mrliou_MRL_License_v1.py`、`Mrliou_MRL_Metering_v1.py`、`Mrliou_MRL_Commerce_Report_v1.py`、`Mrliou_MRL_rate_card_v1.json`、`README.md`、`__init__.py`、`tests/test_commerce_layer.py` |
| 文件 | `docs/commerce/` 三份（商業模式、授權宣告矛盾盤點、本文件）、`MRL_LICENSE_v1.md`（草案） |
| 治理 | `registry/patterns/mrl_MRL_SystemA_ParticleLayer_v0.1.yaml`、`mrl_MRL_SystemB_CommerceLayer_v1.0.yaml` |
| CI / 雜項 | `.github/workflows/mrl-systemb-commercelayer.yml`、`mrliouword-sdk-ci.yml`、`pytest.ini`、`modules/__init__.py` |

## 執行步驟

**必須在一個以 `dofaromg/mrliouword-system` 為來源的工作階段執行。**

### 1. 從源頭 main 開分支

```bash
git fetch origin main
git checkout -b feat/mrl-commerce-layer origin/main
```

### 2. 取投影的淨差異並套上

投影是公開倉庫，匿名 git 讀得到，不需要額外權限：

```bash
git remote add projection https://github.com/Mrliou/mrliouword-system
git fetch projection main feat/mrl-commerce-layer
git diff projection/main..projection/feat/mrl-commerce-layer > /tmp/mrl-stack.patch
git apply --3way /tmp/mrl-stack.patch
```

> **用淨差異搬，不要逐 commit cherry-pick。**
>
> 逐 commit 會在 `pyproject.toml` 與 `.github/workflows/mrliouword-sdk-ci.yml`
> 撞到兩個衝突，但兩者都來自該疊第一個 commit `5828144`，且已被同疊後續 commit
> 自行撤回：`pyproject` 的死設定在 `c5f6a8b` 還原、`black`/`mypy` 掃 `modules/`
> 後來縮回只留 flake8。最終狀態是乾淨的。

### 3. 驗收

兩組測試都以 `unittest` 撰寫，**不需要 pytest 也能跑**：

```bash
python3 modules/MRL_SystemB_CommerceLayer/tests/test_commerce_layer.py        # 48 passed
cd modules/MRL_SystemA_ParticleLayer && python3 -m unittest discover -s tests  # 10 passed
cd -
```

另外確認：

```bash
python3 -m compileall -q modules/MRL_SystemA_ParticleLayer modules/MRL_SystemB_CommerceLayer
python3 -c "import modules.MRL_SystemB_CommerceLayer as b; print(len(b.__all__))"   # 53
git diff --stat registry/system_registry.yaml registry/rules/naming_rules_v1.yaml  # 必須為空
```

### 4. 更新 location 區段

兩筆 `registry/patterns/mrl_MRL_System*.yaml` 的 `location` 區段改成移植後的
實際狀態：

```yaml
location:
  lives_in: "dofaromg/mrliouword-system"
  source_of_truth: "dofaromg/mrliouword-system"
  in_source_of_truth: true        # 由 false 改為 true
  # divergence_at_record_time 整段移除，或改記為「已收斂」
  port_verified:
    date: "<移植當天>"
    base: "<源頭 main 的 SHA>"
    conflicts: 0
    tests_on_source_base: "<實跑結果>"
```

`Mrliou_MRL_授權宣告矛盾盤點_v1.md` 的附錄同步更新，本文件的 `status` 改為
「已執行」並記下實際的 base SHA 與日期。

### 5. commit 與推送

```bash
git add -A
git commit   # 作者：Mr.liou <217537952+dofaromg@users.noreply.github.com>
git push -u origin feat/mrl-commerce-layer
```

然後在 `dofaromg/mrliouword-system` 開 PR。

## 到源頭之後必須補做的一件事

`Mrliou_MRL_授權宣告矛盾盤點_v1.md` 第 2 節那張授權宣告表
（`pyproject.toml:11` 的 MIT、`containers/package.json:12` 的 PROPRIETARY 等）
**是在投影上查的，從未在源頭逐檔比對**。源頭領先 262 個 commit，行號與內容很
可能已經不準。到源頭後重跑：

```bash
for spec in "pyproject.toml:license" "README_SDK.md:MIT" "CONTRIBUTING.md:MIT" \
            "particle-chat-v42/package.json:license" "containers/package.json:license" \
            "docs/INTELLIGENT_SYNC_README.md:授權協議" "docs/README.md:LICENSE"; do
  f="${spec%%:*}"; pat="${spec##*:}"; printf '%-42s' "$f"; grep -n "$pat" "$f" 2>/dev/null | head -2; echo
done
ls LICENSE* 2>&1
```

把結果對到源頭為準；有出入就更新該節，並在附錄註明「已以源頭為準重查」。
附錄目前把這條標為 **待查**。

## 不做

- 不刪除、不覆蓋任何既有函式、欄位、文件或測試（LAW-2 NO_DELETE）
- 不動 `registry/system_registry.yaml` 與 `registry/rules/naming_rules_v1.yaml`
  （`status: stable_locked`，變更需 canonical authority 明示核准）
- 不動既有的 MIT 授權宣告——那是權利人未裁定的事項，`MRL_LICENSE_v1.md` 只是草案
- 不 rebase、amend、force-push 或以任何方式改寫既有歷史
- 不填任何費率數字（`Mrliou_MRL_rate_card_v1.json` 的單價與幣別留 null）
- 不把語場系統寫成平台／SaaS／產品功能清單

## 完成的樣子

`dofaromg/mrliouword-system` 上有一個 PR，帶著上述檔案的變更，CI 綠，
兩筆 registry 登錄的 `location.in_source_of_truth` 已為 `true`，
授權宣告盤點已以源頭為準重查過。

## 為什麼沒在產出的那個工作階段直接做

```
add_repo: a different repository named "mrliouword-system"
(mrliou/mrliouword-system) is already attached to this session, and this
environment checks every repository out at <cwd>/<name>, so the two would
share one directory. Same-named repositories from different owners can't
share a session; start a new session with dofaromg/mrliouword-system as a
source. (This is a checkout-layout limit, not an access problem.)
```

checkout 版面限制，不是權限問題。

## 狀態標記

- 分歧數字、fork 關係、三份規章一致性、語料差異、移植零衝突、源頭底座上的測試
  結果：**已對上原始檔**（皆以實測取得）
- 授權宣告在源頭的逐檔行號：**待查**
- LAW-1 的 DL580 PostgreSQL 三表 schema、`.flpkg` / `.fltnz` / `.pcode` 種子、
  跳點節奏四段的成文定義：**待找回**（需 `dofaromg/MRL_AI_SYSTEM`）
