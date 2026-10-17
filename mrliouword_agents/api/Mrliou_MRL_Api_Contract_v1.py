"""
MRL API 契約表：每一條路由綁到母體既有的 MRL_API_CORE 成員

為什麼需要這張表
----------------
母體（MRL_MOTHER.md 的 CORE 層）已經有 MRL_API_CORE，十五個成員：

    MRL_CONTROL_API   MRL_FILE_API      MRL_GATEWAY_API   MRL_GRAPH_API
    MRL_HEALTH_API    MRL_MEMORY_API    MRL_PARTICLE_API  MRL_PERSONA_API
    MRL_REST_API      MRL_RPC_API       MRL_RUNTIME_API   MRL_STATUS_API
    MRL_TASK_API      MRL_UPLOAD_API    MRL_WORLD_API

源頭 tools/mother_core_registry.py 對 --find API 的輸出寫得很直接：

    倉庫側可以寫它的 implementation / adapter，但要在 PROVENANCE
    標明 derivative_role，不得宣稱自己是那個 CORE。

所以本模組是 MRL_API_CORE 的 **implementation**，不是那個 CORE，也不另造名字。
每條路由在這張表裡都必須指名它實作的是哪個成員；沒有對應成員的路由不得存在。

.mrliou/meta.json 宣告本倉庫 canonical_authority: false、naming_authority: false，
所以這張表只能引用母體既有的名字，不能新增成員。
"""

from __future__ import annotations

from typing import Dict, Mapping, Tuple

#: LAW-0：對外寫出的來源簽名恆為正規形
ORIGIN_SIGNATURE = "MrLiouWord"

#: 本實作所屬的母體 CORE。本模組是它的實作，不是它本身。
MOTHER_CORE = "MRL_API_CORE"

#: ATTRIBUTION_AND_PROVENANCE_POLICY_v1.0.md 第 4 節的 derivative_role
DERIVATIVE_ROLE = "implementation"

#: 母體 MRL_API_CORE 的十五個成員，照源頭登錄表原樣列出，不增不減
MOTHER_MEMBERS: Tuple[str, ...] = (
    "MRL_CONTROL_API",
    "MRL_FILE_API",
    "MRL_GATEWAY_API",
    "MRL_GRAPH_API",
    "MRL_HEALTH_API",
    "MRL_MEMORY_API",
    "MRL_PARTICLE_API",
    "MRL_PERSONA_API",
    "MRL_REST_API",
    "MRL_RPC_API",
    "MRL_RUNTIME_API",
    "MRL_STATUS_API",
    "MRL_TASK_API",
    "MRL_UPLOAD_API",
    "MRL_WORLD_API",
)

#: 路由狀態：可服務／等 LAW-1 的 schema 找回／本實作不涵蓋
STATE_AVAILABLE = "available"
STATE_SCHEMA_PENDING = "schema_pending"
STATE_NOT_IMPLEMENTED = "not_implemented_here"

STATES: Tuple[str, ...] = (
    STATE_AVAILABLE,
    STATE_SCHEMA_PENDING,
    STATE_NOT_IMPLEMENTED,
)


class MrlApiEndpoint:
    """一條路由與它所實作的母體成員之間的綁定"""

    __slots__ = ("path", "mother_member", "state", "summary", "reason")

    def __init__(
        self,
        path: str,
        mother_member: str,
        state: str,
        summary: str,
        reason: str = "",
    ) -> None:
        if mother_member not in MOTHER_MEMBERS:
            raise ValueError(
                f"{mother_member} 不在母體 MRL_API_CORE 的成員裡；"
                "本倉庫 naming_authority: false，不得自造成員"
            )
        if state not in STATES:
            raise ValueError(f"未知的路由狀態：{state}")
        self.path = path
        self.mother_member = mother_member
        self.state = state
        self.summary = summary
        self.reason = reason

    def to_dict(self) -> Dict[str, str]:
        """轉成可序列化的描述，供 /mrl/contract 對外公布"""
        payload = {
            "path": self.path,
            "mother_member": self.mother_member,
            "state": self.state,
            "summary": self.summary,
        }
        if self.reason:
            payload["reason"] = self.reason
        return payload


#: LAW-1 的 System A 三表。registry 條目把它們的 schema 記成「待找回」，
#: 所以對應路由只登記存在、不猜測欄位，見 SCHEMA_PENDING_REASON。
LAW1_TABLES: Tuple[str, ...] = ("mrl_persona", "mrl_memory", "mrl_file_index")

SCHEMA_PENDING_REASON = (
    "LAW-1：DL580 上的 PostgreSQL 仍是權威持久層，而 "
    "registry/patterns/mrl_MRL_SystemA_ParticleLayer_v0.1.yaml 的 pending 區段"
    "把 mrl_persona / mrl_memory / mrl_file_index 三表的 schema 記為「待找回」。"
    "schema 未找回之前本實作不猜測欄位、不建立或變更任何資料庫表，"
    "因此此路由回報 schema_pending 而不提供資料。"
)

