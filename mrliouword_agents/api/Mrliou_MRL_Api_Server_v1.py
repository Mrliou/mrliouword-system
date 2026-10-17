"""
MRL API 伺服器：母體 MRL_API_CORE 的實作

邊界
----
- **本模組是 MRL_API_CORE 的 implementation，不是那個 CORE。** 路由與母體成員的
  綁定寫在 Mrliou_MRL_Api_Contract_v1，沒有對應成員的路由不得存在。
- **不建立、不變更任何資料庫表。** LAW-1 說 DL580 上的 PostgreSQL 仍是權威持久層；
  System A 三表的 schema 目前記為「待找回」，所以 persona / memory / files 三條
  路由只登記存在並回報 schema_pending，不猜測欄位。
- **母體語料只讀不寫。** core/particle_dict.json 是 canonical 語料，本模組只讀取，
  也不把它複製進套件（見 Mrliou_MRL_locate_particle_dict 的說明）。
- **PHASE1_PRIVATE_LAN_ONLY。** 只允許綁定 loopback 或私有位址；未指定位址、
  可全球路由的位址、以及解析不出來的主機名一律拒絕，除非以
  MRL_API_ALLOW_PUBLIC_BIND 明確開啟。
- **LAW-0。** 每個回應都帶 origin_signature，恆為正規形 MrLiouWord
  ——包含框架自己產生的 404 / 405 / 422。
"""

from __future__ import annotations

import ipaddress
import json
import os
import platform
import socket
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from . import Mrliou_MRL_Api_Contract_v1 as contract

#: LAW-0：對外寫出的來源簽名恆為正規形
ORIGIN_SIGNATURE = contract.ORIGIN_SIGNATURE

#: registry 條目宣告的網路階段
NETWORK_PHASE = "PHASE1_PRIVATE_LAN_ONLY"

#: 要綁定到私有網段之外必須明確設這個環境變數
ALLOW_PUBLIC_BIND_ENV = "MRL_API_ALLOW_PUBLIC_BIND"

#: 母體語料的位置覆寫；套件安裝情境下必須設它，見 locate 函式說明
PARTICLE_DICT_ENV = "MRL_PARTICLE_DICT"
PARTICLE_DICT_RELATIVE = Path("core") / "particle_dict.json"

#: 執行環境由呼叫端**宣告**，不自動偵測。沿用
#: modules/MRL_SystemA_ParticleLayer/Mrliou_MRL_Law2_Report_v1.py 的詞彙與理由：
#: 「沙盒結果不得被讀成 DL580 實機結果」，所以環境是宣告的，不是猜的。
ENVIRONMENT_ENV = "MRL_API_ENVIRONMENT"
ENV_SANDBOX = "sandbox"
ENV_DL580 = "dl580"
ENV_UNSPECIFIED = "unspecified"
KNOWN_ENVIRONMENTS: Tuple[str, ...] = (ENV_SANDBOX, ENV_DL580, ENV_UNSPECIFIED)

#: 綁定位址分類
BIND_LOOPBACK = "loopback"
BIND_PRIVATE = "private"
BIND_PUBLIC = "public"
BIND_UNSPECIFIED = "unspecified"
BIND_UNRESOLVABLE = "unresolvable"

#: PHASE1 允許的分類。其餘一律需要明確開啟。
PERMITTED_BIND_CLASSES: Tuple[str, ...] = (BIND_LOOPBACK, BIND_PRIVATE)

#: 判定嚴重性排序：解析出多個位址時取最寬鬆者的最壞情況
_BIND_SEVERITY: Tuple[str, ...] = (
    BIND_LOOPBACK,
    BIND_PRIVATE,
    BIND_PUBLIC,
    BIND_UNRESOLVABLE,
    BIND_UNSPECIFIED,
)


class MrlApiBindRefused(RuntimeError):
    """綁定位址違反 PHASE1_PRIVATE_LAN_ONLY，拒絕啟動"""


