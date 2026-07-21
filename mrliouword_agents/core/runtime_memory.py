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

    WAREHOUSE_CATEGORIES = {
        "vector": {
            "label": "向量",
            "description": "保存向量、嵌入與粒子權重向量資料",
        },
        "function": {
            "label": "函數",
            "description": "保存函數、執行入口與運行上下文",
        },
        "api": {
            "label": "API",
            "description": "保存 API 端點、方法與請求封裝",
        },
        "ai_weight_token": {
            "label": "AI 初始權重 Token",
            "description": "保存人工智能初始權重與 token 種子資料",
        },
    }

    WAREHOUSE_FIELD_ALIASES = {
        "vector": "vector",
        "vectors": "vector",
        "embedding": "vector",
        "embeddings": "vector",
        "function": "function",
        "functions": "function",
        "api": "api",
        "apis": "api",
        "endpoint": "api",
        "endpoints": "api",
        "ai_weight_token": "ai_weight_token",
        "ai_weight_tokens": "ai_weight_token",
        "weight_token": "ai_weight_token",
        "weight_tokens": "ai_weight_token",
        "initial_weight_token": "ai_weight_token",
        "initial_weight_tokens": "ai_weight_token",
    }

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
        self.warehouse_dir = self.storage_dir / "particle_warehouse"
        self._warehouse_registry_path = self.warehouse_dir / "registry.json"
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

    def _default_warehouse_registry(self) -> Dict[str, Any]:
        return {
            "version": "1.0.0",
            "origin": "MrLiouWord",
            "architecture": "mrliou創世公式邏輯架構",
            "warehouse": "particle_memory",
            "updated_at": datetime.now().isoformat(),
            "categories": {
                category: {
                    **metadata,
                    "records": 0,
                    "last_updated": None,
                }
                for category, metadata in self.WAREHOUSE_CATEGORIES.items()
            },
        }

    def _load_warehouse_registry(self) -> Dict[str, Any]:
        if not self._warehouse_registry_path.exists():
            return self._default_warehouse_registry()
        with open(self._warehouse_registry_path, "r", encoding="utf-8") as file:
            registry = json.load(file)

        categories = registry.setdefault("categories", {})
        for category, metadata in self.WAREHOUSE_CATEGORIES.items():
            category_state = categories.setdefault(category, {})
            category_state.setdefault("label", metadata["label"])
            category_state.setdefault("description", metadata["description"])
            category_state.setdefault("records", 0)
            category_state.setdefault("last_updated", None)
        registry.setdefault("version", "1.0.0")
        registry.setdefault("origin", "MrLiouWord")
        registry.setdefault("architecture", "mrliou創世公式邏輯架構")
        registry.setdefault("warehouse", "particle_memory")
        registry.setdefault("updated_at", datetime.now().isoformat())
        return registry

    def _save_warehouse_registry(self, registry: Dict[str, Any]) -> None:
        registry["updated_at"] = datetime.now().isoformat()
        with open(self._warehouse_registry_path, "w", encoding="utf-8") as file:
            json.dump(registry, file, ensure_ascii=False, indent=2)

    def _ensure_warehouse_registry(self) -> None:
        self.warehouse_dir.mkdir(parents=True, exist_ok=True)
        self._save_warehouse_registry(self._load_warehouse_registry())

    def _agent_filename(self, agent_name: str) -> Path:
        slug = "".join(char.lower() if char.isalnum() else "_" for char in agent_name)
        return self.storage_dir / f"{slug}.jsonl"

    def _warehouse_filename(self, category: str) -> Path:
        return self.warehouse_dir / f"{category}.jsonl"

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
        warehouse_entries = self._build_warehouse_entries(
            agent_name,
            event_type,
            particle_fx,
            payload=payload,
            session_id=session_id,
            upstream=upstream_trace,
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
            "warehouse_categories": sorted(
                {entry["category"] for entry in warehouse_entries}
            ),
            "warehouse_entries": warehouse_entries,
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

    def _extract_warehouse_groups(self, value: Optional[Dict[str, Any]]) -> Dict[str, List[Any]]:
        groups: Dict[str, List[Any]] = {}
        if not isinstance(value, dict):
            return groups

        warehouse_value = value.get("particle_warehouse") or value.get("warehouse")
        if isinstance(warehouse_value, dict):
            sources = [warehouse_value]
        else:
            sources = []
        sources.append(value)

        for source in sources:
            for field_name, category in self.WAREHOUSE_FIELD_ALIASES.items():
                if field_name not in source:
                    continue
                raw_items = source[field_name]
                if isinstance(raw_items, list):
                    items = raw_items
                else:
                    items = [raw_items]
                bucket = groups.setdefault(category, [])
                for item in items:
                    bucket.append(self._json_safe(item))
        return groups

    def _build_warehouse_entries(
        self,
        agent_name: str,
        event_type: str,
        particle_fx: Optional[str],
        payload: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
        upstream: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        grouped_entries: Dict[str, List[Any]] = {}
        for category, items in self._extract_warehouse_groups(payload).items():
            grouped_entries.setdefault(category, []).extend(items)
        if isinstance(upstream, dict):
            upstream_warehouse = upstream.get("particle_warehouse") or upstream.get("warehouse")
            if isinstance(upstream_warehouse, dict):
                for category, items in self._extract_warehouse_groups(
                    {"particle_warehouse": upstream_warehouse}
                ).items():
                    grouped_entries.setdefault(category, []).extend(items)

        if isinstance(upstream, dict) and upstream.get("function"):
            grouped_entries.setdefault("function", []).append(
                {
                    "name": upstream.get("function"),
                    "inputs": upstream.get("inputs", {}),
                    "primary_path": upstream.get("primary_path"),
                    "paths": upstream.get("paths", []),
                }
            )

        timestamp = datetime.now().isoformat()
        entries: List[Dict[str, Any]] = []
        for category, items in grouped_entries.items():
            for item in items:
                entries.append(
                    {
                        "id": str(uuid4()),
                        "timestamp": timestamp,
                        "category": category,
                        "agent_name": agent_name,
                        "session_id": session_id,
                        "event_type": event_type,
                        "particle_fx": particle_fx,
                        "record": self._json_safe(item),
                    }
                )
        return entries

    def _persist_warehouse_entries(self, entries: List[Dict[str, Any]]) -> None:
        if not entries:
            return

        registry = self._load_warehouse_registry()
        for entry in entries:
            category = entry["category"]
            category_state = registry["categories"].setdefault(
                category,
                {
                    "label": category,
                    "description": "自動註冊分類",
                    "records": 0,
                    "last_updated": None,
                },
            )
            with open(self._warehouse_filename(category), "a", encoding="utf-8") as file:
                file.write(json.dumps(entry, ensure_ascii=False) + "\n")
            category_state["records"] += 1
            category_state["last_updated"] = entry["timestamp"]

        self._save_warehouse_registry(registry)

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
                self._persist_warehouse_entries(record.get("warehouse_entries", []))
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

    def read_warehouse_records(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        categories = [category] if category else list(self.WAREHOUSE_CATEGORIES.keys())
        records: List[Dict[str, Any]] = []
        for current_category in categories:
            output_file = self._warehouse_filename(current_category)
            if not output_file.exists():
                continue
            with open(output_file, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if line:
                        records.append(json.loads(line))
        return records
