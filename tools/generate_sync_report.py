#!/usr/bin/env python3
"""Generate an evidence-based closure sync report."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from merkle_builder import discover_particle_files


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def generate_sync_report(source_repo: Path, target_repos: list, output_path: Optional[Path] = None) -> Dict[str, Any]:
    source = Path(source_repo).resolve()
    targets = [Path(path).resolve() for path in target_repos]
    verification = load_json(source / ".mrliou" / "verification_report.json")
    report: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": str(source),
        "targets": [str(path) for path in targets],
        "summary": {
            "total_particles": len(discover_particle_files(source)),
            "total_repositories": 1 + len(targets),
            "source_repository": source.name,
            "target_count": len(targets),
            "consistent": verification.get("consistent") if verification else None,
        },
    }
    evidence_files = {
        "consistency": "consistency.map.json",
        "merkle": "merkle.json",
        "sync_report": "sync_report.json",
        "verification_report": "verification_report.json",
    }
    for name, filename in evidence_files.items():
        data = load_json(source / ".mrliou" / filename)
        if data is not None:
            report[name] = data
    if output_path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate MRL closure sync report")
    parser.add_argument("--source", default=".")
    parser.add_argument("--targets")
    parser.add_argument("--output", "-o")
    args = parser.parse_args()
    targets = [Path(item.strip()) for item in args.targets.split(",") if item.strip()] if args.targets else []
    report = generate_sync_report(Path(args.source), targets, Path(args.output) if args.output else None)
    if not args.output:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
