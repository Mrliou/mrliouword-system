"""MRL_SystemA_ParticleLayer 套件入口。

module: MRL_SystemA_ParticleLayer
version: 0.1.0-draft
origin_signature: MrLiouWord

Laws:
- LAW-0: origin_signature 不可變，恆為 MrLiouWord
- LAW-1: DL580 上的 PostgreSQL 仍是權威持久層
- LAW-2: NO_DELETE / ADDITIVE / REVERSIBLE

對應母體粒子（core/particle_dict.json）：
- fx.meta.origin   溯源／追溯根本來源  → Mrliou_MRL_Provenance_v1
- fx.trace.anchor  錨定／創建檢查點    → Mrliou_MRL_Law2_Report_v1
- fx.trace.merkle  Merkle 驗證         → Mrliou_MRL_Law2_Report_v1
- philosophy「怎麼過去，就怎麼回來」   → LAW-2 可逆往返
"""

from .unified_particle import ORIGIN_SIGNATURE, UnifiedParticle
from .Mrliou_MRL_Provenance_v1 import (
    FOREIGN_MARKED,
    MRL_OWNED,
    ORIGIN_KEYS,
    PROVENANCE_STATES,
    UNSIGNED_PENDING,
    Mrliou_MRL_classify_source,
    Mrliou_MRL_is_foreign,
    Mrliou_MRL_locate,
    Mrliou_MRL_source_signature,
)
from .Mrliou_MRL_Law2_Report_v1 import (
    ENV_DL580,
    ENV_SANDBOX,
    ENV_UNSPECIFIED,
    REPORT_NAME,
    REPORT_VERSION,
    STATUS_FAIL,
    STATUS_PASS,
    Mrliou_MRL_build_law2_report,
    Mrliou_MRL_format_law2_report,
)
from .MRL_SystemA_ParticleLayer import (
    ADAPTERS,
    FileIndexAdapter,
    MemoryAdapter,
    OriginSignatureError,
    ParticleLayerError,
    PersonaAdapter,
    RoundtripViolation,
    SystemAAdapter,
    get_adapter,
    verify_law2,
)

__all__ = [
    "ADAPTERS",
    "ENV_DL580",
    "ENV_SANDBOX",
    "ENV_UNSPECIFIED",
    "FOREIGN_MARKED",
    "FileIndexAdapter",
    "MRL_OWNED",
    "MemoryAdapter",
    "Mrliou_MRL_build_law2_report",
    "Mrliou_MRL_classify_source",
    "Mrliou_MRL_format_law2_report",
    "Mrliou_MRL_is_foreign",
    "Mrliou_MRL_locate",
    "Mrliou_MRL_source_signature",
    "ORIGIN_KEYS",
    "ORIGIN_SIGNATURE",
    "OriginSignatureError",
    "PROVENANCE_STATES",
    "ParticleLayerError",
    "PersonaAdapter",
    "REPORT_NAME",
    "REPORT_VERSION",
    "RoundtripViolation",
    "STATUS_FAIL",
    "STATUS_PASS",
    "SystemAAdapter",
    "UNSIGNED_PENDING",
    "UnifiedParticle",
    "get_adapter",
    "verify_law2",
]