def Mrliou_MRL_locate_particle_dict(start: Optional[Path] = None) -> Optional[Path]:
    """定位母體語料

    先看 MRL_PARTICLE_DICT；沒有就從本檔往上層目錄找 core/particle_dict.json。

    **套件安裝情境必須設 MRL_PARTICLE_DICT。** core/particle_dict.json 在
    mrliouword_agents 套件之外，而 setup.py 只做 find_packages()、沒有宣告
    package_data，所以 wheel 裡不會有它，往上找也找不到。這是刻意的：那份語料是
    canonical 母體語料，把它複製進套件會讓同一份 canonical 資料出現第二份副本。
    找不到時相關路由回 503 corpus_unavailable 並指名這個環境變數，
    不會自己造一份語料。
    """
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


def Mrliou_MRL_corpus_is_wellformed(payload: Any) -> bool:
    """語料是否具備本實作會讀到的欄位與型別

    只檢查本實作實際會取用的部分，不替母體定義 schema。任何一項型別不對就當成
    語料不可用，回 503，而不是讓後面的 len() 或迭代在執行期炸掉。
    """
    if not isinstance(payload, dict):
        return False
    if not isinstance(payload.get("origin"), str):
        return False
    for key in ("particles", "domains", "frequencies", "constants"):
        if key in payload and not isinstance(payload[key], dict):
            return False
    if "philosophy" in payload and not isinstance(payload["philosophy"], str):
        return False
    return True


def Mrliou_MRL_load_particle_dict(
    path: Optional[Path] = None,
) -> Optional[Dict[str, Any]]:
    """唯讀載入母體語料。檔案不存在、不是 JSON 物件、或欄位型別不符就回 None。"""
    located = path or Mrliou_MRL_locate_particle_dict()
    if located is None:
        return None
    try:
        with located.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return None
    return payload if Mrliou_MRL_corpus_is_wellformed(payload) else None


def Mrliou_MRL_classify_address(address: str) -> str:
    """把單一 IP 位址分類

    注意判定順序：ipaddress 把 0.0.0.0 與文件保留段都算 is_private，所以
    **不能**拿 is_private 當白名單。先排除未指定位址，再用 is_global 判斷
    是否可全球路由。
    """
    ip = ipaddress.ip_address(address)
    if ip.is_unspecified:
        return BIND_UNSPECIFIED
    if ip.is_global:
        return BIND_PUBLIC
    if ip.is_loopback:
        return BIND_LOOPBACK
    return BIND_PRIVATE


def Mrliou_MRL_classify_bind(host: str) -> str:
    """把綁定目標分類；主機名會先解析，並取解析結果的最壞情況

    解析不出來就回 unresolvable——**失敗時從嚴**，因為無法證明它在私有網段內。
    """
    target = host.strip()
    try:
        return Mrliou_MRL_classify_address(target)
    except ValueError:
        pass  # 不是字面位址，當主機名解析

    try:
        infos = socket.getaddrinfo(target, None)
    except (socket.gaierror, UnicodeError):
        return BIND_UNRESOLVABLE

    classes = set()
    for info in infos:
        sockaddr = info[4]
        if not sockaddr:
            continue
        try:
            classes.add(Mrliou_MRL_classify_address(str(sockaddr[0])))
        except ValueError:
            classes.add(BIND_UNRESOLVABLE)
    if not classes:
        return BIND_UNRESOLVABLE
    return max(classes, key=_BIND_SEVERITY.index)


def Mrliou_MRL_is_public_bind(host: str) -> bool:
    """這個綁定目標是否超出 PHASE1 允許的範圍"""
    return Mrliou_MRL_classify_bind(host) not in PERMITTED_BIND_CLASSES


def Mrliou_MRL_allow_public_bind() -> bool:
    """是否已明確開啟超出私有網段的綁定"""
    raw = os.environ.get(ALLOW_PUBLIC_BIND_ENV, "").strip().lower()
    return raw in {"1", "true", "yes", "on"}


def Mrliou_MRL_declared_environment() -> str:
    """呼叫端宣告的執行環境；未宣告或值不認識時回 unspecified，不自行猜測"""
    raw = os.environ.get(ENVIRONMENT_ENV, "").strip().lower()
    return raw if raw in KNOWN_ENVIRONMENTS else ENV_UNSPECIFIED


