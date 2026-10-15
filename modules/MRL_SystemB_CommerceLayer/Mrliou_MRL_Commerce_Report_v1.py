"""Mrliou MRL 授權與用量稽核報告。

module: Mrliou_MRL_Commerce_Report_v1
version: 1.0.0
origin_signature: MrLiouWord
particle: fx.trace.merkle  (Merkle 驗證, dom=trace, act=verify)

沿用 Mrliou_MRL_Law2_Report_v1 立下的「不會說謊」合約，一條都不打折：

1. 永不丟例外。違約與壞帳是報告要表達的**資料**，不是讓報告消失的例外。
2. 抽樣就明寫抽樣。total_rows / total_rows_known / checked / sampled /
   coverage / global_claim 六欄把範圍講死，局部觀測不得升格成全局結論。
3. 失敗全部列出，不截斷。依 LAW-2「只定位、不刪除」，每一筆都要能指回原處。
4. environment 必填。沙盒結果不得被寫成 DL580 實機結果。
5. 報告自身帶 MRL 身分與簽名，不是一包看不出所屬的通用鍵名。

另外多帶兩件商業層才有的事實：
- network_phase 與 phase_known：對外授權在 Phase 1 下不成立，報告要講出
  自己是在哪個階段下做的判定；階段讀不到就 phase_known=False，
  「不知道」不會被讀成「已開放」。
- unpriced：有用量但費率未填的 (軸別, 單位)。逐一列出，不以 0 計價充數。
- currency 與 Decimal 金額：金額以精確的十進位字串輸出並附幣別。沒有幣別就
  不是可請款的金額；用二進位浮點算出的 0.30000000000000004 也不是。
- 壞帳逐筆列出：帳本裡軸別、單位或 qty 不合法的列不會被靜默跳過。那種跳過
  會讓報告說 PASS 而真實用量憑空消失。

本函式**永不丟例外**這件事涵蓋費率表本身：他方簽名的費率表、沒有幣別的費率表、
帳本裡的未知單位，全部變成報告裡的 failure，而不是把報告炸掉。
"""

from __future__ import annotations

from decimal import Decimal
from itertools import islice
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional

try:  # 套件內匯入
    from ..MRL_SystemA_ParticleLayer.Mrliou_MRL_Provenance_v1 import (
        Mrliou_MRL_locate,
    )
    from .Mrliou_MRL_License_v1 import (
        COMMERCE_AXES,
        FOREIGN_CLAIMED,
        GRANT_STATES,
        MRL_GRANTED,
        ORIGIN_SIGNATURE,
        UNGRANTED_PENDING,
        Mrliou_MRL_check_signature_retention,
        Mrliou_MRL_read_network_phase,
    )
    from .Mrliou_MRL_License_v1 import MrliouMRLCommerceError
    from .Mrliou_MRL_Metering_v1 import (
        MrliouMRLUnpricedUnitError,
        AXIS_UNITS,
        Mrliou_MRL_invalid_usage,
        Mrliou_MRL_rate,
        Mrliou_MRL_rate_card_currency,
        Mrliou_MRL_sum_usage,
    )
except ImportError:  # 相容 cd 進本目錄後直接 import
    import sys

    sys.path.insert(
        0, str(Path(__file__).resolve().parents[1] / "MRL_SystemA_ParticleLayer")
    )
    from Mrliou_MRL_Provenance_v1 import (  # type: ignore[no-redef]
        Mrliou_MRL_locate,
    )
    from Mrliou_MRL_License_v1 import (  # type: ignore[no-redef]
        COMMERCE_AXES,
        FOREIGN_CLAIMED,
        GRANT_STATES,
        MRL_GRANTED,
        ORIGIN_SIGNATURE,
        UNGRANTED_PENDING,
        Mrliou_MRL_check_signature_retention,
        Mrliou_MRL_read_network_phase,
    )
    from Mrliou_MRL_License_v1 import (  # type: ignore[no-redef]
        MrliouMRLCommerceError,
    )
    from Mrliou_MRL_Metering_v1 import (  # type: ignore[no-redef]
        MrliouMRLUnpricedUnitError,
        AXIS_UNITS,
        Mrliou_MRL_invalid_usage,
        Mrliou_MRL_rate,
        Mrliou_MRL_rate_card_currency,
        Mrliou_MRL_sum_usage,
    )

