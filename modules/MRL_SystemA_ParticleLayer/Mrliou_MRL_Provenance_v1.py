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


def Mrliou_MRL_source_signature(row: Mapping[str, Any]) -> Optional[str]:
    """回傳來源列自己攜帶的權威簽名；沒有任何簽名欄位時回 None。

    空字串與僅含空白的值一律視為沒有簽名，不當成有效權威。
    """
    for key in ORIGIN_KEYS:
        value = row.get(key)
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return None


def Mrliou_MRL_classify_source(row: Mapping[str, Any]) -> str:
    """判定來源列的出身，回傳 PROVENANCE_STATES 之一。"""
    signature = Mrliou_MRL_source_signature(row)
    if signature is None:
        return UNSIGNED_PENDING
    if signature == ORIGIN_SIGNATURE:
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
