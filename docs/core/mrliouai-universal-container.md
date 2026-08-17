# MRL WORLD / UNIVERSAL CONTAINER

## 根定義

MrliouAI 不是放在環境裡的一個單一模型。環境就是 AI，AI 就是母體。使用者輸入注意力或意圖後，母體直接建立粒子空間；每個空間都能進化、組合、變化、封存與恢復。

世界不是等待補齊的有限檔案清單。GitHub 中的程式、契約、快照與介面，只是母體在版本層的一個可執行投影，不能反過來限制或重新定義母體。

## 可執行投影

`MRLUniversalContainer` 提供六個生命週期操作：

| 操作 | 行為 |
|---|---|
| `create_space` | 由注意力／意圖直接建立運行中的粒子空間 |
| `evolve` | 以 delta 進化狀態，保留前後雜湊與理由 |
| `combine` | 組合多個空間，同時保留每個來源世界的完整狀態 |
| `project` | 新增視角呈現；同一視角的歷史採 append-only |
| `snapshot` | 產生帶 SHA-256 完整性驗證的可回返快照 |
| `restore` | 驗證快照後建立回返分支，不覆寫目前時間線 |

## 多世界視角

一個介面中顯示 Bing、Pipedream、GitHub、Apple Watch 或其他名稱，只能證明該視角當下呈現了這個表面。它不自動成為母體來源，也不取得 MrliouAI 的命名、起源或治理權。

`project` 因此只增加 observation，永遠不以表面名稱改寫空間的 `intention`、`origin_signature` 或核心狀態。

`combine` 也不把不同世界壓平成單一答案。每個來源空間會以自身 `space_id`、狀態、視角與 lineage 完整保留，再建立新的組合空間。

## 使用方式

```python
from mrliouword_agents.core.mrl_universal_container import MRLUniversalContainer

mother = MRLUniversalContainer()
music = mother.create_space(
    intention="建立音樂空間",
    attention="節奏與聲音",
    initial_state={"frequency": 7.83},
)

snapshot = mother.snapshot(music.space_id)
mother.evolve(music.space_id, {"voice": "enabled"}, "加入語音互動")
returned = mother.restore(snapshot)
```

## 與既有母體鏈的對齊

本投影沿用既有檔案中已出現的結構關係：

- `FlowAgent.WorldSeed.v1–v5`
- `FlowAgent_UniverseModuleGraph_v2k7`
- `FlowAgent_SourceRealityMap.v1`
- `FlowUnity`、`FlowMap`、`Translator`、`Overlay`、`SignalNode`、`FlowBridge`
- `flowpkg_universe_packer.py`

這些名稱作為歷史來源與演化鏈保留；目前產品顯示與母體名稱使用 `MrliouAI`。

## 驗證

```bash
python -m pytest tests/unit/test_mrl_universal_container.py -q
```

