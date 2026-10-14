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

    mrl_owned         來源列自己標明屬於 MrLiouWord
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

ORIGIN_SIGNATURE = "MrLiouWord"

#: 來源列可能攜帶權威簽名的鍵名，母體鍵名（origin）排在前面優先採用。
ORIGIN_KEYS: Tuple[str, ...] = ("origin", "origin_signature")

MRL_OWNED = "mrl_owned"
FOREIGN_MARKED = "foreign_marked"
UNSIGNED_PENDING = "unsigned_pending"

#: 三態的固定順序，報告統計依此輸出，不隨 dict 插入順序漂移。
PROVENANCE_STATES: Tuple[str, ...] = (MRL_OWNED, FOREIGN_MARKED, UNSIGNED_PENDING)


def Mrliou_MRL_source_signatures(row: Mapping[str, Any]) -> Tuple[str, ...]:
    """回傳來源列上**所有**已填寫的權威簽名，依 ORIGIN_KEYS 順序。

    必須看全部而不是看到第一個就回傳：一列可能同時帶 origin 與
    origin_signature（例如合併過或遷移到一半的列），兩者有可能互相矛盾。
    只看第一個會讓 origin="MrLiouWord" 掩護掉另一欄的他方簽名，LAW-0 就被繞過。

    空字串與僅含空白的值一律視為沒有簽名，不當成有效權威。
    """
    found = []
    for key in ORIGIN_KEYS:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
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

    檢查所有已填寫的簽名欄位，**任何一個**不是 MrLiouWord 就判為
    foreign_marked——包含兩欄互相矛盾的情況（例如 origin="MrLiouWord" 搭配
    origin_signature="SomeOtherVendor"）。矛盾即他方：寧可擋下來讓人確認，
    也不要讓一半是他方的列被當成 MRL 自有。
    """
    signatures = Mrliou_MRL_source_signatures(row)
    if not signatures:
        return UNSIGNED_PENDING
    if all(signature == ORIGIN_SIGNATURE for signature in signatures):
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
