"""
MRL API 伺服器：母體 MRL_API_CORE 的實作

邊界
----
- **本模組是 MRL_API_CORE 的 implementation，不是那個 CORE。** 路由與母體成員的
  綁定寫在 Mrliou_MRL_Api_Contract_v1，沒有對應成員的路由不得存在。
- **不建立、不變更任何資料庫表。** LAW-1 說 DL580 上的 PostgreSQL 仍是權威持久層；
  System A 三表的 schema 目前記為「待找回」，所以 persona / memory / files 三條
  路由只登記存在並回報 schema_pending，不猜測欄位。
- **母體語料只讀不寫。** core/particle_dict.json 是 canonical 語料，本模組只讀取。
- **PHASE1_PRIVATE_LAN_ONLY。** 綁定到未指定位址（會對外曝露所有介面）時，
  預設拒絕啟動；要這麼做必須用 MRL_API_ALLOW_PUBLIC_BIND 明確開啟。
- **LAW-0。** 每個回應都帶 origin_signature，恆為正規形 MrLiouWord。
"""

from __future__ import annotations

import ipaddress
import json
import os
import platform
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import Mrliou_MRL_Api_Contract_v1 as contract

#: LAW-0：對外寫出的來源簽名恆為正規形
ORIGIN_SIGNATURE = contract.ORIGIN_SIGNATURE

#: registry 條目宣告的網路階段
NETWORK_PHASE = "PHASE1_PRIVATE_LAN_ONLY"

#: 要綁定到未指定位址必須明確設這個環境變數
ALLOW_PUBLIC_BIND_ENV = "MRL_API_ALLOW_PUBLIC_BIND"

#: 母體語料的檔名；可用這個環境變數指到別處
PARTICLE_DICT_ENV = "MRL_PARTICLE_DICT"
PARTICLE_DICT_RELATIVE = Path("core") / "particle_dict.json"


class MrlApiBindRefused(RuntimeError):
    """綁定位址違反 PHASE1_PRIVATE_LAN_ONLY，拒絕啟動"""


def Mrliou_MRL_locate_particle_dict(start: Optional[Path] = None) -> Optional[Path]:
    """往上找母體語料；找不到就回 None，不丟例外也不自己造一份"""
    override = os.environ.get(PARTICLE_DICT_ENV)
    if override:
        candidate = Path(override)
        return candidate if candidate.is_file() else None

    here = (start or Path(__file__).resolve()).resolve()
    for parent in [here, *here.parents]:
        candidate = parent / PARTICLE_DICT_RELATIVE
        if candidate.is_file():
            return candidate
    return None


