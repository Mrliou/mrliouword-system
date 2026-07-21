"""
背景運行記憶與保存系統
"""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

from .config import config


class ParticleRuntimeMemory:
    """背景同步 Agent 運行記憶，並關聯粒子字典。"""

    DEFAULT_EVENT_PARTICLES = {
        "execution.start": "fx.flow.start",
        "execution.complete": "fx.flow.end",
        "execution.error": "fx.trace.anchor",
    }

    AGENT_PARTICLES = {
        "DataAnalyzer": "fx.logic.analyze",
        "CodeReviewer": "fx.code.validate",
        "DocWriter": "fx.code.generate",
        "TestGenerator": "fx.code.validate",
        "WorkflowOptimizer": "fx.flow.collapse",
    }

    def __init__(
        self,
        storage_dir: Optional[str] = None,
        particle_dict_path: Optional[str] = None,
    ):
        self.storage_dir = Path(storage_dir or config.runtime_memory_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.particle_dict_path = Path(
            particle_dict_path or config.particle_dict_path or self._default_particle_dict()
        )
        self._particle_dict = self._load_particle_dict()
        self._queue: asyncio.Queue[Optional[Dict[str, Any]]] = asyncio.Queue()
        self._worker_task: Optional[asyncio.Task] = None
        self._worker_loop: Optional[asyncio.AbstractEventLoop] = None

    def _default_particle_dict(self) -> Path:
        return Path(__file__).resolve().parents[2] / "core" / "particle_dict.json"

    def _load_particle_dict(self) -> Dict[str, Any]:
        if not self.particle_dict_path.exists():
            return {"particles": {}}
        with open(self.particle_dict_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _agent_filename(self, agent_name: str) -> Path:
        slug = "".join(char.lower() if char.isalnum() else "_" for char in agent_name)
        return self.storage_dir / f"{slug}.jsonl"

    def resolve_particle_fx(self, agent_name: str, event_type: str) -> Optional[str]:
        if event_type == "execution.message":
            particle_fx = self.AGENT_PARTICLES.get(agent_name)
            if particle_fx in self._particle_dict.get("particles", {}):
                return particle_fx

        particle_fx = self.DEFAULT_EVENT_PARTICLES.get(event_type)
        if particle_fx in self._particle_dict.get("particles", {}):
            return particle_fx
        return None

    def build_record(
        self,
        agent_name: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        upstream: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        particle_fx = self.resolve_particle_fx(agent_name, event_type)
        particle = self._particle_dict.get("particles", {}).get(particle_fx, {})
        upstream_trace = self._build_upstream_trace(
            agent_name,
            event_type,
            payload=payload,
            session_id=session_id,
            upstream=upstream,
        )
        return {
            "id": str(uuid4()),
            "timestamp": datetime.now().isoformat(),
            "agent_name": agent_name,
            "session_id": session_id,
            "event_type": event_type,
            "particle_fx": particle_fx,
            "particle": particle,
            "payload": self._json_safe(payload or {}),
            "upstream_path": upstream_trace.get("primary_path"),
            "upstream_paths": upstream_trace.get("paths", []),
            "upstream": self._json_safe(upstream_trace),
        }

    def _json_safe(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {str(key): self._json_safe(item) for key, item in value.items()}
        if isinstance(value, (list, tuple, set)):
            return [self._json_safe(item) for item in value]
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        return repr(value)

    def _build_upstream_trace(
        self,
        agent_name: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        upstream: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        provided = dict(upstream or {})
        payload_paths = self._collect_paths(payload)
        upstream_paths = []
        for path in provided.get("paths", []):
            if isinstance(path, str) and path not in upstream_paths:
                upstream_paths.append(path)
        for path in payload_paths:
            if path not in upstream_paths:
                upstream_paths.append(path)

        primary_path = provided.get("primary_path")
        if not primary_path and upstream_paths:
            primary_path = upstream_paths[0]

        return {
            "agent_name": agent_name,
            "event_type": event_type,
            "session_id": session_id,
            "function": provided.get("function"),
            "inputs": provided.get("inputs", {}),
            "paths": upstream_paths,
            "primary_path": primary_path,
        }

    def _collect_paths(self, value: Any) -> List[str]:
        paths: List[str] = []
        self._collect_paths_into(value, paths)
        return paths

    def _collect_paths_into(self, value: Any, paths: List[str]) -> None:
        if isinstance(value, dict):
            for item in value.values():
                self._collect_paths_into(item, paths)
            return
        if isinstance(value, (list, tuple, set)):
            for item in value:
                self._collect_paths_into(item, paths)
            return
        if isinstance(value, str):
            for token in value.replace("\n", " ").split():
                normalized = token.strip(" ,;:'\"()[]{}<>")
                if (
                    normalized
                    and any(marker in normalized for marker in ("/", "\\", "./", "../"))
                    and normalized not in paths
                ):
                    paths.append(normalized)

    async def _ensure_worker(self):
        loop = asyncio.get_running_loop()
        if (
            self._worker_task is None
            or self._worker_task.done()
            or self._worker_loop is not loop
        ):
            self._worker_loop = loop
            self._worker_task = asyncio.create_task(self._worker(), name="runtime-memory")

    async def _worker(self):
        while True:
            record = await self._queue.get()
            try:
                if record is None:
                    return
                output_file = self._agent_filename(record["agent_name"])
                with open(output_file, "a", encoding="utf-8") as file:
                    file.write(json.dumps(record, ensure_ascii=False) + "\n")
            finally:
                self._queue.task_done()

    async def record(
        self,
        agent_name: str,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        upstream: Optional[Dict[str, Any]] = None,
    ):
        await self._ensure_worker()
        self._queue.put_nowait(
            self.build_record(
                agent_name,
                event_type,
                payload=payload,
                session_id=session_id,
                upstream=upstream,
            )
        )

    async def flush(self):
        if self._worker_task is None:
            return
        await self._queue.join()

    def read_records(self, agent_name: str) -> List[Dict[str, Any]]:
        output_file = self._agent_filename(agent_name)
        if not output_file.exists():
            return []

        records: List[Dict[str, Any]] = []
        with open(output_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
        return records