REPORT_NAME = "Mrliou_MRL_Commerce_Report"
REPORT_VERSION = "1.0.0"

ENV_SANDBOX = "sandbox"
ENV_DL580 = "dl580"
ENV_UNSPECIFIED = "unspecified"
KNOWN_ENVIRONMENTS = (ENV_SANDBOX, ENV_DL580, ENV_UNSPECIFIED)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"


def Mrliou_MRL_build_commerce_report(
    artifacts: Iterable[Mapping[str, Any]],
    environment: str,
    usage_records: Optional[Iterable[Mapping[str, Any]]] = None,
    rate_card: Optional[Mapping[str, Any]] = None,
    sample_n: Optional[int] = None,
    count_total: bool = False,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """檢查載體是否保留簽名、彙總用量，回一份不會說謊的報告。

    Args:
        artifacts: 受授權的載體紀錄。只走一遍，只讀不改。
        environment: 必填。這次稽核實際跑在哪裡（sandbox / dl580）。
        usage_records: 計量帳本的紀錄（Mrliou_MRL_read_usage 的輸出）。
        rate_card: 費率表。給了才算金額；未填價的單位列進 unpriced。
        sample_n: 只檢查前 N 筆；None 表示全檢。
        count_total: 達到 sample_n 後是否把剩下的「數完」以求出 total。
            預設 False——有界消耗，對無界來源不會卡死。此時不謊報總數，
            而是 total_rows=None、total_rows_known=False、coverage=None。
        repo_root: 覆寫 registry 的尋找起點（測試用）。

    Returns:
        報告字典。status 由實際結果決定；global_claim 只有在「全檢、總數已知、
        且無任何違約與壞帳」時才為 True。
    """
    env = str(environment).strip() or ENV_UNSPECIFIED
    network_phase, phase_known = Mrliou_MRL_read_network_phase(repo_root)

    total_rows = 0
    checked = 0
    stopped_early = False
    failures: List[Dict[str, Any]] = []
    grant_counts: Dict[str, int] = {state: 0 for state in GRANT_STATES}
    ungranted_located: List[str] = []
    foreign_located: List[str] = []

    # 有界抽樣：預設只讀 sample_n 筆，連第 N+1 筆都不向來源索取。
    # 與 Mrliou_MRL_Law2_Report_v1 同一作法——在迴圈裡才 break 已經晚了，
    # 那一刻產生器已經被要求產出下一筆（對 DB cursor 就是多一次取值）。
    bounded = sample_n is not None and not count_total
    selected = islice(artifacts, max(0, sample_n)) if bounded else artifacts
    for artifact in selected:
        if sample_n is not None and checked >= sample_n:
            # 已達抽樣上限：只計數，不再檢查，讓 total_rows 保持誠實。
            total_rows += 1
            continue

        total_rows += 1
        fallback = f"artifact-{total_rows}"
        checked += 1

        mapping = dict(artifact)
        try:
            retention = Mrliou_MRL_check_signature_retention(mapping, fallback)
        except Exception as exc:  # 報告要表達失敗，不是被失敗打斷
            failures.append(
                {
                    "located": Mrliou_MRL_locate(mapping, fallback),
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                    "grant_state": None,
                }
            )
            continue

        state = retention["state"]
        grant_counts[state] = grant_counts.get(state, 0) + 1
        located = retention["located"]

        if state == UNGRANTED_PENDING:
            ungranted_located.append(located)
            failures.append(
                {
                    "located": located,
                    "reason": "SignatureNotRetained",
                    "detail": (
                        "chatserver-license.txt GRANT OF LICENSE 1: "
                        "載體未保留 origin_signature"
                    ),
                    "grant_state": state,
                }
            )
        elif state == FOREIGN_CLAIMED:
            foreign_located.append(located)
            failures.append(
                {
                    "located": located,
                    "reason": "ForeignSignatureClaimed",
                    "detail": (
                        "載體標了不屬於本權威的簽名："
                        f"{retention['signatures']}"
                    ),
                    "grant_state": state,
                }
            )

    if bounded and checked >= max(0, sample_n):
        stopped_early = True

    # 用量與金額：費率未填就列進 unpriced，絕不以 0 計價
    # 先 materialize 一次：usage_records 常常是 Mrliou_MRL_read_usage 的
    # 產生器，走第二遍會是空的，壞行就會被靜默漏掉。
    records = [r for r in (usage_records or []) if isinstance(r, Mapping)]
    usage_totals = Mrliou_MRL_sum_usage(records)

    # 帳本裡軸別／單位／qty 不合法的列：逐筆列出，不靜默跳過。
    for problem in Mrliou_MRL_invalid_usage(records):
        failures.append(
            {
                "located": problem["located"],
                "reason": "InvalidUsageRecord",
                "detail": problem["detail"],
                "grant_state": None,
            }
        )

    # 費率表先整體驗一次：簽名屬於本權威、且宣告了幣別。任一不成立就整張
    # 費率表不採用——他方定的價與沒有幣別的數字都不是可請款的金額。
    # 這裡絕不讓例外逃出去：報告的合約是永不丟例外。
    currency: Optional[str] = None
    rate_card_usable = rate_card is not None
    if rate_card is not None:
        try:
            currency = Mrliou_MRL_rate_card_currency(rate_card)
            # 取一次價以觸發簽名檢查，不管結果（單價未填是另一回事）
            try:
                Mrliou_MRL_rate(rate_card, COMMERCE_AXES[0],
                                next(iter(AXIS_UNITS[COMMERCE_AXES[0]])))
            except MrliouMRLUnpricedUnitError:
                pass
        except MrliouMRLCommerceError as exc:
            rate_card_usable = False
            currency = None
            failures.append(
                {
                    "located": "rate_card",
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                    "grant_state": None,
                }
            )

    usage: List[Dict[str, Any]] = []
    unpriced: List[Dict[str, Any]] = []
    amount_sum: Optional[Decimal] = Decimal(0) if rate_card_usable else None

    for axis in COMMERCE_AXES:
        for (rec_axis, unit), qty in sorted(usage_totals.items()):
            if rec_axis != axis:
                continue
            entry: Dict[str, Any] = {
                "axis": axis,
                "unit": unit,
                "qty": str(qty),
            }
            if rate_card_usable and rate_card is not None:
                try:
                    rate = Mrliou_MRL_rate(rate_card, axis, unit)
                except MrliouMRLCommerceError as exc:
                    entry["amount"] = None
                    entry["unpriced_reason"] = str(exc)
                    unpriced.append(
                        {"axis": axis, "unit": unit, "qty": str(qty)}
                    )
                    amount_sum = None
                else:
                    entry["rate"] = str(rate)
                    amount = rate * qty
                    entry["amount"] = str(amount)
                    entry["currency"] = currency
                    if amount_sum is not None:
                        amount_sum += amount
            usage.append(entry)

    amount_total: Optional[str] = (
        str(amount_sum) if amount_sum is not None else None
    )

    total_rows_known = not stopped_early
    sampled = stopped_early or (sample_n is not None and total_rows > checked)
    total_value: Optional[int] = total_rows if total_rows_known else None
    coverage: Optional[float] = None
    if total_rows_known:
        coverage = 1.0 if total_rows == 0 else round(checked / total_rows, 6)
    status = STATUS_PASS if not failures else STATUS_FAIL

    return {
        # 報告自身的 MRL 身分與權威簽名
        "Mrliou_MRL_report": REPORT_NAME,
        "Mrliou_MRL_version": REPORT_VERSION,
        "origin_signature": ORIGIN_SIGNATURE,
        "clause": "chatserver-license.txt GRANT OF LICENSE 1",
        # 稽核範圍：抽樣絕不偽裝成全檢
        "total_rows": total_value,
        "total_rows_known": total_rows_known,
        "checked": checked,
        "sampled": sampled,
        "coverage": coverage,
        "global_claim": total_rows_known and not sampled and not failures,
        # 結果：失敗全部列出不截斷
        "status": status,
        "failures": failures,
        "failure_count": len(failures),
        # 授權三態
        "grants": dict(grant_counts),
        "ungranted_pending_located": ungranted_located,
        "foreign_claimed_located": foreign_located,
        # 用量與金額：未填價一律列出，不以 0 充數
        "usage": usage,
        "unpriced": unpriced,
        "amount_total": amount_total,
        "currency": currency,
        "priced": rate_card_usable and bool(currency) and not unpriced,
        # 階段門：對外授權在 Phase 1 下不成立
        "network_phase": network_phase,
        "phase_known": phase_known,
        # 環境：沙盒結果不得被讀成 DL580 實機結果
        "environment": env,
        "environment_known": env in KNOWN_ENVIRONMENTS,
    }


def Mrliou_MRL_format_commerce_report(report: Mapping[str, Any]) -> str:
    """把報告排成人看的一段文字，範圍、階段與環境一律寫在裡面。"""
    checked = report.get("checked")
    total = report.get("total_rows")
    if not report.get("sampled"):
        scope = f"全檢 {checked} 筆"
    elif report.get("total_rows_known"):
        scope = f"抽樣 {checked}/{total} 筆（覆蓋率 {report.get('coverage')}）"
    else:
        scope = f"抽樣 {checked} 筆（總數未知：為有界消耗提前停止）"

    claim = "可以" if report.get("global_claim") else "不可（範圍不足或有違約）"

    env = str(report.get("environment"))
    if not report.get("environment_known"):
        env = f"{env}（未知環境名，原文帶出）"

    phase = str(report.get("network_phase"))
    if not report.get("phase_known"):
        phase = f"{phase}（讀不到 registry，取最保守的一態）"

    grants = report.get("grants", {})
    grant_text = "  ".join(
        f"{state}={grants.get(state, 0)}" for state in GRANT_STATES
    )

    if report.get("priced"):
        money = f"合計 {report.get('amount_total')} {report.get('currency')}"
    elif report.get("unpriced"):
        money = f"無法計價（{len(report['unpriced'])} 個單位未填費率）"
    elif report.get("amount_total") is None and report.get("usage"):
        money = "無法計價（費率表不可採用：簽名或幣別未過）"
    else:
        money = "未提供費率表，只計量不計價"

    head = (
        f"{report.get('Mrliou_MRL_report')}"
        f" v{report.get('Mrliou_MRL_version')}"
        f" [{report.get('clause')}] {report.get('status')}"
    )
    lines = [
        head,
        f"  範圍      : {scope}",
        f"  全局結論  : {claim}",
        f"  階段      : {phase}",
        f"  環境      : {env}",
        f"  授權三態  : {grant_text}",
        f"  金額      : {money}",
        f"  簽名      : {report.get('origin_signature')}",
    ]

    for entry in report.get("usage", []):
        amount = entry.get("amount")
        if amount is None:
            shown = "未填費率"
        else:
            shown = f"{amount} {entry.get('currency') or ''}".strip()
        lines.append(
            f"  用量      : {entry['axis']}/{entry['unit']}"
            f" × {entry['qty']} → {shown}"
        )
    ungranted = report.get("ungranted_pending_located") or []
    if ungranted:
        lines.append("  未簽名待補: " + ", ".join(ungranted))
    foreign = report.get("foreign_claimed_located") or []
    if foreign:
        lines.append("  他方簽名  : " + ", ".join(foreign))
    for failure in report.get("failures", []):
        lines.append(
            f"  違約／失敗: {failure['located']}"
            f" {failure['reason']} — {failure['detail']}"
        )
    return "\n".join(lines)
