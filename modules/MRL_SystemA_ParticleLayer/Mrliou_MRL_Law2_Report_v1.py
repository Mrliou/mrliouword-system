"""Mrliou MRL LAW-2 可逆往返查詢報告。

module: Mrliou_MRL_Law2_Report_v1
version: 1.0.0
origin_signature: MrLiouWord
particle: fx.trace.anchor (錨定 / 創建檢查點) + fx.trace.merkle (Merkle 驗證)

對應母體：core/particle_dict.json 的 philosophy「怎麼過去，就怎麼回來」。
LAW-2 的可逆往返（to_unified → from_unified → 原列）就是 Trace → Replay 這一段，
本模組產出的報告是那一段的證據。證據不能說謊，所以這份報告：

1. 永不丟例外。失敗是報告要表達的「資料」，不是讓報告消失的例外。
   原本的 verify_law2 在有違規時丟 RoundtripViolation，結果是最需要報告的時候
   根本沒有報告。
2. 抽樣就明寫抽樣。原本回傳 checked=100 卻不說母體有 250 列，讀起來與全驗通過
   完全一樣——那是把局部觀測升格成全局結論。這裡用 total_rows / sampled /
   coverage / global_claim 四個欄位把範圍講死。
3. 失敗全部列出，不截斷。原本例外訊息只帶 failures[:5]，其餘丟失。
   依 LAW-2「只定位、不刪除」，每一筆都要能指回原列。
4. 必填環境。依喚醒規則，沙盒結果不得寫成 DL580 實機結果，所以呼叫端必須明講
   自己在哪裡跑，報告原文帶出。
5. 報告自身帶 MRL 身分與簽名，不是一包看不出所屬的通用鍵名。

記憶體：rows 只走一遍。前 sample_n 列做往返驗證，其餘只計數不驗證，
因此 total_rows 誠實而不需要把整張表讀進記憶體。
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional

try:  # 套件內匯入（從母體 import modules.MRL_SystemA_ParticleLayer 時）
    from .Mrliou_MRL_Provenance_v1 import (
        MRL_OWNED,
        ORIGIN_SIGNATURE,
        PROVENANCE_STATES,
        UNSIGNED_PENDING,
        Mrliou_MRL_classify_source,
        Mrliou_MRL_locate,
    )
except ImportError:  # 相容既有用法：cd 進本目錄後直接 import
    from Mrliou_MRL_Provenance_v1 import (  # type: ignore[no-redef]
        MRL_OWNED,
        ORIGIN_SIGNATURE,
        PROVENANCE_STATES,
        UNSIGNED_PENDING,
        Mrliou_MRL_classify_source,
        Mrliou_MRL_locate,
    )

REPORT_NAME = "Mrliou_MRL_Law2_Report"
REPORT_VERSION = "1.0.0"

ENV_SANDBOX = "sandbox"
ENV_DL580 = "dl580"
ENV_UNSPECIFIED = "unspecified"
KNOWN_ENVIRONMENTS = (ENV_SANDBOX, ENV_DL580, ENV_UNSPECIFIED)

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"


def Mrliou_MRL_build_law2_report(
    adapter: Any,
    rows: Iterable[Mapping[str, Any]],
    environment: str,
    sample_n: Optional[int] = None,
) -> Dict[str, Any]:
    """驗證 LAW-2 可逆往返並回傳一份不會說謊的報告。永不丟例外。

    Args:
        adapter: 任一 SystemAAdapter 實例。
        rows: 來源列。只走一遍。
        environment: 必填。這次驗收實際跑在哪裡（sandbox / dl580）。
        sample_n: 只驗前 N 列；None 表示全驗。

    Returns:
        報告字典。status 由實際結果決定；global_claim 只有在全驗且全數通過時
        才為 True——抽樣永遠不得被讀成全局結論。
    """
    env = str(environment).strip() or ENV_UNSPECIFIED

    total_rows = 0
    checked = 0
    failures: List[Dict[str, Any]] = []
    provenance_counts: Dict[str, int] = {state: 0 for state in PROVENANCE_STATES}
    unsigned_located: List[str] = []
    foreign_located: List[str] = []

    for row in rows:
        total_rows += 1
        fallback = f"row-{total_rows}"

        if sample_n is not None and checked >= sample_n:
            # 已達抽樣上限：只計數，不再驗證，讓 total_rows 保持誠實。
            continue

        checked += 1
        mapping = dict(row)

        state = Mrliou_MRL_classify_source(mapping)
        provenance_counts[state] = provenance_counts.get(state, 0) + 1
        located = Mrliou_MRL_locate(mapping, fallback)

        if state == UNSIGNED_PENDING:
            unsigned_located.append(located)
        elif state != MRL_OWNED:
            foreign_located.append(located)

        try:
            reversible = adapter.roundtrip_check(mapping)
        except Exception as exc:  # 報告要表達失敗，不是被失敗打斷
            failures.append(
                {
                    "located": located,
                    "reason": type(exc).__name__,
                    "detail": str(exc),
                    "source_provenance": state,
                }
            )
            continue

        if not reversible:
            failures.append(
                {
                    "located": located,
                    "reason": "RoundtripMismatch",
                    "detail": "from_unified(to_unified(row)) != row",
                    "source_provenance": state,
                }
            )

    sampled = sample_n is not None and total_rows > checked
    coverage = 1.0 if total_rows == 0 else round(checked / total_rows, 6)
    status = STATUS_PASS if not failures else STATUS_FAIL

    return {
        # 報告自身的 MRL 身分與權威簽名
        "Mrliou_MRL_report": REPORT_NAME,
        "Mrliou_MRL_version": REPORT_VERSION,
        "origin_signature": ORIGIN_SIGNATURE,
        "law": "LAW-2",
        "table": getattr(adapter, "table_name", "unknown"),
        "domain": getattr(adapter, "domain", "unknown"),
        # 驗收範圍：抽樣絕不偽裝成全驗
        "total_rows": total_rows,
        "checked": checked,
        "sampled": sampled,
        "coverage": coverage,
        "global_claim": (not sampled) and not failures,
        # 結果：由實際狀況決定，失敗全部列出不截斷
        "status": status,
        "failures": failures,
        "failure_count": len(failures),
        # 來源權威三態
        "provenance": dict(provenance_counts),
        "unsigned_pending_located": unsigned_located,
        "foreign_marked_located": foreign_located,
        # 環境：沙盒結果不得被讀成 DL580 實機結果
        "environment": env,
        "environment_known": env in KNOWN_ENVIRONMENTS,
    }


def Mrliou_MRL_format_law2_report(report: Mapping[str, Any]) -> str:
    """把報告排成人看的一段文字，範圍與環境一律寫在裡面。"""
    checked = report.get("checked")
    total = report.get("total_rows")
    if report.get("sampled"):
        scope = f"抽樣 {checked}/{total} 列（覆蓋率 {report.get('coverage')}）"
    else:
        scope = f"全驗 {checked} 列"

    if report.get("global_claim"):
        claim = "可以"
    else:
        claim = "不可（範圍不足或有失敗）"

    env = str(report.get("environment"))
    if not report.get("environment_known"):
        env = f"{env}（未知環境名，原文帶出）"

    prov = report.get("provenance", {})
    prov_text = "  ".join(
        f"{state}={prov.get(state, 0)}" for state in PROVENANCE_STATES
    )

    head = (
        f"{report.get('Mrliou_MRL_report')}"
        f" v{report.get('Mrliou_MRL_version')}"
        f" — {report.get('table')}"
        f" [{report.get('law')}] {report.get('status')}"
    )
    lines = [
        head,
        f"  範圍      : {scope}",
        f"  全局結論  : {claim}",
        f"  環境      : {env}",
        f"  來源權威  : {prov_text}",
        f"  簽名      : {report.get('origin_signature')}",
    ]

    unsigned = report.get("unsigned_pending_located") or []
    if unsigned:
        lines.append("  未簽名待定: " + ", ".join(unsigned))
    foreign = report.get("foreign_marked_located") or []
    if foreign:
        lines.append("  他方簽名  : " + ", ".join(foreign))
    for failure in report.get("failures", []):
        lines.append(
            f"  失敗      : {failure['located']}"
            f" {failure['reason']} — {failure['detail']}"
        )
    return "\n".join(lines)
