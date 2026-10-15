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

金額一律用 Decimal，不用二進位浮點：0.1 × 3 在 float 下是
0.30000000000000004，把那個數字當成商業金額呈現就是在說謊。費率從費率表讀出
時即轉成 Decimal（經由 str()，避免先變成 float 就已經失真），乘法與加總全程
在 Decimal 下進行，報告輸出精確的十進位字串。

四捨五入位數與方式刻意**不訂**：那和費率一樣是權利人的商業決定，程式不代訂。
報告給的是精確值，要怎麼進位由費率表日後宣告。

費率不在程式裡：`Mrliou_MRL_rate_card_v1.json` 由權利人填。定價是權利人的
決定，猜一個數字寫進 repo 就是把推測當成事實。
"""

from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
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


class MrliouMRLRateCardAuthorityError(MrliouMRLMeterError):
    """費率表的簽名不屬於本權威。

    費率表是合約文件的一部分。讓他方簽名的費率表能用來對帳，等於讓第三方替
    本權威定價——那和讓他方簽名的資料取得 MRL 權威是同一類錯位。
    """


def Mrliou_MRL_assert_rate_card_authority(rate_card: Mapping[str, Any]) -> None:
    """費率表的 origin_signature 必須屬於本權威，否則丟
    MrliouMRLRateCardAuthorityError。

    這支由 Mrliou_MRL_load_rate_card **和** Mrliou_MRL_rate 兩邊都呼叫。
    只在 load 檢查是不夠的：呼叫端完全可以自己 json.loads 或直接湊一個 dict
    傳進 Mrliou_MRL_rate / 報告 API，於是他方簽名的費率就被採用了。
    把檢查放在真正取價的那一步，才沒有繞道。
    """
    signature = rate_card.get("origin_signature")
    if Mrliou_MRL_normalize_authority(signature) is None:
        raise MrliouMRLRateCardAuthorityError(
            f"rate card origin_signature {signature!r} does not belong to "
            "this authority"
        )


def Mrliou_MRL_rate_card_currency(rate_card: Mapping[str, Any]) -> str:
    """回傳費率表宣告的幣別；未宣告或空白則丟 MrliouMRLUnpricedUnitError。

    單價填了但幣別沒填，報告就會印出「合計 5.0」這種沒有幣別的數字——
    那在商業上是無法解讀的，和「未填價以 0 計」是同一類毛病：一個看起來
    確定、實際上無法據以請款的數字。所以幣別與單價一樣是計價的前提。
    """
    currency = rate_card.get("currency")
    if not isinstance(currency, str) or not currency.strip():
        raise MrliouMRLUnpricedUnitError(
            f"rate card currency is not set ({currency!r}); "
            "幣別未填前不得輸出金額"
        )
    return currency.strip()


def Mrliou_MRL_to_decimal(value: Any, what: str) -> Decimal:
    """把費率表或帳本裡的數字轉成 Decimal，經由 str() 以免先失真。

    bool 不算數字（True 是 int 的子類，但 True 當金額沒有意義）；
    NaN 與 ±Inf 一律拒絕——它們能通過大小比較，卻會汙染整本帳。
    """
    if isinstance(value, bool) or not isinstance(value, (int, float, str, Decimal)):
        raise MrliouMRLMeterError(f"{what} is not a number: {value!r}")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise MrliouMRLMeterError(f"{what} is not a number: {value!r}") from exc
    if not result.is_finite():
        raise MrliouMRLMeterError(f"{what} must be finite, got {value!r}")
    return result


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
    if isinstance(qty, bool) or not isinstance(qty, (int, float)):
        raise MrliouMRLMeterError(f"qty must be a number, got {qty!r}")
    if not math.isfinite(qty):
        # json.dumps 會把這些寫成 NaN / Infinity——那不是合法 JSON，別的解析器
        # 讀不回來，而這是 append-only 的帳本：寫壞的那一行永遠在裡面。
        raise MrliouMRLMeterError(f"qty must be finite, got {qty!r}")
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
        # allow_nan=False 是第二道防線：萬一上面的檢查被繞過，寧可寫入失敗
        # 也不要讓一行非法 JSON 永久留在帳本裡。
        handle.write(
            json.dumps(record, ensure_ascii=False, allow_nan=False) + "\n"
        )
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
    try:
        Mrliou_MRL_assert_rate_card_authority(card)
    except MrliouMRLRateCardAuthorityError as exc:
        raise MrliouMRLRateCardAuthorityError(
            f"rate card {card_path.name}: {exc}"
        ) from exc
    return card


def Mrliou_MRL_rate(
    rate_card: Mapping[str, Any], axis: str, unit: str
) -> Decimal:
    """取出單價（Decimal）。缺漏、null 或非數字一律丟
    MrliouMRLUnpricedUnitError。

    這是本模組與 cost_tracker.py 最關鍵的差別：**不回 0**。
    費率表交付時所有單價都是 null（權利人還沒填），所以在填價之前任何對帳
    嘗試都會明確失敗，而不是算出一張全部免費的帳單。

    取價前先驗兩件事，缺一不可：
    - 費率表的簽名屬於本權威（否則第三方就替本權威定了價）
    - 費率表宣告了幣別（否則算出來的數字無法據以請款）
    """
    Mrliou_MRL_assert_rate_card_authority(rate_card)
    Mrliou_MRL_rate_card_currency(rate_card)
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
    try:
        return Mrliou_MRL_to_decimal(value, f"rate for {axis}/{unit}")
    except MrliouMRLMeterError as exc:
        raise MrliouMRLUnpricedUnitError(str(exc)) from exc


def Mrliou_MRL_price(
    rate_card: Mapping[str, Any], axis: str, unit: str, qty: Any
) -> Decimal:
    """單價 × 數量，全程 Decimal。單價未填就丟例外，不以 0 計價。"""
    rate = Mrliou_MRL_rate(rate_card, axis, unit)
    return rate * Mrliou_MRL_to_decimal(qty, "qty")


def Mrliou_MRL_usage_problem(record: Mapping[str, Any]) -> Optional[str]:
    """這一筆用量紀錄有什麼問題？沒有問題回 None。

    加總時不能靜默跳過有問題的列：一列 qty 寫成字串、或根本沒有 qty，
    跳過之後報告會說 PASS 而那筆真實用量憑空消失。本模組的合約是
    「壞行要被看見」，所以問題在這裡被講出來，由報告逐筆列出。
    """
    if record.get("malformed"):
        return str(record.get("detail") or "malformed ledger line")
    axis = record.get("axis")
    unit = record.get("unit")
    if not isinstance(axis, str) or not axis:
        return f"axis is missing or not a string: {axis!r}"
    if not isinstance(unit, str) or not unit:
        return f"unit is missing or not a string: {unit!r}"
    if axis not in COMMERCE_AXES:
        return f"unknown commerce axis: {axis!r}"
    if unit not in AXIS_UNITS[axis]:
        return f"unit {unit!r} is not valid for axis {axis!r}"
    qty = record.get("qty")
    # 讀的規則與 Mrliou_MRL_record_usage 寫的規則一致：qty 必須是 JSON 數字。
    # 一列 qty 寫成 "10" 不是本模組寫出來的，是帳本被手改過；靜默接受它等於
    # 替手改的帳本背書。寬鬆讀入與嚴格寫出並存，帳就對不起來。
    if isinstance(qty, bool) or not isinstance(qty, (int, float)):
        return f"qty must be a number, got {qty!r}"
    try:
        quantity = Mrliou_MRL_to_decimal(qty, "qty")
    except MrliouMRLMeterError as exc:
        return str(exc)
    if quantity < 0:
        return f"qty must not be negative, got {qty!r}"
    return None


def Mrliou_MRL_invalid_usage(
    records: Iterable[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """列出所有有問題的用量紀錄，附上可定位的位置。不丟例外。"""
    problems: List[Dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        problem = Mrliou_MRL_usage_problem(record)
        if problem is not None:
            problems.append(
                {
                    "located": record.get("located") or f"usage-{index}",
                    "detail": problem,
                }
            )
    return problems


def Mrliou_MRL_sum_usage(
    records: Iterable[Mapping[str, Any]],
) -> Dict[Tuple[str, str], Decimal]:
    """把合法的用量按 (axis, unit) 加總，全程 Decimal。

    有問題的列不計入，但**不被丟掉**：用 Mrliou_MRL_invalid_usage 取得它們，
    或直接看 Mrliou_MRL_Commerce_Report_v1 的報告——它會把每一筆逐一列出。
    """
    totals: Dict[Tuple[str, str], Decimal] = {}
    for record in records:
        if Mrliou_MRL_usage_problem(record) is not None:
            continue
        key = (str(record["axis"]), str(record["unit"]))
        quantity = Mrliou_MRL_to_decimal(record.get("qty"), "qty")
        totals[key] = totals.get(key, Decimal(0)) + quantity
    return totals


def Mrliou_MRL_known_units() -> List[Tuple[str, str]]:
    """所有 (軸別, 單位) 組合，依 COMMERCE_AXES 的固定順序。"""
    return [(axis, unit) for axis in COMMERCE_AXES for unit in AXIS_UNITS[axis]]
