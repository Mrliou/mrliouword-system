#!/usr/bin/env python3
"""Deterministic Merkle tree builder for MRL particle content."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional


PARTICLE_PATTERNS = (
    "core/particles/**/*.json",
    "docs/particle-dictionary/**/*.md",
    ".mrliou/**/*.json",
)

# Runtime outputs must never become inputs to their own integrity hash.
VOLATILE_MRL_FILES = {
    ".mrliou/merkle.json",
    ".mrliou/merkle_new.json",
    ".mrliou/health.json",
    ".mrliou/sync_report.json",
    ".mrliou/verification_report.json",
    ".mrliou/final_sync_report.json",
}


def discover_particle_files(repo_path: Path) -> List[Path]:
    """Return stable, unique particle inputs and exclude generated metadata."""
    root = Path(repo_path).resolve()
    discovered: Dict[str, Path] = {}
    for pattern in PARTICLE_PATTERNS:
        for candidate in root.glob(pattern):
            if not candidate.is_file():
                continue
            relative = candidate.relative_to(root).as_posix()
            if relative in VOLATILE_MRL_FILES:
                continue
            discovered[relative] = candidate
    return [discovered[key] for key in sorted(discovered)]


class ParticleMerkleTree:
    """Path-bound Merkle tree for particle files."""

    def __init__(self, hash_algorithm: str = "sha256"):
        self.hash_algorithm = hash_algorithm
        self.nodes: List[Dict[str, Any]] = []
        self.merkle_root = ""
        self.leaf_count = 0

    def _hash(self, data: str) -> str:
        hasher = hashlib.new(self.hash_algorithm)
        hasher.update(data.encode("utf-8"))
        return hasher.hexdigest()

    def _hash_file(self, file_path: Path) -> str:
        with open(file_path, "rb") as handle:
            hasher = hashlib.new(self.hash_algorithm)
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def build_from_particles(
        self, particle_files: Iterable[Path], root: Optional[Path] = None
    ) -> str:
        files = [Path(path) for path in particle_files]
        if not files:
            self.nodes = []
            self.merkle_root = ""
            self.leaf_count = 0
            return ""

        root_path = Path(root).resolve() if root else None

        def label(path: Path) -> str:
            resolved = path.resolve()
            return (
                resolved.relative_to(root_path).as_posix()
                if root_path
                else path.as_posix()
            )

        leaves = []
        for file_path in sorted(files, key=label):
            relative = label(file_path)
            content_hash = self._hash_file(file_path)
            leaves.append(
                {
                    "file": relative,
                    "content_hash": content_hash,
                    "hash": self._hash(f"{relative}\0{content_hash}"),
                    "level": 0,
                }
            )

        self.leaf_count = len(leaves)
        self.nodes = leaves.copy()
        current_level = leaves
        level = 1

        while len(current_level) > 1:
            next_level = []
            for index in range(0, len(current_level), 2):
                left = current_level[index]
                right = current_level[index + 1] if index + 1 < len(current_level) else None
                parent_hash = (
                    self._hash(left["hash"] + right["hash"])
                    if right
                    else left["hash"]
                )
                parent = {
                    "hash": parent_hash,
                    "level": level,
                    "left": left["hash"],
                    "right": right["hash"] if right else None,
                }
                next_level.append(parent)
                self.nodes.append(parent)
            current_level = next_level
            level += 1

        self.merkle_root = current_level[0]["hash"]
        return self.merkle_root

    def verify_integrity(self, expected_root: str) -> bool:
        return self.merkle_root == expected_root

    def find_missing_nodes(self, other_tree: "ParticleMerkleTree") -> List[Dict[str, Any]]:
        mine = {node["hash"] for node in self.nodes if node.get("level") == 0}
        return [
            node
            for node in other_tree.nodes
            if node.get("level") == 0 and node["hash"] not in mine
        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": "v1.1",
            "merkle_root": self.merkle_root,
            "tree_height": max((node.get("level", 0) for node in self.nodes), default=-1) + 1,
            "leaf_count": self.leaf_count,
            "hash_algorithm": self.hash_algorithm,
            "excluded_generated_files": sorted(VOLATILE_MRL_FILES),
            "nodes": self.nodes,
        }

    def save(self, output_path: Path) -> None:
        destination = Path(output_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    @classmethod
    def load(cls, input_path: Path) -> "ParticleMerkleTree":
        with open(input_path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        tree = cls(hash_algorithm=data.get("hash_algorithm", "sha256"))
        tree.merkle_root = data.get("merkle_root", "")
        tree.leaf_count = data.get("leaf_count", 0)
        tree.nodes = data.get("nodes", [])
        return tree


def build_particle_merkle_tree(
    repo_path: Path, output_path: Optional[Path] = None
) -> ParticleMerkleTree:
    root = Path(repo_path).resolve()
    tree = ParticleMerkleTree()
    tree.build_from_particles(discover_particle_files(root), root=root)
    if output_path:
        tree.save(output_path)
    return tree


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python merkle_builder.py <repo_path> [output_path]")
        sys.exit(1)
    repository = Path(sys.argv[1])
    destination = Path(sys.argv[2]) if len(sys.argv) > 2 else repository / ".mrliou" / "merkle.json"
    merkle_tree = build_particle_merkle_tree(repository, destination)
    print("Merkle tree built successfully")
    print(f"Root: {merkle_tree.merkle_root}")
    print(f"Leaves: {merkle_tree.leaf_count}")
    print(f"Saved to: {destination}")