def Mrliou_MRL_load_particle_dict(
    path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """唯讀載入母體語料。檔案不存在或不是物件就回 None，由呼叫端回報 503。"""
    located = path or Mrliou_MRL_locate_particle_dict()
    if located is None:
        return None
    try:
        with located.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def Mrliou_MRL_is_public_bind(host: str) -> bool:
    """這個位址是否會把服務曝露到所有介面（IPv4 與 IPv6 的未指定位址）"""
    try:
        return ipaddress.ip_address(host.strip()).is_unspecified
    except ValueError:
        # 主機名無法在此判定（要解析 DNS），交由部署端負責，不在此擋
        return False


def Mrliou_MRL_allow_public_bind() -> bool:
    """是否已明確開啟對外綁定"""
    raw = os.environ.get(ALLOW_PUBLIC_BIND_ENV, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def Mrliou_MRL_resolve_bind(
    host: Optional[str] = None, port: Optional[int] = None
) -> tuple[str, int]:
    """決定實際綁定的位址與連接埠，並在違反 PHASE1 時拒絕

    host / port 省略時取 MrliouwordConfig 的 api_host / api_port，
    所以 API_HOST、API_PORT 兩個環境變數照既有設定系統生效。
    """
    if host is None or port is None:
        from ..core.config import config as runtime_config

        host = host if host is not None else runtime_config.api_host
        port = port if port is not None else runtime_config.api_port

    if Mrliou_MRL_is_public_bind(host) and not Mrliou_MRL_allow_public_bind():
        raise MrlApiBindRefused(
            f"綁定位址 {host!r} 會曝露所有網路介面，與 registry 宣告的 "
            f"{NETWORK_PHASE} 不符，拒絕啟動。"
            f"確定要這麼做請設定 {ALLOW_PUBLIC_BIND_ENV}=1，"
            "或把 API_HOST 設成內網位址。"
        )
    return host, int(port)


def _Mrliou_MRL_envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    """LAW-0：所有回應統一帶上來源簽名與衍生角色"""
    enveloped: Dict[str, Any] = {
        "origin_signature": ORIGIN_SIGNATURE,
        "mother_core": contract.MOTHER_CORE,
        "derivative_role": contract.DERIVATIVE_ROLE,
    }
    enveloped.update(payload)
    return enveloped


def _Mrliou_MRL_schema_pending_detail(path: str) -> Dict[str, Any]:
    """三條 LAW-1 路由的統一回應內容"""
    endpoint = contract.Mrliou_MRL_endpoint_for(path)
    return _Mrliou_MRL_envelope(
        {
            "state": endpoint.state,
            "mother_member": endpoint.mother_member,
            "law": "LAW-1",
            "pending_tables": list(contract.LAW1_TABLES),
            "reason": endpoint.reason,
        }
    )


def create_app() -> Any:
    """建立 FastAPI 應用。fastapi 未安裝時丟 ImportError，不靜默降級。"""
    from fastapi import FastAPI, HTTPException

    from ..version import __version__

    app = FastAPI(
        title="MRL API",
        version=__version__,
        description=(
            "母體 MRL_API_CORE 的實作。路由與母體成員的綁定見 /mrl/contract；"
            "本服務不是該 CORE 本身，也不建立或變更任何資料庫表。"
        ),
    )

    @app.get("/mrl/health")
    def mrl_health() -> Dict[str, Any]:
        return _Mrliou_MRL_envelope({"state": "ok"})

    @app.get("/mrl/status")
    def mrl_status() -> Dict[str, Any]:
        corpus = Mrliou_MRL_load_particle_dict()
        return _Mrliou_MRL_envelope(
            {
                "state": "ok",
                "version": __version__,
                "network_phase": NETWORK_PHASE,
                "particle_dict_loaded": corpus is not None,
                "particle_count": len(corpus.get("particles", {})) if corpus else 0,
                "endpoints": len(contract.ENDPOINTS),
            }
        )

    @app.get("/mrl/runtime")
    def mrl_runtime() -> Dict[str, Any]:
        located = Mrliou_MRL_locate_particle_dict()
        return _Mrliou_MRL_envelope(
            {
                "python_version": sys.version.split()[0],
                "platform": platform.system(),
                "network_phase": NETWORK_PHASE,
                "particle_dict_path": str(located) if located else None,
                "public_bind_allowed": Mrliou_MRL_allow_public_bind(),
            }
        )

    @app.get("/mrl/contract")
    def mrl_contract() -> Dict[str, Any]:
        return _Mrliou_MRL_envelope(contract.Mrliou_MRL_contract_payload())

    @app.get("/mrl/world")
    def mrl_world() -> Dict[str, Any]:
        corpus = Mrliou_MRL_load_particle_dict()
        if corpus is None:
            raise HTTPException(
                status_code=503,
                detail=_Mrliou_MRL_envelope(
                    {
                        "state": "corpus_unavailable",
                        "expected": "core/particle_dict.json",
                    }
                ),
            )
        return _Mrliou_MRL_envelope(
            {
                "corpus_version": corpus.get("version"),
                "corpus_origin": corpus.get("origin"),
                "philosophy": corpus.get("philosophy"),
                "domains": corpus.get("domains", {}),
                "frequencies": corpus.get("frequencies", {}),
                "constants": corpus.get("constants", {}),
            }
        )

    @app.get("/mrl/particles")
    def mrl_particles() -> Dict[str, Any]:
        corpus = Mrliou_MRL_load_particle_dict()
        if corpus is None:
            raise HTTPException(
                status_code=503,
                detail=_Mrliou_MRL_envelope(
                    {
                        "state": "corpus_unavailable",
                        "expected": "core/particle_dict.json",
                    }
                ),
            )
        particles = corpus.get("particles", {})
        names: List[str] = sorted(particles) if isinstance(particles, dict) else []
        return _Mrliou_MRL_envelope({"count": len(names), "fx": names})

    @app.get("/mrl/particles/{fx}")
    def mrl_particle(fx: str) -> Dict[str, Any]:
        corpus = Mrliou_MRL_load_particle_dict()
        if corpus is None:
            raise HTTPException(
                status_code=503,
                detail=_Mrliou_MRL_envelope(
                    {
                        "state": "corpus_unavailable",
                        "expected": "core/particle_dict.json",
                    }
                ),
            )
        particles = corpus.get("particles", {})
        if not isinstance(particles, dict) or fx not in particles:
            raise HTTPException(
                status_code=404,
                detail=_Mrliou_MRL_envelope({"state": "not_found", "fx": fx}),
            )
        return _Mrliou_MRL_envelope({"fx": fx, "particle": particles[fx]})

    def _schema_pending(path: str) -> Dict[str, Any]:
        raise HTTPException(
            status_code=503, detail=_Mrliou_MRL_schema_pending_detail(path)
        )

    @app.get("/mrl/persona")
    def mrl_persona() -> Dict[str, Any]:
        return _schema_pending("/mrl/persona")

    @app.get("/mrl/memory")
    def mrl_memory() -> Dict[str, Any]:
        return _schema_pending("/mrl/memory")

    @app.get("/mrl/files")
    def mrl_files() -> Dict[str, Any]:
        return _schema_pending("/mrl/files")

    return app


def Mrliou_MRL_run_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
) -> None:  # pragma: no cover - 需要真的開 port
    """啟動伺服器。綁定位址違反 PHASE1 時在開 port 之前就拒絕。"""
    import uvicorn

    resolved_host, resolved_port = Mrliou_MRL_resolve_bind(host, port)
    uvicorn.run(create_app(), host=resolved_host, port=resolved_port)


__all__ = [
    "ALLOW_PUBLIC_BIND_ENV",
    "MrlApiBindRefused",
    "Mrliou_MRL_allow_public_bind",
    "Mrliou_MRL_is_public_bind",
    "Mrliou_MRL_load_particle_dict",
    "Mrliou_MRL_locate_particle_dict",
    "Mrliou_MRL_resolve_bind",
    "Mrliou_MRL_run_server",
    "NETWORK_PHASE",
    "ORIGIN_SIGNATURE",
    "PARTICLE_DICT_ENV",
    "create_app",
]