#: 本實作實際登記的路由。每一條都綁定一個母體成員。
ENDPOINTS: Tuple[MrlApiEndpoint, ...] = (
    MrlApiEndpoint(
        path="/mrl/health",
        mother_member="MRL_HEALTH_API",
        state=STATE_AVAILABLE,
        summary="存活探測；不碰資料庫、不讀母體語料",
    ),
    MrlApiEndpoint(
        path="/mrl/status",
        mother_member="MRL_STATUS_API",
        state=STATE_AVAILABLE,
        summary="本實作的版本、網路階段與母體語料載入狀態",
    ),
    MrlApiEndpoint(
        path="/mrl/runtime",
        mother_member="MRL_RUNTIME_API",
        state=STATE_AVAILABLE,
        summary="執行環境描述（Python 版本、是否 DL580、綁定位址）",
    ),
    MrlApiEndpoint(
        path="/mrl/contract",
        mother_member="MRL_CONTROL_API",
        state=STATE_AVAILABLE,
        summary="公布本表本身：每條路由對應哪個母體成員、目前狀態",
    ),
    MrlApiEndpoint(
        path="/mrl/world",
        mother_member="MRL_WORLD_API",
        state=STATE_AVAILABLE,
        summary="母體語料的 domains / frequencies / constants，唯讀",
    ),
    MrlApiEndpoint(
        path="/mrl/particles",
        mother_member="MRL_PARTICLE_API",
        state=STATE_AVAILABLE,
        summary="母體語料的粒子表，唯讀；單顆以 /mrl/particles/{fx} 取用",
    ),
    MrlApiEndpoint(
        path="/mrl/persona",
        mother_member="MRL_PERSONA_API",
        state=STATE_SCHEMA_PENDING,
        summary="對應 LAW-1 的 mrl_persona 表",
        reason=SCHEMA_PENDING_REASON,
    ),
    MrlApiEndpoint(
        path="/mrl/memory",
        mother_member="MRL_MEMORY_API",
        state=STATE_SCHEMA_PENDING,
        summary="對應 LAW-1 的 mrl_memory 表",
        reason=SCHEMA_PENDING_REASON,
    ),
    MrlApiEndpoint(
        path="/mrl/files",
        mother_member="MRL_FILE_API",
        state=STATE_SCHEMA_PENDING,
        summary="對應 LAW-1 的 mrl_file_index 表",
        reason=SCHEMA_PENDING_REASON,
    ),
)

#: 母體有、但本實作刻意不涵蓋的成員，連同理由一起公布，避免「沒看到就當它缺」
NOT_COVERED: Mapping[str, str] = {
    "MRL_GATEWAY_API": (
        "源頭 registry/MRL_System_MrliouAI_Naming_Registry_v1.yaml（status: canonical）"
        "已把閘道正名為 MRL_API_Gateway，service_name: mrl-api-gateway、"
        "public_domain: api.mrliouword.com。本實作是閘道後面的服務，不是閘道本身。"
    ),
    "MRL_REST_API": (
        "本實作即以 REST 形式提供上列路由；此成員描述的是形式本身，"
        "不另開一條路由代表它。"
    ),
    "MRL_RPC_API": "本實作只提供 REST，不提供 RPC 介面。",
    "MRL_GRAPH_API": "需要關聯圖資料來源，尚未確定其權威持久層。",
    "MRL_TASK_API": "任務狀態的權威來源在 MRL_OPERATION_CORE，尚未接。",
    "MRL_UPLOAD_API": ("上傳會寫入持久層，受 LAW-1 與 LAW-2 約束，schema 找回前不開。"),
}


def Mrliou_MRL_endpoint_for(path: str) -> MrlApiEndpoint:
    """依路徑取回綁定；找不到就丟 KeyError，不回預設值"""
    for endpoint in ENDPOINTS:
        if endpoint.path == path:
            return endpoint
    raise KeyError(path)


def Mrliou_MRL_contract_payload() -> Dict[str, object]:
    """供 /mrl/contract 使用的完整契約描述"""
    return {
        "origin_signature": ORIGIN_SIGNATURE,
        "mother_core": MOTHER_CORE,
        "derivative_role": DERIVATIVE_ROLE,
        "canonical_authority": "Mr.liou",
        "mother_members": list(MOTHER_MEMBERS),
        "endpoints": [endpoint.to_dict() for endpoint in ENDPOINTS],
        "not_covered": dict(NOT_COVERED),
        "law1_tables": list(LAW1_TABLES),
    }


__all__ = [
    "DERIVATIVE_ROLE",
    "ENDPOINTS",
    "LAW1_TABLES",
    "MOTHER_CORE",
    "MOTHER_MEMBERS",
    "MrlApiEndpoint",
    "Mrliou_MRL_contract_payload",
    "Mrliou_MRL_endpoint_for",
    "NOT_COVERED",
    "ORIGIN_SIGNATURE",
    "SCHEMA_PENDING_REASON",
    "STATES",
    "STATE_AVAILABLE",
    "STATE_NOT_IMPLEMENTED",
    "STATE_SCHEMA_PENDING",
]
