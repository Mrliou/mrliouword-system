"""Mrliou MRL 來源權威判定（溯源）。

module: Mrliou_MRL_Provenance_v1
version: 1.0.0
origin_signature: MrLiouWord
particle: fx.meta.origin  (溯源 / 追溯根本來源, dom=meta, act=trace_origin)

對應母體：core/particle_dict.json 的 `fx.meta.origin`。本模組不新增 schema、
不改資料庫，只回答一件事——「這一列資料的權威屬於誰」。

為什麼需要它（修補的缺陷）：
    原本 SystemAAdapter._validate_row_origin 只在「欄位存在且值不對」時拒絕，
    欄位不存在就放行；接著 to_unified 無條件寫入 origin_signature=MrLiouWord。
    結果是未簽名的第三方資料被蓋上 MRL 的章，而「來源本來沒有簽名」這個事實
    被抹掉。那是替他方資料製造 MRL 權威，必須擋掉。

本模組把來源出身分成三態，只判定、只記錄，不刪除也不覆蓋來源列（LAW-2）：

    mrl_owned         來源列自己標明屬於本權威（mrliou / mrliouword / MRL /
                      Mr.liou 任一別名皆可，見 Mrliou_MRL_Identity_v1）
    foreign_marked    來源列標了別人的簽名 → 由呼叫端拒絕
    unsigned_pending  來源列完全沒有簽名欄位 → 轉換但記錄，不升格為 MRL 權威

「unsigned_pending」刻意不叫「unknown」或「invalid」：依喚醒規則，看不到的歸
「待找回」，不歸「不存在」，也不得逕自升格為自有。

命名鍵相容（缺陷 D）：母體 core/particle_dict.json 與
core/ai_world_particle_personality_registry.json 用的鍵是 `origin`，
本模組 MRL_SystemA_ParticleLayer 用的是 `origin_signature`。兩者指同一個權威，
這裡兩個鍵都認，母體鍵名（origin）優先。
"""

from __future__ import annotations

from typing import Any, Mapping, Optional, Tuple

try:  # 套件內匯入（從母體 import modules.MRL_SystemA_ParticleLayer 時）
    from .Mrliou_MRL_Identity_v1 import (
        AUTHORITY_ALIASES,
        ORIGIN_SIGNATURE,
        RESERVED_NAMES,
        Mrliou_MRL_is_own_authority,
        Mrliou_MRL_normalize_authority,
    )
except ImportError:  # 相容既有用法：cd 進本目錄後直接 import
    from Mrliou_MRL_Identity_v1 import (  # type: ignore[no-redef]
        AUTHORITY_ALIASES,
        ORIGIN_SIGNATURE,
        RESERVED_NAMES,
        Mrliou_MRL_is_own_authority,
        Mrliou_MRL_normalize_authority,
    )

__all__ = [
    "AUTHORITY_ALIASES",
    "FOREIGN_MARKED",
    "MRL_OWNED",
    "ORIGIN_KEYS",
    "ORIGIN_SIGNATURE",
    "PROVENANCE_STATES",
    "RESERVED_NAMES",
    "UNSIGNED_PENDING",
    "Mrliou_MRL_classify_source",
    "Mrliou_MRL_is_foreign",
    "Mrliou_MRL_is_own_authority",
    "Mrliou_MRL_locate",
    "Mrliou_MRL_normalize_authority",
    "Mrliou_MRL_source_signature",
    "Mrliou_MRL_source_signature_values",
    "Mrliou_MRL_source_signatures",
]

#: 來源列可能攜帶權威簽名的鍵名，母體鍵名（origin）排在前面優先採用。
ORIGIN_KEYS: Tuple[str, ...] = ("origin", "origin_signature")

MRL_OWNED = "mrl_owned"
FOREIGN_MARKED = "foreign_marked"
UNSIGNED_PENDING = "unsigned_pending"

#: 三態的固定順序，報告統計依此輸出，不隨 dict 插入順序漂移。
PROVENANCE_STATES: Tuple[str, ...] = (MRL_OWNED, FOREIGN_MARKED, UNSIGNED_PENDING)


