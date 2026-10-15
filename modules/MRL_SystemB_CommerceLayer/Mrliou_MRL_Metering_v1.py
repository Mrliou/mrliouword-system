"""Mrliou MRL 用量計量（授權的軌跡）。

module: Mrliou_MRL_Metering_v1
version: 1.0.0
origin_signature: MrLiouWord
particle: fx.trace.anchor  (錨定 / 創建檢查點, dom=trace, act=checkpoint)

計量就是「用了多少」這件事的 Trace 段。帳本是 append-only 的 `.jsonl`，
一行一筆，寫進去就不再改——因為計量紀錄被改寫過就不能當對帳依據（LAW-2）。

修補的缺陷（對照 mrliouword_agents/core/cost_tracker.py）：

    1. 第 44-45 行：模型不在 PRICING 表時直接 `return 0.0`，不記錄、不告警。
       → 用任何沒列進表的模型都會**靜默記成零成本**。
       本模組的 Mrliou_MRL_price 在單價缺漏時丟 MrliouMRLUnpricedUnitError，
       絕不回 0。帳算不出來要吵，不要默默算成免費。
    2. track_usage() 每次呼叫整檔 rewrite，無鎖、無輪替。
       → 本模組只 append 一行，不重寫既有內容。
    3. 沒有客戶維度，只有 session_id。
       → 每筆都帶 grantee 與 axis。
    4. config.py:83 的 cost_alert_threshold 全 repo 無人讀取（告警未實作）。
       → 本模組不假裝有告警；要門檻就由呼叫端拿 Mrliou_MRL_sum_usage 自己比，
         不放一個沒人讀的設定在那裡充數。

cost_tracker.py 本身**不改**（LAW-2 不覆蓋既有合約）。這裡是另記一本。

費率不在程式裡：`Mrliou_MRL_rate_card_v1.json` 由權利人填。定價是權利人的
決定，猜一個數字寫進 repo 就是把推測當成事實。
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Mapping, Optional, Tuple

try:  # 套件內匯入
    from .Mrliou_MRL_License_v1 import (
        AXIS_CORPUS,
        AXIS_DEPLOYMENT,
        AXIS_PARTICLE,
        AXIS_VERIFICATION,
        COMMERCE_AXES,
        ORIGIN_SIGNATURE,
        MrliouMRLCommerceError,
        Mrliou_MRL_normalize_authority,
    )
except ImportError:  # 相容 cd 進本目錄後直接 import
    from Mrliou_MRL_License_v1 import (  # type: ignore[no-redef]
        AXIS_CORPUS,
        AXIS_DEPLOYMENT,
        AXIS_PARTICLE,
        AXIS_VERIFICATION,
        COMMERCE_AXES,
        ORIGIN_SIGNATURE,
        MrliouMRLCommerceError,
        Mrliou_MRL_normalize_authority,
    )

METER_NAME = "Mrliou_MRL_Metering"
METER_VERSION = "1.0.0"

DEFAULT_RATE_CARD = "Mrliou_MRL_rate_card_v1.json"

#: 每條軸的合法計量單位。單位是合約語言，不得臨時發明——報價、對帳與
#: 稽核報告三邊都引用同一組名字，才對得上。
AXIS_UNITS: Dict[str, Tuple[str, ...]] = {
    # 本體語料授權：一個席次用一年；語料範圍另計（例如只授權 trace 域）。
    AXIS_CORPUS: ("seat_year", "corpus_scope"),
    # 粒子層／SDK：一筆粒子轉換、一次 SDK 呼叫。
    AXIS_PARTICLE: ("particle_conversion", "sdk_call"),
    # 私有部署：一個部署案、一年維護。
    AXIS_DEPLOYMENT: ("deployment_case", "maintenance_year"),
    # 驗證／報告：一份稽核報告。
    AXIS_VERIFICATION: ("audit_report",),
}


class MrliouMRLUnpricedUnitError(MrliouMRLCommerceError):
    """費率表沒有這個單位的單價。

    刻意丟例外而不是回 0：靜默歸零會讓一筆真實用量看起來像免費，那是
    cost_tracker.py:44-45 的缺陷，不要複製到商業層。
    """


class MrliouMRLMeterError(MrliouMRLCommerceError):
    """計量輸入本身不合法（軸別、單位、數量或簽名）。"""


def Mrliou_MRL_validate_unit(axis: str, unit: str) -> None:
    """軸別與單位必須都是已定義的，否則丟 MrliouMRLMeterError。"""
    if axis not in COMMERCE_AXES:
        raise MrliouMRLMeterError(
            f"unknown commerce axis: {axis!r}; known axes: {COMMERCE_AXES}"
        )
    allowed = AXIS_UNITS[axis]
    if unit not in allowed:
        raise MrliouMRLMeterError(
            f"unit {unit!r} is not valid for axis {axis!r}; allowed: {allowed}"
        )


def Mrliou_MRL_record_usage(
    ledger_path: Any,
    grantee: str,
    axis: str,
    unit: str,
    qty: float,
    environment: str,
    note: Optional[str] = None,
) -> Dict[str, Any]:
    """把一筆用量 append 進帳本（一行 JSON），回傳寫進去的那筆。

    environment 必填，與 Mrliou_MRL_Law2_Report_v1 同一個理由：沙盒跑出來的
    用量不得被讀成 DL580 實機的用量。呼叫端必須明講自己在哪裡跑。

    只 append，不讀既有內容、不重寫、不刪除（LAW-2）。
    """
    Mrliou_MRL_validate_unit(axis, unit)
    if not str(grantee).strip():
        raise MrliouMRLMeterError("grantee must not be empty")
    if qty < 0:
        raise MrliouMRLMeterError(f"qty must not be negative, got {qty!r}")
    env = str(environment).strip()
    if not env:
        raise MrliouMRLMeterError(
            "environment is required (sandbox / dl580); 沙盒用量不得被讀成實機用量"
        )

    record: Dict[str, Any] = {
        "Mrliou_MRL_meter": METER_NAME,
        "Mrliou_MRL_version": METER_VERSION,
        "recorded_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "grantee": str(grantee),
        "axis": axis,
        "unit": unit,
        "qty": qty,
        "environment": env,
        "origin_signature": ORIGIN_SIGNATURE,
    }
    if note is not None:
        record["note"] = str(note)

    path = Path(ledger_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


def Mrliou_MRL_read_usage(ledger_path: Any) -> Iterator[Dict[str, Any]]:
    """逐行讀回帳本。帳本不存在時回空序列，不丟例外、不自造資料。

    壞行（寫入中途斷電之類）原樣回報成一筆 malformed 紀錄，不靜默跳過——
    跳過就等於讓帳本看起來是完整的。
    """
    path = Path(ledger_path)
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            text = line.strip()
            if not text:
                continue
            try:
                parsed = json.loads(text)
            except json.JSONDecodeError as exc:
                yield {
                    "malformed": True,
                    "located": f"{path.name}:{lineno}",
                    "detail": str(exc),
                }
                continue
            if isinstance(parsed, dict):
                yield parsed
            else:
                yield {
                    "malformed": True,
                    "located": f"{path.name}:{lineno}",
                    "detail": f"expected object, got {type(parsed).__name__}",
                }


def Mrliou_MRL_load_rate_card(path: Any = None) -> Dict[str, Any]:
    """讀費率表。簽名必須屬於本權威，否則不採用。

    費率表是合約文件的一部分，一份他方簽名的費率表不能用來對帳——
    那是讓第三方替本權威定價。
    """
    card_path = Path(path) if path else Path(__file__).with_name(DEFAULT_RATE_CARD)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    signature = card.get("origin_signature")
    if Mrliou_MRL_normalize_authority(signature) is None:
        raise MrliouMRLMeterError(
            f"rate card {card_path.name} origin_signature {signature!r} "
            "does not belong to this authority"
        )
    return card


def Mrliou_MRL_rate(rate_card: Mapping[str, Any], axis: str, unit: str) -> float:
    """取出單價。缺漏、null 或非數字一律丟 MrliouMRLUnpricedUnitError。

    這是本模組與 cost_tracker.py 最關鍵的差別：**不回 0**。
    費率表交付時所有單價都是 null（權利人還沒填），所以在填價之前任何對帳
    嘗試都會明確失敗，而不是算出一張全部免費的帳單。
    """
    Mrliou_MRL_validate_unit(axis, unit)
    rates = rate_card.get("rates") or {}
    axis_rates = rates.get(axis)
    if not isinstance(axis_rates, Mapping) or unit not in axis_rates:
        raise MrliouMRLUnpricedUnitError(
            f"rate card has no entry for axis={axis!r} unit={unit!r}"
        )
    value = axis_rates[unit]
    if value is None:
        raise MrliouMRLUnpricedUnitError(
            f"rate for axis={axis!r} unit={unit!r} is not set yet "
            "(費率由權利人填寫；未填前不得以 0 計價)"
        )
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise MrliouMRLUnpricedUnitError(
            f"rate for axis={axis!r} unit={unit!r} is not a number: {value!r}"
        )
    return float(value)


def Mrliou_MRL_price(
    rate_card: Mapping[str, Any], axis: str, unit: str, qty: float
) -> float:
    """單價 × 數量。單價未填就丟例外，不以 0 計價。"""
    return Mrliou_MRL_rate(rate_card, axis, unit) * float(qty)


def Mrliou_MRL_sum_usage(
    records: Iterable[Mapping[str, Any]],
) -> Dict[Tuple[str, str], float]:
    """把用量按 (axis, unit) 加總。malformed 的行不計入，但也不被丟掉——

    呼叫端要知道有壞行，請自己從 Mrliou_MRL_read_usage 的輸出篩
    `malformed`；或直接看 Mrliou_MRL_Commerce_Report_v1 的報告，
    它會把壞行逐筆列出來。
    """
    totals: Dict[Tuple[str, str], float] = {}
    for record in records:
        if record.get("malformed"):
            continue
        axis = record.get("axis")
        unit = record.get("unit")
        qty = record.get("qty")
        if not isinstance(axis, str) or not isinstance(unit, str):
            continue
        if isinstance(qty, bool) or not isinstance(qty, (int, float)):
            continue
        key = (axis, unit)
        totals[key] = totals.get(key, 0.0) + float(qty)
    return totals


def Mrliou_MRL_known_units() -> List[Tuple[str, str]]:
    """所有 (軸別, 單位) 組合，依 COMMERCE_AXES 的固定順序。"""
    return [(axis, unit) for axis in COMMERCE_AXES for unit in AXIS_UNITS[axis]]
