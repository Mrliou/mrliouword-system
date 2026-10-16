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

try:  # 套件內匯入：讓母體可以 import modules.MRL_SystemA_ParticleLayer
    from .unified_particle import ORIGIN_SIGNATURE, UnifiedParticle
    from .Mrliou_MRL_Law2_Report_v1 import (
        ENV_UNSPECIFIED,
        Mrliou_MRL_build_law2_report,
    )
    from .Mrliou_MRL_Provenance_v1 import (
        FOREIGN_MARKED,
        Mrliou_MRL_classify_source,
    )
except ImportError:  # 相容既有用法：cd 進本目錄後直接 import
    from unified_particle import (  # type: ignore[no-redef]
        ORIGIN_SIGNATURE,
        UnifiedParticle,
    )
    from Mrliou_MRL_Law2_Report_v1 import (  # type: ignore[no-redef]
        ENV_UNSPECIFIED,
        Mrliou_MRL_build_law2_report,
    )
    from Mrliou_MRL_Provenance_v1 import (  # type: ignore[no-redef]
        FOREIGN_MARKED,
        Mrliou_MRL_classify_source,
    )


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
            # 粒子簽名恆為 MrLiouWord（LAW-0），但來源的出身另記，不抹掉。
            source_provenance=Mrliou_MRL_classify_source(source_row),
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
        """標了他方簽名就拒絕；完全未簽名則放行但由 source_provenance 記錄。

        行為與原版一致（LAW-2 不覆蓋），差別只在改用 Mrliou_MRL_Provenance_v1
        判定，因此母體鍵名 `origin` 也會被認出來，不再只看 `origin_signature`。
        未簽名的列不在這裡擋下——擋了會讓既有資料無法轉換；它的出身改由
        UnifiedParticle.source_provenance 標成 unsigned_pending，並在
        Mrliou_MRL_Law2_Report 裡逐筆定位，不會被洗成 MRL 權威。
        """
        if Mrliou_MRL_classify_source(row) == FOREIGN_MARKED:
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
    # 母體 core/particle_dict.json 的 domains 只有九個：memory / logic / code /
    # language / signal / trace / persona / flow / meta——沒有 file_index，那是
    # 外部造的詞。檔案索引的語意正是 fx.trace.anchor（錨定／創建檢查點）與
    # fx.trace.merkle（Merkle 驗證），與本層 _extract_proof 收
    # hash/sha256/checksum/signature 完全同一件事，因此對到 trace。
    # 舊值不刪除，保留在 legacy_domain 可回溯（LAW-2）。
    domain = "trace"
    legacy_domain = "file_index"


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
    """Verify up to sample_n rows and return a deployment-friendly report.

    合約不變（LAW-2 不覆蓋）：回傳鍵名、成功時的值、以及失敗時丟出的例外型別
    與訊息格式都與原版相同，既有呼叫端與測試不需改動。

    內部改由 Mrliou_MRL_build_law2_report 執行，因此失敗時能拿到完整定位而不是
    只有前五筆。要一份「不會說謊」的報告——明寫抽樣範圍、能表達失敗、帶環境與
    來源權威三態——請直接呼叫 Mrliou_MRL_build_law2_report，這個包裝函式為了
    維持舊合約，仍然會在有違規時丟例外而不產出報告。

    兩個旗標都是為了逐字保住原本的行為：
    - count_total=False：原版在 checked >= sample_n 時 break。若讓它為了算出
      total_rows 把剩下的列走完，預設 sample_n=100 就不再是上界——資料庫
      cursor 會被整表掃描，無界的產生器更是永不返回。
    - catch_errors=False：原版讓 roundtrip_check 的例外原樣往外傳。若收進報告
      再統一改丟 RoundtripViolation，呼叫端就分不出「輸入畸形」
      （ParticleLayerError，例如找不到識別碼）與「真的往返不一致」，
      診斷訊息也會丟失。
    """
    report = Mrliou_MRL_build_law2_report(
        adapter,
        rows,
        environment=ENV_UNSPECIFIED,
        sample_n=sample_n,
        count_total=False,
        catch_errors=False,
    )

    if report["failures"]:
        located = [failure["located"] for failure in report["failures"]]
        raise RoundtripViolation(
            f"LAW-2 violation on {len(located)} rows: {located[:5]}"
        )

    return {
        "table": adapter.table_name,
        "checked": report["checked"],
        "failures": 0,
        "law": "LAW-2",
        "status": "PASS",
        "origin_signature": ORIGIN_SIGNATURE,
    }
