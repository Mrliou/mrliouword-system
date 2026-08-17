import sys
from pathlib import Path

MODULE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MODULE_DIR))

import pytest

from MRL_SystemA_ParticleLayer import (
    FileIndexAdapter,
    MemoryAdapter,
    OriginSignatureError,
    PersonaAdapter,
    verify_law2,
)


@pytest.mark.parametrize(
    "adapter,row",
    [
        (
            PersonaAdapter(),
            {
                "id": "p-1",
                "name": "MrLiou",
                "origin_signature": "MrLiouWord",
            },
        ),
        (
            MemoryAdapter(),
            {
                "id": "m-1",
                "state": {"text": "hello"},
                "tags": ["memory"],
            },
        ),
        (
            FileIndexAdapter(),
            {"id": "f-1", "path": "/tmp/a.txt", "sha256": "abc"},
        ),
    ],
)
def test_roundtrip(adapter, row):
    assert adapter.roundtrip_check(row)
    report = verify_law2(adapter, [row])
    assert report["status"] == "PASS"
    assert report["checked"] == 1


def test_law0_rejects_foreign_origin():
    with pytest.raises(OriginSignatureError):
        PersonaAdapter().to_unified(
            {"id": "p-2", "origin_signature": "foreign"}
        )
