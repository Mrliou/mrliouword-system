#!/usr/bin/env python3
"""Fail-closed, source-authoritative MRL closure sync manager."""

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from merkle_builder import ParticleMerkleTree, discover_particle_files


def file_digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


class ClosureSyncManager:
    """Synchronize only from the declared source into declared targets."""

    def __init__(self, source_repo: Path, target_repos: Optional[List[Path]] = None):
        self.source = Path(source_repo).resolve()
        self.targets = [Path(path).resolve() for path in (target_repos or [])]
        if not self.source.is_dir():
            raise FileNotFoundError(f"Source repository not found: {self.source}")
        if self.source in self.targets:
            raise ValueError("Source repository cannot also be a target")
        if len(set(self.targets)) != len(self.targets):
            raise ValueError("Duplicate target repositories are not allowed")
        self.state: Dict[str, Any] = {
            "phase": "init",
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "source": str(self.source),
            "targets": [str(path) for path in self.targets],
            "authority": "source_only",
        }
        self._load_metadata()
        self._load_sync_config()

    def _load_metadata(self) -> None:
        metadata = self.source / ".mrliou" / "meta.json"
        if metadata.exists():
            with open(metadata, "r", encoding="utf-8") as handle:
                self.meta = json.load(handle)
        else:
            self.meta = {}

    def _load_sync_config(self) -> None:
        config_path = self.source / ".mrliou" / "sync.config.json"
        if not config_path.exists():
            self.sync_config = {
                "authority": {"mode": "source_only", "target_to_source": False},
                "auto_heal": False,
            }
            return
        with open(config_path, "r", encoding="utf-8") as handle:
            self.sync_config = json.load(handle)
        authority = self.sync_config.get("authority", {})
        if authority.get("mode") != "source_only":
            raise ValueError("sync.config.json must declare source_only authority")
        if authority.get("target_to_source") is not False:
            raise ValueError("target-to-source synchronization must remain disabled")
        if self.sync_config.get("auto_heal") is not False:
            raise ValueError("automatic healing must remain disabled by default")

    def _observe_repo(self, repo_path: Path) -> Dict[str, Any]:
        if not repo_path.is_dir():
            raise FileNotFoundError(f"Repository not found: {repo_path}")
        files = discover_particle_files(repo_path)
        file_map = {
            path.relative_to(repo_path).as_posix(): file_digest(path) for path in files
        }
        tree = ParticleMerkleTree()
        tree.build_from_particles(files, root=repo_path)
        return {
            "path": str(repo_path),
            "exists": True,
            "particles": sorted(file_map),
            "file_hashes": file_map,
            "particle_count": len(files),
            "merkle_root": tree.merkle_root,
        }

    def observe(self) -> Dict[str, Any]:
        self.state["phase"] = "observe"
        observations = {"source": self._observe_repo(self.source), "targets": {}}
        for target in self.targets:
            observations["targets"][str(target)] = self._observe_repo(target)
        self.observations = observations
        return observations

    def resolve(self) -> Dict[str, Any]:
        if not hasattr(self, "observations"):
            raise RuntimeError("Must run observe() before resolve()")
        self.state["phase"] = "resolve"
        source_hashes = self.observations["source"]["file_hashes"]
        resolution: Dict[str, Any] = {
            "authority": "source_only",
            "missing_in_targets": {},
            "changed_in_targets": {},
            "extra_in_targets": {},
            "action_plan": [],
        }
        for target_path, target_state in self.observations["targets"].items():
            target_hashes = target_state["file_hashes"]
            missing = sorted(set(source_hashes) - set(target_hashes))
            extra = sorted(set(target_hashes) - set(source_hashes))
            changed = sorted(
                path
                for path in set(source_hashes) & set(target_hashes)
                if source_hashes[path] != target_hashes[path]
            )
            resolution["missing_in_targets"][target_path] = missing
            resolution["changed_in_targets"][target_path] = changed
            resolution["extra_in_targets"][target_path] = extra
            files_to_copy = sorted(set(missing + changed))
            if files_to_copy:
                resolution["action_plan"].append(
                    {"action": "copy_to_target", "target": target_path, "files": files_to_copy}
                )
        self.resolution = resolution
        return resolution

    def mirror(self, dry_run: bool = True) -> Dict[str, Any]:
        if not hasattr(self, "resolution"):
            raise RuntimeError("Must run resolve() before mirror()")
        self.state["phase"] = "mirror"
        result: Dict[str, Any] = {
            "dry_run": dry_run,
            "files_planned": 0,
            "files_copied": 0,
            "operations": [],
        }
        for action in self.resolution["action_plan"]:
            target = Path(action["target"])
            for relative in action["files"]:
                source_file = self.source / relative
                target_file = target / relative
                if not source_file.is_file():
                    raise FileNotFoundError(f"Authoritative source file disappeared: {source_file}")
                result["files_planned"] += 1
                if not dry_run:
                    target_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, target_file)
                    result["files_copied"] += 1
                result["operations"].append(
                    {
                        "type": "copy_to_target",
                        "source": str(source_file),
                        "destination": str(target_file),
                        "dry_run": dry_run,
                    }
                )
        self.mirror_result = result
        return result

    def verify(self) -> Dict[str, Any]:
        updated = self.observe()
        self.state["phase"] = "verify"
        source_root = updated["source"]["merkle_root"]
        mismatches = []
        roots = {"source": source_root}
        if not source_root:
            mismatches.append({"repository": str(self.source), "reason": "empty_source"})
        for target_path, state in updated["targets"].items():
            roots[target_path] = state["merkle_root"]
            if state["merkle_root"] != source_root:
                mismatches.append(
                    {
                        "repository": target_path,
                        "expected": source_root,
                        "actual": state["merkle_root"],
                    }
                )
        verification = {
            "consistent": not mismatches,
            "reference_root": source_root,
            "merkle_roots": roots,
            "mismatches": mismatches,
        }
        self.verification = verification
        return verification

    def generate_report(self) -> Dict[str, Any]:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "state": self.state,
            "observations": getattr(self, "observations", {}),
            "resolution": getattr(self, "resolution", {}),
            "mirror_result": getattr(self, "mirror_result", {}),
            "verification": getattr(self, "verification", {}),
        }

    def save_report(self, output_path: Path) -> None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as handle:
            json.dump(self.generate_report(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fail-closed MRL closure sync")
    parser.add_argument("--source", default=".")
    parser.add_argument("--targets", help="Comma-separated checked-out target paths")
    parser.add_argument("--mode", choices=["full", "observe", "verify"], default="observe")
    parser.add_argument("--verify", choices=["merkle", "content"], default="merkle")
    parser.add_argument("--auto-heal", action="store_true", help="Explicitly apply source-to-target copies")
    parser.add_argument("--dry-run", action="store_true", help="Force a non-writing plan")
    parser.add_argument("--report")
    args = parser.parse_args()

    targets = [Path(item.strip()) for item in args.targets.split(",") if item.strip()] if args.targets else []
    manager = ClosureSyncManager(Path(args.source), targets)
    exit_code = 0

    if args.mode == "observe":
        manager.observe()
    elif args.mode == "verify":
        manager.observe()
        exit_code = 0 if manager.verify()["consistent"] else 1
    else:
        manager.observe()
        manager.resolve()
        apply_changes = args.auto_heal and not args.dry_run
        manager.mirror(dry_run=not apply_changes)
        consistent = manager.verify()["consistent"]
        # A dry run is a plan, so let the dedicated verification step report
        # expected differences without preventing its evidence file.
        exit_code = 0 if not apply_changes or consistent else 1

    if args.report:
        manager.save_report(Path(args.report))
    else:
        print(json.dumps(manager.generate_report(), indent=2, ensure_ascii=False))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
