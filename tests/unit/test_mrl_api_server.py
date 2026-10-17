"""
測試 MRL API 伺服器

重點不只是「路由會回 200」，而是三條邊界守住了：
- 每條路由都綁到母體 MRL_API_CORE 既有的成員，不能自造名字
- LAW-1 的三表 schema 未找回之前，對應路由回 schema_pending 而不是假資料
- 綁定到會曝露所有介面的位址時，預設拒絕啟動（PHASE1_PRIVATE_LAN_ONLY）
"""

import json

import pytest

from mrliouword_agents.api import (
    ALLOW_PUBLIC_BIND_ENV,
    ENDPOINTS,
    LAW1_TABLES,
    MOTHER_MEMBERS,
    PARTICLE_DICT_ENV,
    STATES,
    MrlApiBindRefused,
    MrlApiEndpoint,
    Mrliou_MRL_contract_payload,
    Mrliou_MRL_endpoint_for,
    Mrliou_MRL_is_public_bind,
    Mrliou_MRL_load_particle_dict,
    Mrliou_MRL_locate_particle_dict,
    Mrliou_MRL_resolve_bind,
)

ORIGIN = "MrLiouWord"


# ── 契約表：母體綁定 ──────────────────────────────────────────────


def test_every_endpoint_binds_a_mother_member():
    """每條路由都必須指名它實作的母體成員"""
    for endpoint in ENDPOINTS:
        assert endpoint.mother_member in MOTHER_MEMBERS
        assert endpoint.state in STATES


def test_endpoint_paths_are_unique():
    """同一條路徑不得綁兩個成員"""
    paths = [endpoint.path for endpoint in ENDPOINTS]
    assert len(paths) == len(set(paths))


def test_cannot_invent_a_mother_member():
    """本倉庫 naming_authority: false——自造成員必須被拒"""
    with pytest.raises(ValueError):
        MrlApiEndpoint(
            path="/mrl/invented",
            mother_member="MRL_INVENTED_API",
            state="available",
            summary="不該被接受",
        )


def test_unknown_state_is_rejected():
    with pytest.raises(ValueError):
        MrlApiEndpoint(
            path="/mrl/health",
            mother_member="MRL_HEALTH_API",
            state="definitely_not_a_state",
            summary="不該被接受",
        )


def test_endpoint_lookup_raises_for_unknown_path():
    """查不到就丟 KeyError，不回預設值"""
    with pytest.raises(KeyError):
        Mrliou_MRL_endpoint_for("/mrl/does-not-exist")


def test_contract_payload_declares_derivative_role():
    """契約必須公布自己是 implementation，不是那個 CORE"""
    payload = Mrliou_MRL_contract_payload()
    assert payload["mother_core"] == "MRL_API_CORE"
    assert payload["derivative_role"] == "implementation"
    assert payload["canonical_authority"] == "Mr.liou"
    assert payload["origin_signature"] == ORIGIN


# ── PHASE1_PRIVATE_LAN_ONLY ───────────────────────────────────────


@pytest.mark.parametrize(
    "host,expected",
    [
        ("0.0.0.0", True),
        ("::", True),
        ("127.0.0.1", False),
        ("::1", False),
        ("192.168.1.5", False),
        ("10.0.0.3", False),
        ("mrl-runtime", False),
    ],
)
def test_public_bind_detection(host, expected):
    assert Mrliou_MRL_is_public_bind(host) is expected


def test_resolve_bind_refuses_public_bind_by_default(monkeypatch):
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)
    with pytest.raises(MrlApiBindRefused) as excinfo:
        Mrliou_MRL_resolve_bind(host="0.0.0.0", port=8000)
    assert "PHASE1_PRIVATE_LAN_ONLY" in str(excinfo.value)


def test_resolve_bind_allows_public_bind_with_explicit_optin(monkeypatch):
    monkeypatch.setenv(ALLOW_PUBLIC_BIND_ENV, "1")
    host, port = Mrliou_MRL_resolve_bind(host="0.0.0.0", port=8123)
    assert (host, port) == ("0.0.0.0", 8123)


