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
    BIND_LOOPBACK,
    BIND_PRIVATE,
    BIND_PUBLIC,
    BIND_UNRESOLVABLE,
    BIND_UNSPECIFIED,
    ENVIRONMENT_ENV,
    ENV_DL580,
    ENV_UNSPECIFIED,
    PERMITTED_BIND_CLASSES,
    ENDPOINTS,
    LAW1_TABLES,
    MOTHER_MEMBERS,
    PARTICLE_DICT_ENV,
    STATES,
    MrlApiBindRefused,
    MrlApiEndpoint,
    Mrliou_MRL_classify_bind,
    Mrliou_MRL_corpus_is_wellformed,
    Mrliou_MRL_declared_environment,
    Mrliou_MRL_resolve_workers,
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
    "host,expected_class",
    [
        ("127.0.0.1", BIND_LOOPBACK),
        ("::1", BIND_LOOPBACK),
        ("localhost", BIND_LOOPBACK),
        ("192.168.1.5", BIND_PRIVATE),
        ("10.0.0.3", BIND_PRIVATE),
        ("172.16.0.1", BIND_PRIVATE),
        ("fc00::1", BIND_PRIVATE),
        ("0.0.0.0", BIND_UNSPECIFIED),
        ("::", BIND_UNSPECIFIED),
        ("8.8.8.8", BIND_PUBLIC),
        ("1.1.1.1", BIND_PUBLIC),
        ("mrl-host.invalid", BIND_UNRESOLVABLE),
    ],
)
def test_bind_classification(host, expected_class):
    assert Mrliou_MRL_classify_bind(host) == expected_class


@pytest.mark.parametrize(
    "host,expected",
    [
        ("127.0.0.1", False),
        ("192.168.1.5", False),
        ("fc00::1", False),
        # 以下四種以前全被放過去，這是 Codex P1 指出的繞過
        ("0.0.0.0", True),
        ("::", True),
        ("8.8.8.8", True),
        ("mrl-host.invalid", True),
    ],
)
def test_public_bind_detection(host, expected):
    """只擋 wildcard 是不夠的：可全球路由的位址與解析不出來的主機名也要擋"""
    assert Mrliou_MRL_is_public_bind(host) is expected


def test_permitted_classes_are_only_loopback_and_private():
    assert PERMITTED_BIND_CLASSES == (BIND_LOOPBACK, BIND_PRIVATE)


@pytest.mark.parametrize("host", ["8.8.8.8", "1.1.1.1", "mrl-host.invalid", "::"])
def test_resolve_bind_refuses_anything_outside_private_lan(monkeypatch, host):
    """公開位址、解析失敗的主機名，預設都要被拒——PHASE1 從嚴"""
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)
    with pytest.raises(MrlApiBindRefused) as excinfo:
        Mrliou_MRL_resolve_bind(host=host, port=8000)
    assert "PHASE1_PRIVATE_LAN_ONLY" in str(excinfo.value)


@pytest.mark.parametrize("host", ["127.0.0.1", "192.168.1.5", "10.0.0.3", "fc00::1"])
def test_resolve_bind_allows_private_lan(monkeypatch, host):
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)
    assert Mrliou_MRL_resolve_bind(host=host, port=8000) == (host, 8000)


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


# ── Codex 審查補上的覆蓋 ──────────────────────────────────────────


def test_malformed_corpus_shapes_are_rejected(monkeypatch, tmp_path):
    """{"particles": null} 以前會讓 /mrl/status 在 len(None) 爆 500"""
    for payload in (
        {"origin": "MrLiouWord", "particles": None},
        {"origin": "MrLiouWord", "domains": []},
        {"origin": 123},
        {"particles": {}},
        [],
    ):
        target = tmp_path / "particle_dict.json"
        target.write_text(json.dumps(payload), encoding="utf-8")
        monkeypatch.setenv(PARTICLE_DICT_ENV, str(target))
        assert Mrliou_MRL_corpus_is_wellformed(payload) is False
        assert Mrliou_MRL_load_particle_dict() is None


