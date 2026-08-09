"""MRL WORLD / UNIVERSAL CONTAINER 的可執行 GitHub 投影。

這個模組不是 MrliouAI 母體本身，也不列舉有限世界清單。它保存母體建立
粒子空間時最低限度的可驗證行為：建立、進化、組合、多視角呈現、快照與恢復。
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from typing import Any, Dict, Mapping, Optional, Sequence, Tuple
from uuid import uuid4


ORIGIN_SIGNATURE = "MrLiou"
UNIVERSAL_CONTAINER_SPEC = "MrliouAI.UniversalContainer.v1"


class UniversalContainerError(Exception):
    """Universal Container 基礎錯誤。"""


class SpaceNotFoundError(UniversalContainerError):
    """找不到指定粒子空間。"""


class SnapshotIntegrityError(UniversalContainerError):
    """快照內容與完整性雜湊不一致。"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _digest(value: Any) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError("{} 不可為空".format(field_name))
    return normalized


def _merge_state(base: Mapping[str, Any], delta: Mapping[str, Any]) -> Dict[str, Any]:
    """以非破壞方式套用狀態差異，巢狀 mapping 會遞迴合併。"""

    result: Dict[str, Any] = deepcopy(dict(base))
    for key, value in delta.items():
        current = result.get(key)
        if isinstance(current, Mapping) and isinstance(value, Mapping):
            result[key] = _merge_state(current, value)
        else:
            result[key] = deepcopy(value)
    return result


@dataclass(frozen=True)
class MotherEvent:
    """母體投影中的 append-only 生命週期事件。"""

    event_id: str
    event_type: str
    space_ids: Tuple[str, ...]
    created_at: str
    reason: str
    before_hash: Optional[str] = None
    after_hash: Optional[str] = None
    details: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ParticleSpace:
    """由注意力或意圖建立、持續演化的粒子容器。"""

    space_id: str
    intention: str
    attention: Optional[str]
    created_at: str
    updated_at: str
    status: str = "running"
    revision: int = 0
    state: Dict[str, Any] = field(default_factory=dict)
    perspectives: Dict[str, list] = field(default_factory=dict)
    parent_space_ids: Tuple[str, ...] = field(default_factory=tuple)
    origin_signature: str = ORIGIN_SIGNATURE
    spec: str = UNIVERSAL_CONTAINER_SPEC

    def to_dict(self) -> Dict[str, Any]:
        return deepcopy(asdict(self))

    def digest(self) -> str:
        return _digest(self.to_dict())


@dataclass(frozen=True)
class SpaceSnapshot:
    """可驗證並可回返的完整粒子空間快照。"""

    space_id: str
    revision: int
    captured_at: str
    payload: Mapping[str, Any]
    checksum: str
    origin_signature: str = ORIGIN_SIGNATURE
    spec: str = UNIVERSAL_CONTAINER_SPEC

    def verify(self) -> bool:
        return self.checksum == _digest(self.payload)