def Mrliou_MRL_resolve_bind(
    host: Optional[str] = None, port: Optional[int] = None
) -> Tuple[str, int]:
    """決定實際綁定的位址與連接埠，並在違反 PHASE1 時拒絕

    host / port 省略時取 MrliouwordConfig 的 api_host / api_port，
    所以 API_HOST、API_PORT 兩個環境變數照既有設定系統生效。
    """
    if host is None or port is None:
        from ..core.config import config as runtime_config

        host = host if host is not None else runtime_config.api_host
        port = port if port is not None else runtime_config.api_port

    bind_class = Mrliou_MRL_classify_bind(host)
    if bind_class not in PERMITTED_BIND_CLASSES and not Mrliou_MRL_allow_public_bind():
        raise MrlApiBindRefused(
            f"綁定目標 {host!r} 的分類是 {bind_class}，不在 PHASE1 允許的 "
            f"{PERMITTED_BIND_CLASSES} 之內，與 registry 宣告的 {NETWORK_PHASE} "
            f"不符，拒絕啟動。確定要這麼做請設定 {ALLOW_PUBLIC_BIND_ENV}=1，"
            "或把 API_HOST 設成 loopback 或內網位址。"
        )
    return host, int(port)


def Mrliou_MRL_resolve_workers(workers: Optional[int] = None) -> int:
    """實際使用的 worker 數；省略時取 MrliouwordConfig 的 api_workers"""
    if workers is None:
        from ..core.config import config as runtime_config

        workers = runtime_config.api_workers
    return max(1, int(workers))


def _Mrliou_MRL_envelope(payload: Dict[str, Any]) -> Dict[str, Any]:
    """LAW-0：所有回應統一帶上來源簽名與衍生角色"""
    enveloped: Dict[str, Any] = {
        "origin_signature": ORIGIN_SIGNATURE,
        "mother_core": contract.MOTHER_CORE,
        "derivative_role": contract.DERIVATIVE_ROLE,
    }
    enveloped.update(payload)
    return enveloped


def _Mrliou_MRL_is_enveloped(value: Any) -> bool:
    """這個 detail 是否已經帶過封套，避免重複包裝"""
    return isinstance(value, dict) and value.get("origin_signature") == ORIGIN_SIGNATURE


def _Mrliou_MRL_corpus_unavailable() -> Dict[str, Any]:
    return _Mrliou_MRL_envelope(
        {
            "state": "corpus_unavailable",
            "expected": str(PARTICLE_DICT_RELATIVE),
            "hint": (
                f"套件安裝情境請以 {PARTICLE_DICT_ENV} 指向 canonical 母體語料；"
                "本實作不會自行產生語料。"
            ),
        }
    )


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