def test_status_does_not_crash_on_malformed_corpus(monkeypatch, tmp_path):
    target = tmp_path / "particle_dict.json"
    target.write_text(
        json.dumps({"origin": "MrLiouWord", "particles": None}), encoding="utf-8"
    )
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(target))

    from fastapi.testclient import TestClient

    from mrliouword_agents.api import create_app

    response = TestClient(create_app()).get("/mrl/status")
    assert response.status_code == 200
    body = response.json()
    assert body["particle_dict_loaded"] is False
    assert body["particle_count"] == 0


def test_corpus_unavailable_names_the_override_env(monkeypatch, tmp_path):
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(tmp_path / "nope.json"))

    from fastapi.testclient import TestClient

    from mrliouword_agents.api import create_app

    response = TestClient(create_app()).get("/mrl/world")
    assert response.status_code == 503
    detail = response.json()["detail"]
    assert detail["state"] == "corpus_unavailable"
    assert PARTICLE_DICT_ENV in detail["hint"]


def test_framework_404_carries_origin_signature(client):
    """LAW-0 也要蓋到框架自己產生的回應"""
    response = client.get("/mrl/definitely-not-a-route")
    assert response.status_code == 404
    assert response.json()["origin_signature"] == ORIGIN


def test_framework_405_carries_origin_signature(client):
    response = client.post("/mrl/health")
    assert response.status_code == 405
    assert response.json()["origin_signature"] == ORIGIN


def test_workers_follow_config():
    """api_workers 以前完全沒有被讀到"""
    from mrliouword_agents.core.config import config as runtime_config

    assert Mrliou_MRL_resolve_workers() == max(1, runtime_config.api_workers)
    assert Mrliou_MRL_resolve_workers(3) == 3
    assert Mrliou_MRL_resolve_workers(0) == 1


def test_runtime_returns_what_the_contract_advertises(monkeypatch):
    """契約說會回報宣告的環境與綁定目標，就必須真的有"""
    monkeypatch.setenv(ENVIRONMENT_ENV, ENV_DL580)

    from fastapi.testclient import TestClient

    from mrliouword_agents.api import create_app

    body = TestClient(create_app(bind=("127.0.0.1", 8000))).get("/mrl/runtime").json()
    assert body["declared_environment"] == ENV_DL580
    assert body["environment_is_declared_not_detected"] is True
    assert body["bind_host"] == "127.0.0.1"
    assert body["bind_port"] == 8000
    assert body["bind_class"] == BIND_LOOPBACK


def test_environment_is_declared_not_guessed(monkeypatch):
    """沒宣告或值不認識時回 unspecified，不自行猜測"""
    monkeypatch.delenv(ENVIRONMENT_ENV, raising=False)
    assert Mrliou_MRL_declared_environment() == ENV_UNSPECIFIED
    monkeypatch.setenv(ENVIRONMENT_ENV, "whatever")
    assert Mrliou_MRL_declared_environment() == ENV_UNSPECIFIED


def test_runtime_bind_is_null_when_unknown(client):
    """直接 create_app() 時不編一個綁定位址出來"""
    body = client.get("/mrl/runtime").json()
    assert body["bind_host"] is None
    assert body["bind_class"] is None



# origin_signature: MrLiouWord
@pytest.mark.parametrize("workers", [1, 3])
def test_launcher_worker_factory_reports_the_selected_bind(monkeypatch, workers):
    """A fresh interpreter must see the launcher bind, as Windows workers do."""
    import importlib
    import os
    import subprocess
    import sys

    server = importlib.import_module(
        "mrliouword_agents.api.Mrliou_MRL_Api_Server_v1"
    )
    previous = '{"previous": "launch"}'
    monkeypatch.setenv(server._MRL_LAUNCH_BIND_ENV, previous)
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)
    observed = {}

    def fake_uvicorn_run(app, **options):
        module_name, factory_name = app.split(":")
        child = (
            "import importlib,json; from fastapi.testclient import TestClient; "
            f"factory=getattr(importlib.import_module({module_name!r}),"
            f"{factory_name!r}); "
            "print(json.dumps(TestClient(factory()).get('/mrl/runtime').json()))"
        )
        output = subprocess.check_output(
            [sys.executable, "-c", child], env=os.environ.copy(), text=True
        )
        observed.update(json.loads(output))
        assert options["host"] == "127.0.0.1"
        assert options["port"] == 8127
        assert options["workers"] == workers
        assert options["factory"] is True

    monkeypatch.setattr("uvicorn.run", fake_uvicorn_run)
    server.Mrliou_MRL_run_server(host="127.0.0.1", port=8127, workers=workers)
    assert observed["bind_host"] == "127.0.0.1"
    assert observed["bind_port"] == 8127
    assert observed["bind_class"] == BIND_LOOPBACK
    assert observed["origin_signature"] == ORIGIN
    assert os.environ[server._MRL_LAUNCH_BIND_ENV] == previous