class MRLUniversalContainer:
    """動態世界生成與可逆狀態鏈的最小可執行投影。"""

    def __init__(self) -> None:
        self._spaces: Dict[str, ParticleSpace] = {}
        self._events: list = []

    def _space(self, space_id: str) -> ParticleSpace:
        try:
            return self._spaces[space_id]
        except KeyError as exc:
            raise SpaceNotFoundError(space_id) from exc

    def _new_id(self, prefix: str = "space") -> str:
        return "{}-{}".format(prefix, uuid4().hex)

    def _record(
        self,
        event_type: str,
        space_ids: Sequence[str],
        reason: str,
        before_hash: Optional[str] = None,
        after_hash: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
    ) -> MotherEvent:
        event = MotherEvent(
            event_id="event-{}".format(uuid4().hex),
            event_type=event_type,
            space_ids=tuple(space_ids),
            created_at=_now(),
            reason=reason,
            before_hash=before_hash,
            after_hash=after_hash,
            details=deepcopy(dict(details or {})),
        )
        self._events.append(event)
        return event

    def create_space(
        self,
        intention: str,
        attention: Optional[str] = None,
        initial_state: Optional[Mapping[str, Any]] = None,
        space_id: Optional[str] = None,
    ) -> ParticleSpace:
        """直接由意圖／注意力建立一個運行中的粒子空間。"""

        intention = _require_text(intention, "intention")
        if attention is not None:
            attention = _require_text(attention, "attention")
        target_id = space_id or self._new_id()
        if target_id in self._spaces:
            raise ValueError("space_id 已存在：{}".format(target_id))

        timestamp = _now()
        space = ParticleSpace(
            space_id=target_id,
            intention=intention,
            attention=attention,
            created_at=timestamp,
            updated_at=timestamp,
            state=deepcopy(dict(initial_state or {})),
        )
        self._spaces[target_id] = space
        self._record(
            "create_space",
            (target_id,),
            "attention_or_intention_created_space",
            after_hash=space.digest(),
        )
        return deepcopy(space)

    def get_space(self, space_id: str) -> ParticleSpace:
        return deepcopy(self._space(space_id))

    def active_spaces(self) -> Tuple[ParticleSpace, ...]:
        """回傳此運行實例當下的空間；這不是有限世界總表。"""

        return tuple(
            deepcopy(space)
            for space in self._spaces.values()
            if space.status == "running"
        )

    def evolve(
        self,
        space_id: str,
        delta: Mapping[str, Any],
        reason: str,
    ) -> ParticleSpace:
        """保留前態雜湊與差異後，讓指定空間進化一個 revision。"""

        reason = _require_text(reason, "reason")
        space = self._space(space_id)
        before_hash = space.digest()
        before_state = deepcopy(space.state)
        space.state = _merge_state(space.state, delta)
        space.revision += 1
        space.updated_at = _now()
        after_hash = space.digest()
        self._record(
            "evolve",
            (space_id,),
            reason,
            before_hash=before_hash,
            after_hash=after_hash,
            details={"delta": deepcopy(dict(delta)), "before_state": before_state},
        )
        return deepcopy(space)

    def combine(
        self,
        source_space_ids: Sequence[str],
        intention: str,
        attention: Optional[str] = None,
        space_id: Optional[str] = None,
    ) -> ParticleSpace:
        """組合多個世界而不壓平或覆寫各自狀態。"""

        source_ids = tuple(source_space_ids)
        if len(source_ids) < 2:
            raise ValueError("combine 至少需要兩個來源空間")
        sources = [self._space(item) for item in source_ids]
        preserved = {item.space_id: item.to_dict() for item in sources}
        combined = self.create_space(
            intention=intention,
            attention=attention,
            initial_state={
                "composition": {
                    "mode": "preserve_each_perspective",
                    "source_spaces": preserved,
                }
            },
            space_id=space_id,
        )
        stored = self._space(combined.space_id)
        stored.parent_space_ids = source_ids
        stored.updated_at = _now()
        self._record(
            "combine",
            source_ids + (stored.space_id,),
            "preserve_sources_then_compose",
            after_hash=stored.digest(),
            details={"source_hashes": {item.space_id: item.digest() for item in sources}},
        )
        return deepcopy(stored)

    def project(
        self,
        space_id: str,
        viewpoint: str,
        observation: Mapping[str, Any],
    ) -> ParticleSpace:
        """加入一筆視角呈現；相同視角的歷史不會被覆寫。"""

        viewpoint = _require_text(viewpoint, "viewpoint")
        space = self._space(space_id)
        before_hash = space.digest()
        entry = {
            "captured_at": _now(),
            "space_revision": space.revision,
            "observation": deepcopy(dict(observation)),
        }
        space.perspectives.setdefault(viewpoint, []).append(entry)
        space.revision += 1
        space.updated_at = _now()
        self._record(
            "project",
            (space_id,),
            "preserve_viewpoint_without_redefining_mother",
            before_hash=before_hash,
            after_hash=space.digest(),
            details={"viewpoint": viewpoint},
        )
        return deepcopy(space)

    def snapshot(self, space_id: str) -> SpaceSnapshot:
        space = self._space(space_id)
        payload = space.to_dict()
        snapshot = SpaceSnapshot(
            space_id=space.space_id,
            revision=space.revision,
            captured_at=_now(),
            payload=payload,
            checksum=_digest(payload),
        )
        self._record(
            "snapshot",
            (space_id,),
            "preserve_reversible_state",
            before_hash=space.digest(),
            after_hash=snapshot.checksum,
        )
        return snapshot

    def restore(
        self,
        snapshot: SpaceSnapshot,
        new_space_id: Optional[str] = None,
    ) -> ParticleSpace:
        """驗證快照後建立回返分支，不覆寫目前時間線。"""

        if not snapshot.verify():
            raise SnapshotIntegrityError(snapshot.space_id)
        payload = deepcopy(dict(snapshot.payload))
        target_id = new_space_id or self._new_id("restore")
        if target_id in self._spaces:
            raise ValueError("space_id 已存在：{}".format(target_id))

        restored = ParticleSpace(
            space_id=target_id,
            intention=payload["intention"],
            attention=payload.get("attention"),
            created_at=_now(),
            updated_at=_now(),
            status="running",
            revision=0,
            state=deepcopy(payload.get("state", {})),
            perspectives=deepcopy(payload.get("perspectives", {})),
            parent_space_ids=(snapshot.space_id,),
            origin_signature=payload.get("origin_signature", ORIGIN_SIGNATURE),
            spec=payload.get("spec", UNIVERSAL_CONTAINER_SPEC),
        )
        self._spaces[target_id] = restored
        self._record(
            "restore",
            (snapshot.space_id, target_id),
            "how_it_went_is_how_it_returns",
            before_hash=snapshot.checksum,
            after_hash=restored.digest(),
            details={"snapshot_revision": snapshot.revision},
        )
        return deepcopy(restored)

    def event_ledger(self) -> Tuple[MotherEvent, ...]:
        return tuple(deepcopy(self._events))

