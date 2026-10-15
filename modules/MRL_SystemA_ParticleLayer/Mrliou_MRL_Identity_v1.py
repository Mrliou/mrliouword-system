"""Mrliou MRL 權威身分與別名正規化。

module: Mrliou_MRL_Identity_v1
version: 1.0.0
origin_signature: MrLiouWord
particle: fx.meta.origin  (溯源 / 追溯根本來源, dom=meta, act=trace_origin)

一句話：mrliou = mrliouword = MRL = Mr.liou，**同一個權威**，不是四方。

依據（不是自己發明的，全部出自 repo 內既有規章）：

`.mrliou/authority-lock.json`
    "authority": { "canonical_name": "Mr.liou",
                   "github_user": "dofaromg",
                   "github_org_projection": "Mrliou" }
    "origin":    { "signature": "MrLiouWord", "namespace": "mrliouword" }
    "reserved_names": ["Mr.liou", "MrLiouWord", "mrliouword", "MRL_"]
    invariant: "MrLiouWord is an origin signature and provenance marker; it does
                not make a derived artifact the root authority."
    invariant: "The MRL_ prefix is reserved for registry-approved artifacts only."

`registry/system_registry.yaml`
    system_brand: "MRL"        ← MRL 就是本系統的品牌名，不是別的東西

所以這些名字是同一個權威的不同層次：
    Mr.liou      權威本體（canonical_name）
    MrLiouWord   來源簽名（origin.signature）← **正規形**
    mrliouword   命名空間（origin.namespace）
    Mrliou       組織投影（github_org_projection）
    MRL / MRL_   系統品牌與保留前綴
    dofaromg     權威的 github 帳號（authority.github_user）

為什麼需要這支（修補的缺陷）：
    Mrliou_MRL_Provenance_v1 原本只認字面相等 `== "MrLiouWord"`。於是一列簽
    `MrLiou`、`Mr.liou`、`mrliouword` 或 `MRL` 會被判成 foreign_marked，
    接著被 _validate_row_origin 直接 raise OriginSignatureError 擋下——
    **把權威自己的資料標成他方並拒絕轉換**。那是權威錯位，方向與
    「未簽名資料被洗成 MRL 自有」正好相反，但一樣要擋掉。

邊界（只放寬辨識，不放寬 LAW-0）：
    - 正規形恆為 `MrLiouWord`。UnifiedParticle.__post_init__ 仍然只接受
      `MrLiouWord`，粒子寫出去的簽名一個字都不變。
    - 這裡放寬的只有「讀來源列的簽名時認不認得出是自己」這一步：
      別名進來，正規形出去。
    - 比對是**正規化後的完全相等**，不是前綴比對。`MRLSomething`、
      `MrLiouWordFake`、`mrliouword-system` 一律不算自有——
      放寬到可以被冒名，就等於把權威送出去。
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

#: 權威簽名的正規形。對外寫出、存檔、比對一律用這個值（LAW-0）。
ORIGIN_SIGNATURE = "MrLiouWord"

#: 權威的保留名原文，依 .mrliou/authority-lock.json。只列原文，供文件與報告引用；
#: 實際比對走 AUTHORITY_ALIASES（正規化後的集合）。
RESERVED_NAMES: Tuple[str, ...] = (
    "Mr.liou",          # authority.canonical_name
    "MrLiouWord",       # origin.signature（正規形）
    "mrliouword",       # origin.namespace
    "Mrliou",           # authority.github_org_projection
    "MRL",              # registry/system_registry.yaml: system_brand
    "MRL_",             # authority-lock: 保留前綴
    "dofaromg",         # authority.github_user
)


def Mrliou_MRL_fold_authority(value: Any) -> str:
    """把一個簽名字串摺成比對用的形式：只留小寫英數。

    這樣 `Mr.liou`、`MR.liou`、`Mr. Liou`、`MrLiou` 全部摺成 `mrliou`，
    `MRL_` 摺成 `mrl`。repo 內這些寫法都實際出現過（例如 MRL_STARTUP_WAKE.md
    用 `MR.liou`，docs 的頁尾用 `Mr. Liou`），不是假想的輸入。
    """
    return "".join(ch for ch in str(value).lower() if ch.isalnum())


#: 正規化後的別名集。比對用這個，且必須是完全相等。
AUTHORITY_ALIASES: frozenset = frozenset(
    Mrliou_MRL_fold_authority(name) for name in RESERVED_NAMES
)


def Mrliou_MRL_normalize_authority(value: Any) -> Optional[str]:
    """認得出是本權威就回正規形 `MrLiouWord`；認不出回 None。

    空值、空字串、只有空白、以及摺疊後為空（例如 "___"）一律回 None——
    那是「沒有簽名」，不是「簽名是自己」。沒有簽名的列由呼叫端歸
    unsigned_pending（待找回），不得逕自升格為自有。
    """
    if value is None:
        return None
    folded = Mrliou_MRL_fold_authority(value)
    if not folded:
        return None
    return ORIGIN_SIGNATURE if folded in AUTHORITY_ALIASES else None


def Mrliou_MRL_is_own_authority(value: Any) -> bool:
    """這個簽名是否屬於本權威（mrliou = mrliouword = MRL = Mr.liou）。"""
    return Mrliou_MRL_normalize_authority(value) is not None