def Mrliou_MRL_source_signature_values(row: Mapping[str, Any]) -> Tuple[Any, ...]:
    """回傳來源列上所有「有填東西」的簽名欄位的**原值**，依 ORIGIN_KEYS 順序。

    判定權威必須看原值，不能先 str()。摺疊會去掉所有非英數字元，所以
    str(["MRL"]) == "['MRL']" 摺完就是 "mrl"，命中別名——一個 list 就取得了
    MRL 權威。Mrliou_MRL_source_signatures 回字串是給顯示與紀錄用的，
    Mrliou_MRL_classify_source 走這一支。

    「有填東西」的定義：不是 None；若是字串，則去空白後非空且至少有一個
    英數字元（純符號如 "___" 裡沒有任何人的名字，算沒有簽名）。非字串只要
    不是 None 就算有填——欄位裡有東西，只是不是本權威的簽名。
    """
    found = []
    for key in ORIGIN_KEYS:
        value = row.get(key)
        if value is None:
            continue
        if isinstance(value, str):
            text = value.strip()
            if text and any(ch.isalnum() for ch in text):
                found.append(value)
            continue
        found.append(value)
    return tuple(found)


def Mrliou_MRL_source_signatures(row: Mapping[str, Any]) -> Tuple[str, ...]:
    """回傳來源列上**所有**已填寫的權威簽名，依 ORIGIN_KEYS 順序。

    必須看全部而不是看到第一個就回傳：一列可能同時帶 origin 與
    origin_signature（例如合併過或遷移到一半的列），兩者有可能互相矛盾。
    只看第一個會讓 origin="MrLiouWord" 掩護掉另一欄的他方簽名，LAW-0 就被繞過。

    空字串、僅含空白、以及摺疊後一個英數字元都不剩的值（例如 "___"、"--"）
    一律視為**沒有簽名**，不當成有效權威。

    最後那一類刻意不判成他方：`origin="___"` 裡沒有任何人的名字，說它是
    「別人的簽名」就是在無憑據下指控第三方，而那會直接把一列資料送進
    HISTORICAL_AUTHORITY_AUDIT 的追償流程。依喚醒規則，看不到的歸
    「待找回」，所以它歸 unsigned_pending。注意摺疊只去掉符號——中日韓文字
    的 isalnum() 為真，所以中文簽名不會被誤殺。
    """
    found = []
    for key in ORIGIN_KEYS:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text and any(ch.isalnum() for ch in text):
            found.append(text)
    return tuple(found)


def Mrliou_MRL_source_signature(row: Mapping[str, Any]) -> Optional[str]:
    """回傳來源列的首選權威簽名（母體鍵名 origin 優先）；沒有時回 None。

    這是給顯示與紀錄用的便利函式。判定權威請用
    Mrliou_MRL_classify_source，它會檢查全部簽名欄位而不只是第一個。
    """
    signatures = Mrliou_MRL_source_signatures(row)
    return signatures[0] if signatures else None


def Mrliou_MRL_classify_source(row: Mapping[str, Any]) -> str:
    """判定來源列的出身，回傳 PROVENANCE_STATES 之一。

    檢查所有已填寫的簽名欄位，**任何一個**不屬於本權威就判為 foreign_marked
    ——包含兩欄互相矛盾的情況（例如 origin="MrLiouWord" 搭配
    origin_signature="SomeOtherVendor"）。矛盾即他方：寧可擋下來讓人確認，
    也不要讓一半是他方的列被當成 MRL 自有。

    「屬於本權威」走 Mrliou_MRL_Identity_v1 的別名集，不是字面相等：
    mrliou = mrliouword = MRL = Mr.liou 是同一個權威（依
    .mrliou/authority-lock.json 的 reserved_names）。改成字面相等會讓簽
    `MrLiou` 或 `MRL` 的自有資料被判他方並被拒絕轉換——那是把權威自己的
    資料擋在門外，與放行他方資料一樣是權威錯位。
    """
    values = Mrliou_MRL_source_signature_values(row)
    if not values:
        return UNSIGNED_PENDING
    if all(Mrliou_MRL_is_own_authority(value) for value in values):
        return MRL_OWNED
    return FOREIGN_MARKED


def Mrliou_MRL_is_foreign(row: Mapping[str, Any]) -> bool:
    """來源列是否標了別人的簽名（應由呼叫端拒絕轉換）。"""
    return Mrliou_MRL_classify_source(row) == FOREIGN_MARKED


def Mrliou_MRL_locate(row: Mapping[str, Any], fallback: str) -> str:
    """取出一列的可定位識別碼，用於報告逐筆定位。

    依 LAW-2「只定位、不刪除」，報告必須能指回原列，所以這裡只讀既有欄位，
    找不到時回傳呼叫端給的 fallback（例如 row-7），絕不自造 id 寫回來源。
    """
    for key in ("id", "seed_id", "uuid", "key"):
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value)
    return fallback