def test_resolve_bind_passes_loopback(monkeypatch):
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)
    assert Mrliou_MRL_resolve_bind(host="127.0.0.1", port=8000) == ("127.0.0.1", 8000)


# ── 母體語料：唯讀 ────────────────────────────────────────────────


def test_locates_repo_particle_dict(monkeypatch):
    monkeypatch.delenv(PARTICLE_DICT_ENV, raising=False)
    located = Mrliou_MRL_locate_particle_dict()
    assert located is not None
    assert located.name == "particle_dict.json"


def test_particle_dict_env_override(monkeypatch, tmp_path):
    corpus = {"version": "test", "origin": ORIGIN, "particles": {"fx.test": {}}}
    target = tmp_path / "particle_dict.json"
    target.write_text(json.dumps(corpus), encoding="utf-8")
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(target))
    assert Mrliou_MRL_load_particle_dict() == corpus


def test_missing_corpus_returns_none_instead_of_raising(monkeypatch, tmp_path):
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(tmp_path / "nope.json"))
    assert Mrliou_MRL_load_particle_dict() is None


def test_malformed_corpus_returns_none(monkeypatch, tmp_path):
    broken = tmp_path / "particle_dict.json"
    broken.write_text("{ not json", encoding="utf-8")
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(broken))
    assert Mrliou_MRL_load_particle_dict() is None


# ── HTTP 行為 ─────────────────────────────────────────────────────


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient

    from mrliouword_agents.api import create_app

    return TestClient(create_app())


@pytest.mark.parametrize(
    "path",
    ["/mrl/health", "/mrl/status", "/mrl/runtime", "/mrl/contract"],
)
def test_available_routes_respond_with_origin_signature(client, path):
    """LAW-0：對外寫出的簽名恆為正規形 MrLiouWord"""
    response = client.get(path)
    assert response.status_code == 200
    assert response.json()["origin_signature"] == ORIGIN


def test_status_reports_corpus_state(client):
    body = client.get("/mrl/status").json()
    assert body["network_phase"] == "PHASE1_PRIVATE_LAN_ONLY"
    assert body["particle_dict_loaded"] is True
    assert body["particle_count"] > 0


def test_world_serves_mother_corpus(client):
    body = client.get("/mrl/world").json()
    assert body["corpus_origin"] == ORIGIN
    assert body["philosophy"] == "怎麼過去，就怎麼回來"
    assert len(body["domains"]) > 0


def test_particles_list_and_single(client):
    listing = client.get("/mrl/particles").json()
    assert listing["count"] == len(listing["fx"])
    assert listing["count"] > 0

    first = listing["fx"][0]
    single = client.get(f"/mrl/particles/{first}").json()
    assert single["fx"] == first
    assert single["origin_signature"] == ORIGIN


def test_unknown_particle_is_404(client):
    response = client.get("/mrl/particles/fx.definitely.not.here")
    assert response.status_code == 404
    assert response.json()["detail"]["state"] == "not_found"


@pytest.mark.parametrize("path", ["/mrl/persona", "/mrl/memory", "/mrl/files"])
def test_law1_routes_report_schema_pending_not_fake_data(client, path):
    """schema 未找回之前不供資料、不猜欄位"""
    response = client.get(path)
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["state"] == "schema_pending"
    assert detail["law"] == "LAW-1"
    assert detail["pending_tables"] == list(LAW1_TABLES)
    assert detail["origin_signature"] == ORIGIN


def test_no_route_outside_the_contract(client):
    """應用註冊的 /mrl 路由不得超出契約表"""
    contract_paths = {endpoint.path for endpoint in ENDPOINTS}
    contract_paths.add("/mrl/particles/{fx}")  # 契約以 /mrl/particles 一條涵蓋
    registered = {
        route.path
        for route in client.app.routes
        if getattr(route, "path", "").startswith("/mrl")
    }
    assert registered == contract_paths
