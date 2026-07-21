"""
測試背景運行記憶同步
"""
import json

import pytest

from mrliouword_agents.agents.data_analyzer import MrliouwordDataAnalyzer
from mrliouword_agents.core.config import config
from mrliouword_agents.core.runtime_memory import ParticleRuntimeMemory


def _write_particle_dict(path):
    payload = {
        "particles": {
            "fx.flow.start": {"fx": "fx.flow.start", "dom": "flow"},
            "fx.flow.end": {"fx": "fx.flow.end", "dom": "flow"},
            "fx.trace.anchor": {"fx": "fx.trace.anchor", "dom": "trace"},
            "fx.logic.analyze": {"fx": "fx.logic.analyze", "dom": "logic"},
        }
    }
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


@pytest.mark.asyncio
async def test_runtime_memory_persists_records(tmp_path):
    """背景保存會寫入對應 Agent 記憶檔"""
    particle_dict_path = tmp_path / "particle_dict.json"
    _write_particle_dict(particle_dict_path)

    memory = ParticleRuntimeMemory(
        storage_dir=str(tmp_path / "runtime_memory"),
        particle_dict_path=str(particle_dict_path),
    )

    await memory.record("DataAnalyzer", "execution.start", {"step": "boot"})
    await memory.record(
        "DataAnalyzer",
        "execution.message",
        {"message": "分析中", "artifacts": ["/tmp/input.csv"]},
        upstream={
            "function": "execute",
            "inputs": {"file_path": "/tmp/input.csv", "full_analysis": False},
            "paths": ["/tmp/input.csv"],
            "primary_path": "/tmp/input.csv",
        },
    )
    await memory.record("DataAnalyzer", "execution.complete", {"duration_seconds": 0.1})
    await memory.flush()

    records = memory.read_records("DataAnalyzer")
    assert len(records) == 3
    assert records[0]["particle_fx"] == "fx.flow.start"
    assert records[1]["particle_fx"] == "fx.logic.analyze"
    assert records[2]["particle_fx"] == "fx.flow.end"
    assert records[1]["upstream_path"] == "/tmp/input.csv"
    assert records[1]["upstream"]["function"] == "execute"
    assert records[1]["upstream"]["inputs"]["file_path"] == "/tmp/input.csv"
    assert records[1]["upstream_paths"] == ["/tmp/input.csv"]


@pytest.mark.asyncio
async def test_data_analyzer_syncs_background_memory(tmp_path, sample_csv_file, monkeypatch):
    """DataAnalyzer 執行時會同步保存背景記憶"""
    particle_dict_path = tmp_path / "particle_dict.json"
    _write_particle_dict(particle_dict_path)

    monkeypatch.setattr(config, "runtime_memory_dir", str(tmp_path / "runtime_memory"))
    monkeypatch.setattr(config, "particle_dict_path", str(particle_dict_path))

    analyzer = MrliouwordDataAnalyzer()
    messages = []

    async for message in analyzer.analyze_file(sample_csv_file):
        messages.append(message)

    assert any("開始分析" in message for message in messages)

    records = analyzer.runtime_memory.read_records("DataAnalyzer")
    event_types = [record["event_type"] for record in records]
    assert "execution.start" in event_types
    assert "execution.message" in event_types
    assert "execution.complete" in event_types
    assert all(record["upstream_path"] == sample_csv_file for record in records)
    assert records[0]["upstream"]["inputs"]["file_path"] == sample_csv_file
