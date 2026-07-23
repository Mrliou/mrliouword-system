"""MRL System A Particle Layer.

module: MRL_SystemA_ParticleLayer
version: 0.1.0-draft
origin_signature: MrLiouWord
status: schema-pending

Laws:
- LAW-0: origin_signature immutability
- LAW-1: PostgreSQL on DL580 is canonical persistence
- LAW-2: NO_DELETE / ADDITIVE / REVERSIBLE

This implementation is schema-safe: each source row is preserved verbatim in
UnifiedParticle.state. Explicit field mappings can be added after the three
PostgreSQL schemas are confirmed without changing the round-trip contract.
"""

from __future__ import annotations

from abc import ABC
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Mapping, Optional, Type

from unified_particle import ORIGIN_SIGNATURE, UnifiedParticle


class ParticleLayerError(RuntimeError):
    """Base exception for particle-layer contract failures."""


class OriginSignatureError(ParticleLayerError):
    """Raised when LAW-0 is violated."""


class RoundtripViolation(ParticleLayerError):
    """Raised when LAW-2 reversible conversion fails."""


class SystemAAdapter(ABC):
    """Common reversible particle representation for one System A table."""

    table_name: str
    domain: str
    origin_signature: str = ORIGIN_SIGNATURE
    id_candidates = ("seed_id", "id", "uuid", "key")
    persona_id_candidates = ("persona_id", "owner_persona_id")
    tags_candidates = ("tags",)

    def to_unified(self, row: Mapping[str, Any]) -> UnifiedParticle:
        source_row = deepcopy(dict(row))
        self._validate_row_origin(source_row)

        seed_id = self._first_value(source_row, self.id_candidates)
        if seed_id is None:
            raise ParticleLayerError(
                f"{self.table_name}: no identifier found in {self.id_candidates}"
            )

        persona_id = self._first_value(source_row, self.persona_id_candidates)
        tags = self._normalize_tags(
            self._first_value(source_row, self.tags_candidates)
        )
        proof = self._extract_proof(source_row)

        path_value = source_row.get("fltnz_path") or source_row.get("path")
        return UnifiedParticle(
            source=self.table_name,
            seed_id=str(seed_id),
            persona_id=None if persona_id is None else str(persona_id),
            domain=self.domain,
            fltnz_path=self._optional_string(path_value),
            state=source_row,
            proof=proof,
            tags=tags,
            origin_signature=ORIGIN_SIGNATURE,
        )

    def from_unified(self, particle: UnifiedParticle) -> Dict[str, Any]:
        if particle.origin_signature != ORIGIN_SIGNATURE:
            raise OriginSignatureError("LAW-0 violation")
        if particle.source != self.table_name:
            raise ParticleLayerError(
                f"source mismatch: expected {self.table_name}, "
                f"got {particle.source}"
            )
        return deepcopy(dict(particle.state))

    def roundtrip_check(self, row: Mapping[str, Any]) -> bool:
        return dict(row) == self.from_unified(self.to_unified(row))

    def assert_roundtrip(self, row: Mapping[str, Any]) -> None:
        if not self.roundtrip_check(row):
            raise RoundtripViolation(f"LAW-2 violation in {self.table_name}")

    def _validate_row_origin(self, row: Mapping[str, Any]) -> None:
        value = row.get("origin_signature")
        if value is not None and value != ORIGIN_SIGNATURE:
            raise OriginSignatureError(
                f"{self.table_name}: origin_signature must be {ORIGIN_SIGNATURE}"
            )

    @staticmethod
    def _first_value(row: Mapping[str, Any], candidates: Iterable[str]) -> Any:
        for key in candidates:
            value = row.get(key)
            if value is not None and value != "":
                return value
        return None

    @staticmethod
    def _normalize_tags(value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, tuple):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return [str(value)]

    @staticmethod
    def _extract_proof(row: Mapping[str, Any]) -> Dict[str, Any]:
        proof: Dict[str, Any] = {}
        for key in ("hash", "sha256", "checksum", "signature"):
            if row.get(key) is not None:
                proof[key] = row[key]
        return proof

    @staticmethod
    def _optional_string(value: Any) -> Optional[str]:
        return None if value is None else str(value)


class PersonaAdapter(SystemAAdapter):
    table_name = "mrl_persona"
    domain = "persona"


class MemoryAdapter(SystemAAdapter):
    table_name = "mrl_memory"
    domain = "memory"


class FileIndexAdapter(SystemAAdapter):
    table_name = "mrl_file_index"
    domain = "file_index"


ADAPTERS: Dict[str, Type[SystemAAdapter]] = {
    cls.table_name: cls
    for cls in (PersonaAdapter, MemoryAdapter, FileIndexAdapter)
}


def get_adapter(table_name: str) -> SystemAAdapter:
    try:
        return ADAPTERS[table_name]()
    except KeyError as exc:
        raise ParticleLayerError(
            f"unsupported System A table: {table_name}"
        ) from exc


def verify_law2(
    adapter: SystemAAdapter,
    rows: Iterable[Mapping[str, Any]],
    sample_n: int = 100,
) -> Dict[str, Any]:
    """Verify up to sample_n rows and return a deployment-friendly report."""
    checked = 0
    failures: List[Any] = []
    for row in rows:
        if checked >= sample_n:
            break
        checked += 1
        if not adapter.roundtrip_check(row):
            failures.append(row.get("id", row.get("seed_id", f"row-{checked}")))

    if failures:
        raise RoundtripViolation(
            f"LAW-2 violation on {len(failures)} rows: {failures[:5]}"
        )

    return {
        "table": adapter.table_name,
        "checked": checked,
        "failures": 0,
        "law": "LAW-2",
        "status": "PASS",
        "origin_signature": ORIGIN_SIGNATURE,
    }