def test_launcher_restores_environment_after_startup_failure(monkeypatch):
    import importlib
    import os

    server = importlib.import_module(
        "mrliouword_agents.api.Mrliou_MRL_Api_Server_v1"
    )
    monkeypatch.delenv(server._MRL_LAUNCH_BIND_ENV, raising=False)
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)

    def fail_start(*args, **kwargs):
        raise RuntimeError("fixture startup failure")

    monkeypatch.setattr("uvicorn.run", fail_start)
    with pytest.raises(RuntimeError, match="fixture startup failure"):
        server.Mrliou_MRL_run_server(host="127.0.0.1", port=8127, workers=3)
    assert server._MRL_LAUNCH_BIND_ENV not in os.environ


@pytest.mark.parametrize(
    "metadata",
    [None, "not-json", '["127.0.0.1", true]', '["127.0.0.1", 0]'],
)
def test_worker_factory_rejects_missing_or_invalid_bind(monkeypatch, metadata):
    import importlib

    server = importlib.import_module(
        "mrliouword_agents.api.Mrliou_MRL_Api_Server_v1"
    )
    if metadata is None:
        monkeypatch.delenv(server._MRL_LAUNCH_BIND_ENV, raising=False)
    else:
        monkeypatch.setenv(server._MRL_LAUNCH_BIND_ENV, metadata)
    with pytest.raises(MrlApiBindRefused):
        server._Mrliou_MRL_create_server_app()


def test_worker_factory_rechecks_private_lan_boundary(monkeypatch):
    import importlib

    server = importlib.import_module(
        "mrliouword_agents.api.Mrliou_MRL_Api_Server_v1"
    )
    monkeypatch.delenv(ALLOW_PUBLIC_BIND_ENV, raising=False)
    monkeypatch.setenv(server._MRL_LAUNCH_BIND_ENV, '["0.0.0.0", 8127]')
    with pytest.raises(MrlApiBindRefused):
        server._Mrliou_MRL_create_server_app()



def test_installed_wheel_uses_explicit_existing_corpus(monkeypatch, tmp_path):
    """A wheel outside the checkout must use the existing corpus, never copy it."""
    import hashlib
    import os
    from pathlib import Path
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[2]
    corpus = root / "core" / "particle_dict.json"
    before = hashlib.sha256(corpus.read_bytes()).hexdigest()
    wheel_dir = tmp_path / "wheels"
    wheel_dir.mkdir()
    subprocess.run(
        [
            sys.executable, "-m", "pip", "wheel", "--no-index", "--no-deps",
            "--no-build-isolation", "--wheel-dir", str(wheel_dir), str(root),
        ],
        check=True, capture_output=True, text=True,
    )
    wheels = list(wheel_dir.glob("*.whl"))
    assert len(wheels) == 1
    wheel = str(wheels[0])
    script = (
        "import json; from fastapi.testclient import TestClient; "
        "import mrliouword_agents.api.Mrliou_MRL_Api_Server_v1 as server; "
        f"assert server.__file__.startswith({wheel!r}); "
        "response=TestClient(server.create_app()).get('/mrl/world'); "
        "print(json.dumps({'status': response.status_code, 'body': response.json()}))"
    )
    environment = os.environ.copy()
    environment["PYTHONPATH"] = wheel
    environment.pop(PARTICLE_DICT_ENV, None)
    missing = json.loads(subprocess.check_output(
        [sys.executable, "-c", script], cwd=tmp_path,
        env=environment, text=True,
    ))
    assert missing["status"] == 503
    environment[PARTICLE_DICT_ENV] = str(corpus)
    loaded = json.loads(subprocess.check_output(
        [sys.executable, "-c", script], cwd=tmp_path,
        env=environment, text=True,
    ))
    assert loaded["status"] == 200
    assert loaded["body"]["corpus_origin"] == ORIGIN
    assert loaded["body"]["philosophy"] == "怎麼過去，就怎麼回來"
    assert hashlib.sha256(corpus.read_bytes()).hexdigest() == before



