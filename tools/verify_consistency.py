#!/usr/bin/env python3
"""Fail-closed Merkle consistency verifier."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from merkle_builder import ParticleMerkleTree, discover_particle_files


def verify_consistency(repos: list, output_path: Optional[Path] = None) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "consistent": False,
        "repositories": {},
        "reference_root": None,
        "mismatches": [],
    }

    for index, repo_value in enumerate(repos):
        repo = Path(repo_value).resolve()
        if not repo.is_dir():
            result["repositories"][str(repo)] = {"status": "not_found", "merkle_root": None}
            result["mismatches"].append({"repository": str(repo), "reason": "not_found"})
            continue

        files = discover_particle_files(repo)
        tree = ParticleMerkleTree()
        tree.build_from_particles(files, root=repo)
        status = "verified" if files else "empty"
        result["repositories"][str(repo)] = {
            "status": status,
            "merkle_root": tree.merkle_root,
            "particle_count": len(files),
            "tree_height": max((node.get("level", 0) for node in tree.nodes), default=-1) + 1,
        }

        if index == 0:
            result["reference_root"] = tree.merkle_root
            if not files:
                result["mismatches"].append({"repository": str(repo), "reason": "empty_source"})
        elif tree.merkle_root != result["reference_root"]:
            result["mismatches"].append(
                {
                    "repository": str(repo),
                    "expected": result["reference_root"],
                    "actual": tree.merkle_root,
                }
            )

    result["consistent"] = bool(repos) and not result["mismatches"]
    if output_path:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, ensure_ascii=False)
            handle.write("\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify MRL consistency")
    parser.add_argument("repos", nargs="+")
    parser.add_argument("--output", "-o")
    parser.add_argument("--check-merkle", action="store_true")
    parser.add_argument("--cross-repo", action="store_true")
    args = parser.parse_args()
    result = verify_consistency(args.repos, Path(args.output) if args.output else None)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["consistent"] else 1


if __name__ == "__main__":
    sys.exit(main())
