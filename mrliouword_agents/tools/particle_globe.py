"""
Particle globe module for spatial particle memory.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from html import escape
import json
from math import asin, cos, radians, sin, sqrt
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Union
from uuid import uuid4


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


@dataclass
class GeoPoint:
    """Single geographic point."""

    latitude: float
    longitude: float
    altitude: float = 0.0
    timestamp: str = field(default_factory=_utc_now)
    meta: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LifecycleEvent:
    """Particle lifecycle event."""

    stage: str
    timestamp: str = field(default_factory=_utc_now)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParticleBinding:
    """Internal representation for a particle on the globe."""

    bind_id: str
    particle_id: str
    origin_signature: str
    geometry_type: str
    latitude: float
    longitude: float
    altitude: float
    data: Dict[str, Any] = field(default_factory=dict)
    trajectory: List[GeoPoint] = field(default_factory=list)
    structure: Dict[str, Any] = field(default_factory=dict)
    lifecycle: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["trajectory"] = [point.to_dict() for point in self.trajectory]
        return payload


PointInput = Union[GeoPoint, Dict[str, Any], Sequence[float]]


class ParticleGlobe:
    """粒子記憶地球儀。"""

    def __init__(self, origin_signature: str = "MrLiouWord"):
        self.origin_signature = origin_signature
        self._bindings: Dict[str, ParticleBinding] = {}
        self._particle_index: Dict[str, List[str]] = {}

    @staticmethod
    def _validate_coordinate(latitude: float, longitude: float, altitude: float) -> None:
        if latitude is None or longitude is None:
            raise ValueError("latitude and longitude are required")
        if not -90 <= latitude <= 90:
            raise ValueError("latitude must be between -90 and 90")
        if not -180 <= longitude <= 180:
            raise ValueError("longitude must be between -180 and 180")
        if not isinstance(altitude, (int, float)):
            raise ValueError("altitude must be numeric")

    @classmethod
    def _normalize_point(
        cls,
        point: PointInput,
        default_meta: Optional[Dict[str, Any]] = None,
    ) -> GeoPoint:
        if isinstance(point, GeoPoint):
            cls._validate_coordinate(point.latitude, point.longitude, point.altitude)
            if default_meta:
                merged_meta = dict(default_meta)
                merged_meta.update(point.meta)
                point.meta = merged_meta
            return point

        if isinstance(point, dict):
            latitude = point.get("latitude", point.get("lat"))
            longitude = point.get("longitude", point.get("lng", point.get("lon")))
            altitude = point.get("altitude", point.get("alt", 0.0))
            timestamp = point.get("timestamp") or _utc_now()
            meta = dict(default_meta or {})
            meta.update(point.get("meta", {}))
            cls._validate_coordinate(latitude, longitude, altitude)
            return GeoPoint(
                latitude=float(latitude),
                longitude=float(longitude),
                altitude=float(altitude),
                timestamp=str(timestamp),
                meta=meta,
            )

        if isinstance(point, Sequence) and len(point) >= 2:
            latitude = float(point[0])
            longitude = float(point[1])
            altitude = float(point[2]) if len(point) > 2 else 0.0
            cls._validate_coordinate(latitude, longitude, altitude)
            return GeoPoint(
                latitude=latitude,
                longitude=longitude,
                altitude=altitude,
                meta=dict(default_meta or {}),
            )

        raise ValueError("point must provide latitude and longitude")

    @classmethod
    def _normalize_points(
        cls,
        points: Optional[Iterable[PointInput]],
        default_meta: Optional[Dict[str, Any]] = None,
    ) -> List[GeoPoint]:
        return [cls._normalize_point(point, default_meta) for point in (points or [])]

    @staticmethod
    def _detect_geometry_type(structure: Dict[str, Any], trajectory: List[GeoPoint]) -> str:
        if structure.get("surfaces"):
            return "surface"
        if structure.get("lines") or len(trajectory) > 1 or len(structure.get("points", [])) > 1:
            return "line"
        return "point"

    def _latest_binding(self, particle_id: str) -> ParticleBinding:
        bind_ids = self._particle_index.get(particle_id, [])
        if not bind_ids:
            raise KeyError("particle_id not found")
        return self._bindings[bind_ids[-1]]

    def bind_particle(
        self,
        particle_id: str,
        latitude: float,
        longitude: float,
        altitude: float = 0,
        data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """將粒子綁定到地理座標。"""

        self._validate_coordinate(latitude, longitude, altitude)
        bind_id = uuid4().hex
        point = GeoPoint(
            latitude=float(latitude),
            longitude=float(longitude),
            altitude=float(altitude),
            meta={"event": "bind"},
        )
        lifecycle_event = LifecycleEvent(
            stage="bound",
            metrics={"trajectory_points": 1, "structure_points": 1},
        )
        binding = ParticleBinding(
            bind_id=bind_id,
            particle_id=particle_id,
            origin_signature=self.origin_signature,
            geometry_type="point",
            latitude=point.latitude,
            longitude=point.longitude,
            altitude=point.altitude,
            data=dict(data or {}),
            trajectory=[point],
            structure={
                "points": [point.to_dict()],
                "lines": [],
                "surfaces": [],
                "scale": 1.0,
                "zoom": 1.0,
            },
            lifecycle={
                "stage": lifecycle_event.stage,
                "created_at": lifecycle_event.timestamp,
                "updated_at": lifecycle_event.timestamp,
                "history": [lifecycle_event.to_dict()],
            },
        )
        self._bindings[bind_id] = binding
        self._particle_index.setdefault(particle_id, []).append(bind_id)
        return bind_id

    def get_binding(self, particle_id: str) -> Optional[Dict[str, Any]]:
        """取得粒子最新綁定。"""

        try:
            return self._latest_binding(particle_id).to_dict()
        except KeyError:
            return None

    def list_bindings(self) -> List[Dict[str, Any]]:
        """列出所有綁定。"""

        return [binding.to_dict() for binding in self._bindings.values()]

    def record_trajectory(
        self,
        particle_id: str,
        latitude: float,
        longitude: float,
        altitude: float = 0,
        timestamp: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """追加粒子軌跡點。"""

        binding = self._latest_binding(particle_id)
        point = self._normalize_point(
            {
                "latitude": latitude,
                "longitude": longitude,
                "altitude": altitude,
                "timestamp": timestamp or _utc_now(),
                "meta": meta or {},
            },
            {"event": "trajectory"},
        )
        binding.trajectory.append(point)
        binding.latitude = point.latitude
        binding.longitude = point.longitude
        binding.altitude = point.altitude
        binding.structure.setdefault("points", []).append(point.to_dict())
        binding.geometry_type = self._detect_geometry_type(binding.structure, binding.trajectory)
        binding.lifecycle["updated_at"] = point.timestamp
        return point.to_dict()

    def update_particle_structure(
        self,
        particle_id: str,
        points: Optional[Iterable[PointInput]] = None,
        lines: Optional[Iterable[Iterable[PointInput]]] = None,
        surfaces: Optional[Iterable[Iterable[PointInput]]] = None,
        scale: Optional[float] = None,
        zoom: Optional[float] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """更新點、線、面結構。"""

        binding = self._latest_binding(particle_id)
        structure = binding.structure

        if points is not None:
            normalized_points = self._normalize_points(points, {"type": "point"})
            structure["points"] = [point.to_dict() for point in normalized_points]
            if normalized_points:
                head = normalized_points[0]
                binding.latitude = head.latitude
                binding.longitude = head.longitude
                binding.altitude = head.altitude

        if lines is not None:
            normalized_lines = [
                [point.to_dict() for point in self._normalize_points(line, {"type": "line"})]
                for line in lines
            ]
            structure["lines"] = normalized_lines

        if surfaces is not None:
            normalized_surfaces = [
                [point.to_dict() for point in self._normalize_points(surface, {"type": "surface"})]
                for surface in surfaces
            ]
            structure["surfaces"] = normalized_surfaces

        if scale is not None:
            if scale <= 0:
                raise ValueError("scale must be positive")
            structure["scale"] = float(scale)

        if zoom is not None:
            if zoom <= 0:
                raise ValueError("zoom must be positive")
            structure["zoom"] = float(zoom)

        if data:
            binding.data.update(data)

        binding.geometry_type = self._detect_geometry_type(structure, binding.trajectory)
        binding.lifecycle["updated_at"] = _utc_now()
        return binding.to_dict()

    def evolve_particle(
        self,
        particle_id: str,
        stage: str,
        metrics: Optional[Dict[str, Any]] = None,
        structure: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """記錄生命週期演化。"""

        binding = self._latest_binding(particle_id)
        if structure:
            self.update_particle_structure(
                particle_id=particle_id,
                points=structure.get("points"),
                lines=structure.get("lines"),
                surfaces=structure.get("surfaces"),
                scale=structure.get("scale"),
                zoom=structure.get("zoom"),
                data=structure.get("data"),
            )
            binding = self._latest_binding(particle_id)

        event = LifecycleEvent(stage=stage, metrics=dict(metrics or {}))
        history = binding.lifecycle.setdefault("history", [])
        history.append(event.to_dict())
        binding.lifecycle["stage"] = stage
        binding.lifecycle["updated_at"] = event.timestamp
        return binding.to_dict()

    def scale_particle(self, particle_id: str, factor: float) -> Dict[str, float]:
        """縮放粒子結構。"""

        if factor <= 0:
            raise ValueError("factor must be positive")
        binding = self._latest_binding(particle_id)
        next_scale = float(binding.structure.get("scale", 1.0)) * factor
        binding.structure["scale"] = next_scale
        binding.lifecycle["updated_at"] = _utc_now()
        return {"particle_id": particle_id, "scale": next_scale}

    def set_zoom(self, particle_id: str, zoom: float) -> Dict[str, float]:
        """設定粒子縮放倍率。"""

        if zoom <= 0:
            raise ValueError("zoom must be positive")
        binding = self._latest_binding(particle_id)
        binding.structure["zoom"] = float(zoom)
        binding.lifecycle["updated_at"] = _utc_now()
        return {"particle_id": particle_id, "zoom": float(zoom)}

    @staticmethod
    def _distance_km(
        latitude_a: float,
        longitude_a: float,
        latitude_b: float,
        longitude_b: float,
    ) -> float:
        radius = 6371.0
        lat_delta = radians(latitude_b - latitude_a)
        lon_delta = radians(longitude_b - longitude_a)
        start_lat = radians(latitude_a)
        end_lat = radians(latitude_b)
        haversine = sin(lat_delta / 2) ** 2 + cos(start_lat) * cos(end_lat) * sin(
            lon_delta / 2
        ) ** 2
        return 2 * radius * asin(sqrt(haversine))

    def get_particles_in_radius(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
    ) -> List[Dict[str, Any]]:
        """獲取指定範圍內的粒子。"""

        if radius_km < 0:
            raise ValueError("radius_km must be non-negative")

        results: List[Dict[str, Any]] = []
        for binding in self._bindings.values():
            distance = self._distance_km(
                latitude,
                longitude,
                binding.latitude,
                binding.longitude,
            )
            if distance <= radius_km:
                payload = binding.to_dict()
                payload["distance_km"] = round(distance, 4)
                results.append(payload)
        return sorted(results, key=lambda item: item["distance_km"])

    def _select_bindings(
        self,
        particles: Optional[Iterable[Union[str, Dict[str, Any]]]] = None,
    ) -> List[Dict[str, Any]]:
        if particles is None:
            return [binding.to_dict() for binding in self._bindings.values()]

        selected: List[Dict[str, Any]] = []
        for item in particles:
            if isinstance(item, str):
                if item in self._bindings:
                    selected.append(self._bindings[item].to_dict())
                    continue
                selected.append(self._latest_binding(item).to_dict())
                continue

            if isinstance(item, dict):
                if "trajectory" in item and "structure" in item:
                    selected.append(item)
                    continue
                point = self._normalize_point(item)
                selected.append(
                    {
                        "bind_id": item.get("bind_id", uuid4().hex),
                        "particle_id": item.get("particle_id", item.get("id", "external")),
                        "origin_signature": self.origin_signature,
                        "geometry_type": "point",
                        "latitude": point.latitude,
                        "longitude": point.longitude,
                        "altitude": point.altitude,
                        "data": dict(item.get("data", {})),
                        "trajectory": [point.to_dict()],
                        "structure": {
                            "points": [point.to_dict()],
                            "lines": [],
                            "surfaces": [],
                            "scale": 1.0,
                            "zoom": 1.0,
                        },
                        "lifecycle": {
                            "stage": item.get("stage", "external"),
                            "created_at": point.timestamp,
                            "updated_at": point.timestamp,
                            "history": [],
                        },
                    }
                )
                continue

            raise ValueError("particles must contain particle ids or dictionaries")
        return selected

    @staticmethod
    def _kml_coordinates(points: Iterable[Dict[str, Any]]) -> str:
        return " ".join(
            "{lon},{lat},{alt}".format(
                lon=point["longitude"],
                lat=point["latitude"],
                alt=point.get("altitude", 0.0),
            )
            for point in points
        )

    def export_kml(
        self,
        filename: str,
        particles: Optional[Iterable[Union[str, Dict[str, Any]]]] = None,
    ) -> str:
        """導出為 KML。"""

        records = self._select_bindings(particles)
        lines: List[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<kml xmlns="http://www.opengis.net/kml/2.2">',
            "<Document>",
            "  <name>MrLiouWord Particle Globe</name>",
            "  <description>粒子記憶地球儀</description>",
        ]

        for record in records:
            particle_id = escape(str(record["particle_id"]))
            description = escape(
                json.dumps(record.get("data", {}), ensure_ascii=False, sort_keys=True)
            )
            lines.extend(
                [
                    "  <Placemark>",
                    "    <name>{}</name>".format(particle_id),
                    "    <description>{}</description>".format(description),
                    "    <Point>",
                    "      <coordinates>{},{},{}</coordinates>".format(
                        record["longitude"],
                        record["latitude"],
                        record.get("altitude", 0.0),
                    ),
                    "    </Point>",
                    "  </Placemark>",
                ]
            )

            if len(record.get("trajectory", [])) > 1:
                lines.extend(
                    [
                        "  <Placemark>",
                        "    <name>{} trajectory</name>".format(particle_id),
                        "    <LineString>",
                        "      <coordinates>{}</coordinates>".format(
                            self._kml_coordinates(record["trajectory"])
                        ),
                        "    </LineString>",
                        "  </Placemark>",
                    ]
                )

            for index, segment in enumerate(record.get("structure", {}).get("lines", []), start=1):
                lines.extend(
                    [
                        "  <Placemark>",
                        "    <name>{} line {}</name>".format(particle_id, index),
                        "    <LineString>",
                        "      <coordinates>{}</coordinates>".format(
                            self._kml_coordinates(segment)
                        ),
                        "    </LineString>",
                        "  </Placemark>",
                    ]
                )

            for index, surface in enumerate(
                record.get("structure", {}).get("surfaces", []), start=1
            ):
                if len(surface) < 3:
                    continue
                ring = list(surface)
                if ring[0] != ring[-1]:
                    ring.append(surface[0])
                lines.extend(
                    [
                        "  <Placemark>",
                        "    <name>{} surface {}</name>".format(particle_id, index),
                        "    <Polygon><outerBoundaryIs><LinearRing>",
                        "      <coordinates>{}</coordinates>".format(
                            self._kml_coordinates(ring)
                        ),
                        "    </LinearRing></outerBoundaryIs></Polygon>",
                        "  </Placemark>",
                    ]
                )

        lines.extend(["</Document>", "</kml>"])
        path = Path(filename)
        path.write_text("\n".join(lines), encoding="utf-8")
        return str(path)

    def export_to_kml(
        self,
        particles: Optional[Iterable[Union[str, Dict[str, Any], str]]] = None,
        filename: Optional[str] = None,
    ) -> str:
        """兼容的 KML 導出別名。"""

        if isinstance(particles, str) and filename is None:
            return self.export_kml(particles)
        if filename is None:
            raise ValueError("filename is required when particles are provided")
        return self.export_kml(filename, particles)

    def generate_offline_globe(
        self,
        filename: str,
        particles: Optional[Iterable[Union[str, Dict[str, Any]]]] = None,
    ) -> str:
        """生成離線 HTML 地球儀。"""

        records = self._select_bindings(particles)
        payload = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
        html = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8" />
  <title>MrLiouWord Particle Globe</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 0; background: #08111f; color: #e6eef9; }
    .layout { display: grid; grid-template-columns: 2fr 1fr; min-height: 100vh; }
    canvas { width: 100%; height: 100%; background: radial-gradient(circle, #15375e 0%, #08111f 72%); }
    .panel { padding: 16px; overflow: auto; border-left: 1px solid rgba(255,255,255,0.1); }
    .controls { display: flex; gap: 8px; margin-bottom: 16px; }
    button { border: 0; border-radius: 6px; padding: 8px 12px; background: #2d7ff9; color: white; cursor: pointer; }
    code { display: block; white-space: pre-wrap; word-break: break-word; }
  </style>
</head>
<body>
  <div class="layout">
    <canvas id="globe" width="900" height="900"></canvas>
    <div class="panel">
      <h1>粒子記憶地球儀</h1>
      <div class="controls">
        <button type="button" id="zoomIn">放大</button>
        <button type="button" id="zoomOut">縮小</button>
      </div>
      <p id="summary"></p>
      <code id="details"></code>
    </div>
  </div>
  <script>
    const records = __PAYLOAD__;
    const canvas = document.getElementById('globe');
    const ctx = canvas.getContext('2d');
    const summary = document.getElementById('summary');
    const details = document.getElementById('details');
    let zoom = 1;

    function project(lat, lon, radius) {
      const phi = (90 - lat) * Math.PI / 180;
      const theta = (lon + 180) * Math.PI / 180;
      const x = radius * Math.sin(phi) * Math.cos(theta);
      const y = radius * Math.cos(phi);
      return { x, y };
    }

    function draw() {
      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = Math.min(centerX, centerY) * 0.72 * zoom;
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.beginPath();
      ctx.fillStyle = '#10253f';
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#63b3ff';
      ctx.stroke();

      records.forEach((record) => {
        const point = project(record.latitude, record.longitude, radius);
        ctx.beginPath();
        ctx.fillStyle = record.geometry_type === 'surface' ? '#ff6b6b' : (record.geometry_type === 'line' ? '#ffd166' : '#80ed99');
        ctx.arc(centerX + point.x, centerY - point.y, 5 * (record.structure.zoom || 1), 0, Math.PI * 2);
        ctx.fill();
      });

      summary.textContent = `粒子數: ${records.length} | 目前縮放: ${zoom.toFixed(2)}x`;
      details.textContent = JSON.stringify(records, null, 2);
    }

    document.getElementById('zoomIn').addEventListener('click', () => {
      zoom *= 1.2;
      draw();
    });

    document.getElementById('zoomOut').addEventListener('click', () => {
      zoom = Math.max(0.4, zoom / 1.2);
      draw();
    });

    draw();
  </script>
</body>
</html>
""".replace("__PAYLOAD__", payload)
        path = Path(filename)
        path.write_text(html, encoding="utf-8")
        return str(path)


__all__ = ["ParticleGlobe"]