@pytest.mark.parametrize(
    "declarations",
    [
        {"origin": "ExternalVendor"},
        {"origin": ORIGIN, "origin_signature": "ExternalVendor"},
        {"origin": "ExternalVendor", "origin_signature": ORIGIN},
        {},
        {"origin": ""},
        {"origin": "   "},
        {"origin": None},
        {"origin": 123},
        {"origin": ORIGIN, "origin_signature": None},
        {"origin": ORIGIN, "origin_signature": ""},
        {"origin": ORIGIN, "canonical_authority": "ExternalVendor"},
        {"origin": "mrliouword"},
        {"origin": "Mr.liou"},
        {"origin": "dofaromg"},
    ],
)
def test_corpus_authority_rejected_without_source_rewrite(
    monkeypatch, tmp_path, declarations
):
    """Namespace, human authority and contributor names are not origin signatures."""
    import hashlib

    from fastapi.testclient import TestClient

    from mrliouword_agents.api import create_app

    corpus = {"particles": {"fx.test": {"hv": "untrusted"}}, **declarations}
    target = tmp_path / "corpus.json"
    target.write_text(json.dumps(corpus), encoding="utf-8")
    before = hashlib.sha256(target.read_bytes()).hexdigest()
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(target))
    assert Mrliou_MRL_corpus_is_wellformed(corpus) is False
    assert Mrliou_MRL_load_particle_dict() is None
    with TestClient(create_app()) as client:
        status = client.get("/mrl/status").json()
        assert status["particle_dict_loaded"] is False
        assert status["particle_count"] == 0
        for route in ("/mrl/world", "/mrl/particles", "/mrl/particles/fx.test"):
            response = client.get(route)
            assert response.status_code == 503
            body = response.json()
            assert body["signature_scope"] == "api_implementation"
            assert body["detail"]["state"] == "corpus_unavailable"
            assert "corpus_origin" not in body
            assert "particle" not in body
    assert hashlib.sha256(target.read_bytes()).hexdigest() == before


@pytest.mark.parametrize(
    "declarations",
    [
        {"origin": ORIGIN},
        {"origin_signature": ORIGIN},
        {"origin": ORIGIN, "origin_signature": ORIGIN},
        {"origin": ORIGIN, "canonical_authority": "Mr.liou"},
    ],
)
def test_canonical_corpus_source_key_aliases_preserved(
    monkeypatch, tmp_path, declarations
):
    from fastapi.testclient import TestClient

    from mrliouword_agents.api import create_app

    corpus = {"particles": {"fx.test": {}}, **declarations}
    target = tmp_path / "corpus.json"
    target.write_text(json.dumps(corpus), encoding="utf-8")
    original = target.read_bytes()
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(target))
    assert Mrliou_MRL_corpus_is_wellformed(corpus) is True
    assert Mrliou_MRL_load_particle_dict() == corpus
    with TestClient(create_app()) as client:
        response = client.get("/mrl/world")
        assert response.status_code == 200
        assert response.json()["corpus_origin"] == ORIGIN
        assert response.json()["signature_scope"] == "api_implementation"
        assert client.get("/mrl/particles/fx.test").status_code == 200
    assert target.read_bytes() == original


def test_duplicate_source_declarations_fail_closed(monkeypatch, tmp_path):
    target = tmp_path / "corpus.json"
    target.write_text(
        '{"origin":"ExternalVendor","origin":"MrLiouWord","particles":{}}',
        encoding="utf-8",
    )
    monkeypatch.setenv(PARTICLE_DICT_ENV, str(target))
    assert Mrliou_MRL_load_particle_dict() is None
