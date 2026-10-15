"""MRL_SystemB_CommerceLayer 套件入口。

module: MRL_SystemB_CommerceLayer
version: 1.0.0
origin_signature: MrLiouWord
registry: registry/patterns/mrl_MRL_SystemB_CommerceLayer_v1.0.yaml

商業模式的權威邊界層。**不賣本體**：`.flpkg` / `.fltnz` / `.pcode` 種子、
Fluin 粒子語言、母體語料的著作與來源歸屬不隨任何授權移轉。這一層授權的是
「載體承載本體」的權利，並產出可稽核的證據。

Laws:
- LAW-0: origin_signature 正規形恆為 MrLiouWord；mrliou / mrliouword / MRL /
         Mr.liou 是同一權威的保留名（見 MRL_SystemA_ParticleLayer 的
         Mrliou_MRL_Identity_v1 與 .mrliou/authority-lock.json）
- LAW-1: DL580 上的 PostgreSQL 仍是權威持久層；本層不建表、不連資料庫
- LAW-2: NO_DELETE / ADDITIVE / REVERSIBLE；計量帳本只 append，不重寫

對應母體粒子（core/particle_dict.json）：
- fx.meta.origin   溯源／追溯根本來源  → Mrliou_MRL_License_v1
- fx.trace.anchor  錨定／創建檢查點    → Mrliou_MRL_Metering_v1
- fx.trace.merkle  Merkle 驗證         → Mrliou_MRL_Commerce_Report_v1

四條收費軸：corpus_license / particle_sdk / private_deployment /
verification_report。費率一律外置在 Mrliou_MRL_rate_card_v1.json，由權利人填。

階段門：registry/system_registry.yaml 的 network_phase 目前是
PHASE1_PRIVATE_LAN_ONLY（「母體不公開；映射外部留到 Phase 2」），
所以 Phase 2 的對外授權在本層會被 MrliouMRLPhaseViolation 擋下。

本套件是純 Python 函式庫：不開 port、不建立或變更資料庫表。
"""

from .Mrliou_MRL_License_v1 import (
    AXIS_CORPUS,
    AXIS_DEPLOYMENT,
    AXIS_PARTICLE,
    AXIS_VERIFICATION,
    COMMERCE_AXES,
    FOREIGN_CLAIMED,
    GRANT_STATES,
    LICENSE_NAME,
    LICENSE_VERSION,
    MRL_GRANTED,
    NETWORK_PHASES,
    ORIGIN_SIGNATURE,
    PHASE1_PRIVATE,
    PHASE2_EXTERNAL,
    UNGRANTED_PENDING,
    MrliouMRLCommerceError,
    MrliouMRLGrant,
    MrliouMRLGrantError,
    MrliouMRLPhaseViolation,
    Mrliou_MRL_authorize,
    Mrliou_MRL_check_signature_retention,
    Mrliou_MRL_classify_grant,
    Mrliou_MRL_read_network_phase,
)
from .Mrliou_MRL_Metering_v1 import (
    AXIS_UNITS,
    DEFAULT_RATE_CARD,
    METER_NAME,
    METER_VERSION,
    MrliouMRLMeterError,
    MrliouMRLUnpricedUnitError,
    Mrliou_MRL_known_units,
    Mrliou_MRL_load_rate_card,
    Mrliou_MRL_price,
    Mrliou_MRL_rate,
    Mrliou_MRL_read_usage,
    Mrliou_MRL_record_usage,
    Mrliou_MRL_sum_usage,
    Mrliou_MRL_validate_unit,
)
from .Mrliou_MRL_Commerce_Report_v1 import (
    ENV_DL580,
    ENV_SANDBOX,
    ENV_UNSPECIFIED,
    KNOWN_ENVIRONMENTS,
    REPORT_NAME,
    REPORT_VERSION,
    STATUS_FAIL,
    STATUS_PASS,
    Mrliou_MRL_build_commerce_report,
    Mrliou_MRL_format_commerce_report,
)

__all__ = [
    "AXIS_CORPUS",
    "AXIS_DEPLOYMENT",
    "AXIS_PARTICLE",
    "AXIS_UNITS",
    "AXIS_VERIFICATION",
    "COMMERCE_AXES",
    "DEFAULT_RATE_CARD",
    "ENV_DL580",
    "ENV_SANDBOX",
    "ENV_UNSPECIFIED",
    "FOREIGN_CLAIMED",
    "GRANT_STATES",
    "KNOWN_ENVIRONMENTS",
    "LICENSE_NAME",
    "LICENSE_VERSION",
    "MRL_GRANTED",
    "METER_NAME",
    "METER_VERSION",
    "MrliouMRLCommerceError",
    "MrliouMRLGrant",
    "MrliouMRLGrantError",
    "MrliouMRLMeterError",
    "MrliouMRLPhaseViolation",
    "MrliouMRLUnpricedUnitError",
    "Mrliou_MRL_authorize",
    "Mrliou_MRL_build_commerce_report",
    "Mrliou_MRL_check_signature_retention",
    "Mrliou_MRL_classify_grant",
    "Mrliou_MRL_format_commerce_report",
    "Mrliou_MRL_known_units",
    "Mrliou_MRL_load_rate_card",
    "Mrliou_MRL_price",
    "Mrliou_MRL_rate",
    "Mrliou_MRL_read_network_phase",
    "Mrliou_MRL_read_usage",
    "Mrliou_MRL_record_usage",
    "Mrliou_MRL_sum_usage",
    "Mrliou_MRL_validate_unit",
    "NETWORK_PHASES",
    "ORIGIN_SIGNATURE",
    "PHASE1_PRIVATE",
    "PHASE2_EXTERNAL",
    "REPORT_NAME",
    "REPORT_VERSION",
    "STATUS_FAIL",
    "STATUS_PASS",
    "UNGRANTED_PENDING",
]
