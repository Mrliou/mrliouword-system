"""Mrliou MRL 授權判定（商業模式的權威邊界）。

module: Mrliou_MRL_License_v1
version: 1.0.0
origin_signature: MrLiouWord
particle: fx.meta.origin  (溯源 / 追溯根本來源, dom=meta, act=trace_origin)

這一層回答三個問題，全部只判定、不扣額、不寫回來源（LAW-2）：

    1. 這份授權屬於誰？        → 授權三態（與來源權威三態同構命名）
    2. 載體有沒有保留簽名？    → ChatServer License 第 1 條的程式化
    3. 這條軸現在能不能對外？  → network_phase 階段門

依據（repo 內既有規章，不是自己發明的）：

`docs/references/licenses/chatserver-license.txt`（全 repo 唯一的 MRL 自撰授權）
    GRANT OF LICENSE:
    1. The Software must retain the origin_signature: MrLiouWord in all copies.
    3. Redistribution of the Software outside the MrLiouWord system requires
       prior written permission from MR.liou.
    → 第 1 條就是 Mrliou_MRL_check_signature_retention 要檢查的事。

`.mrliou/authority-lock.json`
    invariant: "Every derivative or projection using MrLiouWord must declare
                artifact_owner, source_repo, projection_role, and
                origin_signature."
    → MrliouMRLGrant 強制帶這四欄，缺一不可。

`registry/system_registry.yaml`
    network_phase: "PHASE1_PRIVATE_LAN_ONLY"
    principle: "母體不公開；映射外部留到 Phase 2"
    → 對外授權（Phase 2）在 Phase 1 下不得放行。這不是我加的限制，
      是本系統自己的規章；繞過它就是繞過自己的閉環。

不賣本體：本模組授權的是**載體承載本體**的權利。`.flpkg` / `.fltnz` /
`.pcode` 種子、母體語料的著作與來源歸屬不隨任何授權移轉，`origin_signature`
恆為 MrLiouWord（LAW-0）。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Optional, Tuple

try:  # 套件內匯入（從母體 import modules.MRL_SystemB_CommerceLayer 時）
    from ..MRL_SystemA_ParticleLayer.Mrliou_MRL_Identity_v1 import (
        ORIGIN_SIGNATURE,
        RESERVED_NAMES,
        Mrliou_MRL_is_own_authority,
        Mrliou_MRL_normalize_authority,
    )
    from ..MRL_SystemA_ParticleLayer.Mrliou_MRL_Provenance_v1 import (
        Mrliou_MRL_locate,
        Mrliou_MRL_source_signature_values,
        Mrliou_MRL_source_signatures,
    )
except ImportError:  # 相容 cd 進本目錄後直接 import
    import sys

    sys.path.insert(
        0, str(Path(__file__).resolve().parents[1] / "MRL_SystemA_ParticleLayer")
    )
    from Mrliou_MRL_Identity_v1 import (  # type: ignore[no-redef]
        ORIGIN_SIGNATURE,
        RESERVED_NAMES,
        Mrliou_MRL_is_own_authority,
        Mrliou_MRL_normalize_authority,
    )
    from Mrliou_MRL_Provenance_v1 import (  # type: ignore[no-redef]
        Mrliou_MRL_locate,
        Mrliou_MRL_source_signature_values,
        Mrliou_MRL_source_signatures,
    )

LICENSE_NAME = "Mrliou_MRL_License"
LICENSE_VERSION = "1.0.0"

# --- 四條收費軸 -------------------------------------------------------------
#: 本體語料授權：授權席次 × 語料範圍。賣的是「有權在自己的載體上承載母體語料」，
#: 不是賣語料的著作權。
AXIS_CORPUS = "corpus_license"
#: 粒子層／SDK 使用：粒子轉換筆數、SDK 呼叫次數。
AXIS_PARTICLE = "particle_sdk"
#: 私有部署：部署案 × 年度維護（LAW-1 的 DL580 on-prem）。
AXIS_DEPLOYMENT = "private_deployment"
#: 驗證／報告服務：LAW-2 可逆往返與來源權威三態的稽核報告次數。
AXIS_VERIFICATION = "verification_report"

#: 固定順序，報告統計依此輸出，不隨 dict 插入順序漂移。
COMMERCE_AXES: Tuple[str, ...] = (
    AXIS_CORPUS,
    AXIS_PARTICLE,
    AXIS_DEPLOYMENT,
    AXIS_VERIFICATION,
)

# --- 階段門（registry/system_registry.yaml 的 network_phase）---------------
PHASE1_PRIVATE = "phase1_private_lan_only"
PHASE2_EXTERNAL = "phase2_external_mapping"
NETWORK_PHASES: Tuple[str, ...] = (PHASE1_PRIVATE, PHASE2_EXTERNAL)

#: registry 裡的原文值 → 本模組的階段常數。
_REGISTRY_PHASE_MAP = {
    "PHASE1_PRIVATE_LAN_ONLY": PHASE1_PRIVATE,
    "PHASE2_EXTERNAL_MAPPING": PHASE2_EXTERNAL,
}

# --- 授權三態（與 Mrliou_MRL_Provenance_v1 的來源權威三態同構命名）---------
MRL_GRANTED = "mrl_granted"
FOREIGN_CLAIMED = "foreign_claimed"
UNGRANTED_PENDING = "ungranted_pending"

GRANT_STATES: Tuple[str, ...] = (MRL_GRANTED, FOREIGN_CLAIMED, UNGRANTED_PENDING)


class MrliouMRLCommerceError(RuntimeError):
    """商業層合約失敗的基底例外。"""


class MrliouMRLGrantError(MrliouMRLCommerceError):
    """授權本身不成立（簽名、欄位、軸別或席次）。"""


class MrliouMRLPhaseViolation(MrliouMRLCommerceError):
    """授權的階段高於當前 network_phase 允許的範圍。"""


def Mrliou_MRL_read_network_phase(
    repo_root: Optional[Path] = None,
) -> Tuple[str, bool]:
    """讀 registry/system_registry.yaml 的 network_phase，回 (階段, 是否已知)。

    刻意用正規表示式讀單一行而不依賴 PyYAML：本層與 SystemA 一樣必須零依賴，
    而且這樣就不會把階段值複製一份進程式裡等它漂移——規章改了，這裡自動跟上。

    讀不到檔或讀不到該鍵時**取最保守的一態**（Phase 1）並回報 known=False。
    依喚醒規則：看不到的歸「待找回」，不歸「不存在」，更不得逕自假設已開放。
    """
    root = repo_root or Path(__file__).resolve().parents[2]
    registry = root / "registry" / "system_registry.yaml"
    try:
        text = registry.read_text(encoding="utf-8")
    except OSError:
        return PHASE1_PRIVATE, False
    match = re.search(r'^network_phase:\s*"?([A-Za-z0-9_]+)"?', text, re.M)
    if not match:
        return PHASE1_PRIVATE, False
    mapped = _REGISTRY_PHASE_MAP.get(match.group(1))
    if mapped is None:
        return PHASE1_PRIVATE, False
    return mapped, True


@dataclass(frozen=True)
class MrliouMRLGrant:
    """一份授權。

    刻意 frozen：授權核發後不得在流程中途被改寫（改了席次或軸別就等於自己
    發新授權）。要改就核發新的一份，舊的留著可回溯（LAW-2 不刪除）。

    四欄宣告（artifact_owner / source_repo / projection_role /
    origin_signature）是 .mrliou/authority-lock.json 的 invariant 明文要求，
    缺一不可——沒有這四欄就無法分辨「授權的投影」與「冒名的根權威」。
    """

    grantee: str
    axes: Tuple[str, ...]
    artifact_owner: str
    source_repo: str
    projection_role: str
    seats: int = 1
    scope: Tuple[str, ...] = field(default_factory=tuple)
    term: Optional[str] = None
    phase: str = PHASE1_PRIVATE
    environment: str = "unspecified"
    origin_signature: str = ORIGIN_SIGNATURE

    def __post_init__(self) -> None:
        # 簽名：認別名，存正規形。簽 MRL / Mr.liou 的授權不該被自己擋下。
        normalized = Mrliou_MRL_normalize_authority(self.origin_signature)
        if normalized is None:
            raise MrliouMRLGrantError(
                "LAW-0 violation: origin_signature must be one of "
                f"{RESERVED_NAMES}, got {self.origin_signature!r}"
            )
        object.__setattr__(self, "origin_signature", normalized)
        object.__setattr__(self, "axes", tuple(self.axes))
        object.__setattr__(self, "scope", tuple(self.scope))

        if not str(self.grantee).strip():
            raise MrliouMRLGrantError("grantee must not be empty")
        for required in ("artifact_owner", "source_repo", "projection_role"):
            if not str(getattr(self, required)).strip():
                raise MrliouMRLGrantError(
                    f"authority-lock invariant: {required} must be declared"
                )
        if not self.axes:
            raise MrliouMRLGrantError("at least one commerce axis is required")
        unknown = [axis for axis in self.axes if axis not in COMMERCE_AXES]
        if unknown:
            raise MrliouMRLGrantError(
                f"unknown commerce axis: {unknown}; known axes: {COMMERCE_AXES}"
            )
        if self.seats < 0:
            raise MrliouMRLGrantError("seats must not be negative")
        if self.phase not in NETWORK_PHASES:
            raise MrliouMRLGrantError(
                f"unknown phase: {self.phase!r}; known phases: {NETWORK_PHASES}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "grantee": self.grantee,
            "axes": list(self.axes),
            "artifact_owner": self.artifact_owner,
            "source_repo": self.source_repo,
            "projection_role": self.projection_role,
            "seats": self.seats,
            "scope": list(self.scope),
            "term": self.term,
            "phase": self.phase,
            "environment": self.environment,
            "origin_signature": self.origin_signature,
        }


def Mrliou_MRL_classify_grant(record: Mapping[str, Any]) -> str:
    """判定一筆授權紀錄的權威歸屬，回傳 GRANT_STATES 之一。

    與 Mrliou_MRL_classify_source 完全同構：讀**所有**簽名欄位（ORIGIN_KEYS）的
    **原值**，任何一個不屬於本權威就判 foreign_claimed——包含兩欄互相矛盾的
    情況。矛盾即他方。沒有任何簽名欄位則是 ungranted_pending（待補，不是
    不存在，也不得逕自升格為已授權）。

    用原值而不是 str() 後的字串：摺疊會去掉標點，所以 str(["MRL"]) 摺完就是
    "mrl"，一個 list 就取得了授權。兩層必須用同一支判定函式，否則
    Provenance 擋下的列會從 License 這邊漏進來——那正是本次修掉的漏洞。
    """
    values = Mrliou_MRL_source_signature_values(record)
    if not values:
        return UNGRANTED_PENDING
    if all(Mrliou_MRL_is_own_authority(value) for value in values):
        return MRL_GRANTED
    return FOREIGN_CLAIMED


def Mrliou_MRL_check_signature_retention(
    artifact: Mapping[str, Any], fallback: str = "artifact"
) -> Dict[str, Any]:
    """把 ChatServer License 第 1 條程式化：載體是否保留了 origin_signature。

    「保留」認任一保留名（mrliou / mrliouword / MRL / Mr.liou …），因為那些
    是同一個權威；只要讀得出屬於本權威就算保留。完全抹掉簽名即違約，
    標了他方簽名也是違約——但兩者原因不同，報告要分得開，所以回傳 state
    而不是只回一個布林。

    只讀、只定位，絕不改寫 artifact（LAW-2）。
    """
    state = Mrliou_MRL_classify_grant(artifact)
    return {
        "located": Mrliou_MRL_locate(artifact, fallback),
        "state": state,
        "retained": state == MRL_GRANTED,
        "signatures": list(Mrliou_MRL_source_signatures(artifact)),
        "clause": "chatserver-license.txt GRANT OF LICENSE 1",
    }


def Mrliou_MRL_authorize(
    grant: MrliouMRLGrant,
    axis: str,
    repo_root: Optional[Path] = None,
) -> Dict[str, Any]:
    """判定這份授權此刻能不能動用某一條軸。只判定，不扣額、不寫檔。

    擋兩件事：
    1. 軸別不在授權範圍內 → MrliouMRLGrantError
    2. 授權是 Phase 2（對外映射）但系統還在 Phase 1（母體不公開）
       → MrliouMRLPhaseViolation

    第 2 點是本系統自己的規章（registry/system_registry.yaml）。階段讀不到時
    取最保守的 Phase 1，回傳的 phase_known=False 會一路帶進報告裡，
    不會讓「不知道」被讀成「已開放」。
    """
    if axis not in COMMERCE_AXES:
        raise MrliouMRLGrantError(
            f"unknown commerce axis: {axis!r}; known axes: {COMMERCE_AXES}"
        )
    if axis not in grant.axes:
        raise MrliouMRLGrantError(
            f"axis {axis!r} is not in this grant's axes {grant.axes}"
        )

    current_phase, phase_known = Mrliou_MRL_read_network_phase(repo_root)
    if grant.phase == PHASE2_EXTERNAL and current_phase == PHASE1_PRIVATE:
        raise MrliouMRLPhaseViolation(
            f"grant phase {PHASE2_EXTERNAL} is not permitted while "
            f"network_phase is {PHASE1_PRIVATE} "
            "(registry/system_registry.yaml: 母體不公開；映射外部留到 Phase 2)"
        )

    return {
        "Mrliou_MRL_license": LICENSE_NAME,
        "Mrliou_MRL_version": LICENSE_VERSION,
        "grantee": grant.grantee,
        "axis": axis,
        "seats": grant.seats,
        "grant_phase": grant.phase,
        "network_phase": current_phase,
        "phase_known": phase_known,
        "environment": grant.environment,
        "origin_signature": grant.origin_signature,
    }
