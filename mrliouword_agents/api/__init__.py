"""
MRL API 模組：母體 MRL_API_CORE 的實作

本套件匯入時不需要 fastapi——fastapi 只在 create_app() 內部匯入，uvicorn 只在
Mrliou_MRL_run_server() 內部匯入，所以 `import mrliouword_agents.api` 在沒有安裝
Web 依賴的環境裡仍然可用（例如只要讀契約表的時候）。
"""

from .Mrliou_MRL_Api_Contract_v1 import (
    DERIVATIVE_ROLE,
    ENDPOINTS,
    LAW1_TABLES,
    MOTHER_CORE,
    MOTHER_MEMBERS,
    NOT_COVERED,
    SCHEMA_PENDING_REASON,
    STATE_AVAILABLE,
    STATE_NOT_IMPLEMENTED,
    STATE_SCHEMA_PENDING,
    STATES,
    MrlApiEndpoint,
    Mrliou_MRL_contract_payload,
    Mrliou_MRL_endpoint_for,
)
from .Mrliou_MRL_Api_Server_v1 import (
    ALLOW_PUBLIC_BIND_ENV,
    NETWORK_PHASE,
    ORIGIN_SIGNATURE,
    PARTICLE_DICT_ENV,
    MrlApiBindRefused,
    Mrliou_MRL_allow_public_bind,
    Mrliou_MRL_is_public_bind,
    Mrliou_MRL_load_particle_dict,
    Mrliou_MRL_locate_particle_dict,
    Mrliou_MRL_resolve_bind,
    Mrliou_MRL_run_server,
    create_app,
)

__all__ = [
    "ALLOW_PUBLIC_BIND_ENV",
    "DERIVATIVE_ROLE",
    "ENDPOINTS",
    "LAW1_TABLES",
    "MOTHER_CORE",
    "MOTHER_MEMBERS",
    "MrlApiBindRefused",
    "MrlApiEndpoint",
    "Mrliou_MRL_allow_public_bind",
    "Mrliou_MRL_contract_payload",
    "Mrliou_MRL_endpoint_for",
    "Mrliou_MRL_is_public_bind",
    "Mrliou_MRL_load_particle_dict",
    "Mrliou_MRL_locate_particle_dict",
    "Mrliou_MRL_resolve_bind",
    "Mrliou_MRL_run_server",
    "NETWORK_PHASE",
    "NOT_COVERED",
    "ORIGIN_SIGNATURE",
    "PARTICLE_DICT_ENV",
    "SCHEMA_PENDING_REASON",
    "STATES",
    "STATE_AVAILABLE",
    "STATE_NOT_IMPLEMENTED",
    "STATE_SCHEMA_PENDING",
    "create_app",
]