def create_app(bind: Optional[Tuple[str, int]] = None) -> Any:
    """建立 FastAPI 應用

    bind 是已決定的 (host, port)，由 Mrliou_MRL_run_server 傳入，讓
    /mrl/runtime 能回報實際綁定目標。直接呼叫 create_app() 時為 None，
    /mrl/runtime 的 bind 欄位就回 null，而不是編一個值出來。
    """
    from fastapi import FastAPI, HTTPException
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse
    from starlette.exceptions import HTTPException as StarletteHTTPException

    from ..version import __version__

    app = FastAPI(
        title="MRL API",
        version=__version__,
        description=(
            "母體 MRL_API_CORE 的實作。路由與母體成員的綁定見 /mrl/contract；"
            "本服務不是該 CORE 本身，也不建立或變更任何資料庫表。"
        ),
    )

    # LAW-0 也要蓋到框架自己產生的錯誤回應（404 / 405 / 422），
    # 否則「每個回應都帶 origin_signature」這句話是假的。
    @app.exception_handler(StarletteHTTPException)
    async def _mrl_http_exception_handler(_request: Any, exc: Any) -> Any:
        detail = exc.detail
        if _Mrliou_MRL_is_enveloped(detail):
            body: Dict[str, Any] = dict(detail)
        else:
            body = _Mrliou_MRL_envelope({"state": "error", "detail": detail})
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": body, **_Mrliou_MRL_envelope({})},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    async def _mrl_validation_exception_handler(_request: Any, exc: Any) -> Any:
        body = _Mrliou_MRL_envelope(
            {"state": "validation_error", "errors": json.loads(exc.json())}
        )
        return JSONResponse(
            status_code=422, content={"detail": body, **_Mrliou_MRL_envelope({})}
        )

    @app.get("/mrl/health")
    def mrl_health() -> Dict[str, Any]:
        return _Mrliou_MRL_envelope({"state": "ok"})

    @app.get("/mrl/status")
    def mrl_status() -> Dict[str, Any]:
        corpus = Mrliou_MRL_load_particle_dict()
        particles = corpus.get("particles", {}) if corpus else {}
        return _Mrliou_MRL_envelope(
            {
                "state": "ok",
                "version": __version__,
                "network_phase": NETWORK_PHASE,
                "particle_dict_loaded": corpus is not None,
                "particle_count": len(particles),
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
                "declared_environment": Mrliou_MRL_declared_environment(),
                "environment_is_declared_not_detected": True,
                "bind_host": bind[0] if bind else None,
                "bind_port": bind[1] if bind else None,
                "bind_class": Mrliou_MRL_classify_bind(bind[0]) if bind else None,
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
                status_code=503, detail=_Mrliou_MRL_corpus_unavailable()
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
                status_code=503, detail=_Mrliou_MRL_corpus_unavailable()
            )
        particles = corpus.get("particles", {})
        names: List[str] = sorted(particles)
        return _Mrliou_MRL_envelope({"count": len(names), "fx": names})

    @app.get("/mrl/particles/{fx}")
    def mrl_particle(fx: str) -> Dict[str, Any]:
        corpus = Mrliou_MRL_load_particle_dict()
        if corpus is None:
            raise HTTPException(
                status_code=503, detail=_Mrliou_MRL_corpus_unavailable()
            )
        particles = corpus.get("particles", {})
        if fx not in particles:
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


#: Mrliou_MRL_run_server 以 import string 啟動，worker 數才會生效
APP_FACTORY_IMPORT_STRING = "mrliouword_agents.api.Mrliou_MRL_Api_Server_v1:create_app"


def Mrliou_MRL_run_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
    workers: Optional[int] = None,
) -> None:  # pragma: no cover - 需要真的開 port
    """啟動伺服器。綁定目標違反 PHASE1 時在開 port 之前就拒絕。

    worker 數取 MrliouwordConfig 的 api_workers（環境變數 API_WORKERS）。
    uvicorn 只有在應用以 import string 傳入時才會套用 workers，所以這裡用
    APP_FACTORY_IMPORT_STRING 而不是現成的 app 物件。
    """
    import uvicorn

    resolved_host, resolved_port = Mrliou_MRL_resolve_bind(host, port)
    resolved_workers = Mrliou_MRL_resolve_workers(workers)
    uvicorn.run(
        APP_FACTORY_IMPORT_STRING,
        factory=True,
        host=resolved_host,
        port=resolved_port,
        workers=resolved_workers,
    )


__all__ = [
    "ALLOW_PUBLIC_BIND_ENV",
    "APP_FACTORY_IMPORT_STRING",
    "BIND_LOOPBACK",
    "BIND_PRIVATE",
    "BIND_PUBLIC",
    "BIND_UNRESOLVABLE",
    "BIND_UNSPECIFIED",
    "ENVIRONMENT_ENV",
    "ENV_DL580",
    "ENV_SANDBOX",
    "ENV_UNSPECIFIED",
    "KNOWN_ENVIRONMENTS",
    "MrlApiBindRefused",
    "Mrliou_MRL_allow_public_bind",
    "Mrliou_MRL_classify_address",
    "Mrliou_MRL_classify_bind",
    "Mrliou_MRL_corpus_is_wellformed",
    "Mrliou_MRL_declared_environment",
    "Mrliou_MRL_is_public_bind",
    "Mrliou_MRL_load_particle_dict",
    "Mrliou_MRL_locate_particle_dict",
    "Mrliou_MRL_resolve_bind",
    "Mrliou_MRL_resolve_workers",
    "Mrliou_MRL_run_server",
    "NETWORK_PHASE",
    "ORIGIN_SIGNATURE",
    "PARTICLE_DICT_ENV",
    "PERMITTED_BIND_CLASSES",
    "create_app",
]
