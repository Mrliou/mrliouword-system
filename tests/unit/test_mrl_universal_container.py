"""MRL WORLD / UNIVERSAL CONTAINER 行為驗證。"""
from dataclasses import replace

import pytest

from mrliouword_agents.core.mrl_universal_container import (
    MRLUniversalContainer,
    SnapshotIntegrityError,
)


def test_attention_or_intention_creates_running_space():
    mother = MRLUniversalContainer()

    space = mother.create_space(
        intention="建立音樂空間",
        attention="節奏與聲音",
        initial_state={"frequency": 7.83},
        space_id="music-space",
    )

    assert space.status == "running"
    assert space.state == {"frequency": 7.83}
    assert space.origin_signature == "MrLiou"
    assert [event.event_type for event in mother.event_ledger()] == ["create_space"]


def test_evolve_and_restore_preserve_reversible_lineage():
    mother = MRLUniversalContainer()
    mother.create_space("建立工作室", initial_state={"light": "warm"}, space_id="studio")
    original = mother.snapshot("studio")

    evolved = mother.evolve("studio", {"light": "blue", "tools": ["voice"]}, "加入語音工具")
    restored = mother.restore(original, new_space_id="studio-return")

    assert evolved.state == {"light": "blue", "tools": ["voice"]}
    assert restored.state == {"light": "warm"}
    assert restored.parent_space_ids == ("studio",)
    assert mother.get_space("studio").state == evolved.state


def test_combine_preserves_conflicting_world_states_instead_of_flattening():
    mother = MRLUniversalContainer()
    mother.create_space(
        intention="世界甲",
        attention="甲視角",
        initial_state={"answer": "A"},
        space_id="world-a",
    )
    mother.create_space(
        intention="世界乙",
        attention="乙視角",
        initial_state={"answer": "B"},
        space_id="world-b",
    )

    combined = mother.combine(("world-a", "world-b"), "同時觀看兩個世界", space_id="world-ab")
    sources = combined.state["composition"]["source_spaces"]

    assert sources["world-a"]["state"]["answer"] == "A"
    assert sources["world-b"]["state"]["answer"] == "B"
    assert combined.parent_space_ids == ("world-a", "world-b")


def test_projection_appends_viewpoint_history_without_redefining_space():
    mother = MRLUniversalContainer()
    mother.create_space("建立搜尋空間", space_id="search")

    mother.project("search", "AGI-browser", {"surface": "Bing AI"})
    projected = mother.project("search", "AGI-browser", {"surface": "another view"})

    assert projected.intention == "建立搜尋空間"
    assert len(projected.perspectives["AGI-browser"]) == 2
    assert projected.perspectives["AGI-browser"][0]["observation"]["surface"] == "Bing AI"


def test_tampered_snapshot_is_rejected():
    mother = MRLUniversalContainer()
    mother.create_space("建立新世界", initial_state={"seed": 1}, space_id="seed")
    snapshot = mother.snapshot("seed")
    tampered = replace(snapshot, payload={**snapshot.payload, "state": {"seed": 2}})

    with pytest.raises(SnapshotIntegrityError):
        mother.restore(tampered)
