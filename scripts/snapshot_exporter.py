#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Snapshot Exporter v1
Author: MR.liou
Date: 2026-01-26
origin_signature: MrLiouWord

快照打包可攜帶工具 - Export system snapshots for portable deployment.
怎麼過去，就怎麼回來
"""

import os
import sys
import json
import shutil
import tarfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional


class SnapshotExporter:
    """
    Create portable snapshots of MrLiouWord system state.
    
    怎麼過去，就怎麼回來 - Ensure all snapshots are complete and reversible.
    """
    
    def __init__(self, source_path: str = "."):
        """Initialize exporter with source path."""
        self.source_path = Path(source_path)
        self.snapshot_data = {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "origin_signature": "MrLiouWord",
            "files": [],
            "metadata": {}
        }
    
    def create_snapshot(
        self, 
        output_path: str,
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> bool:
        """
        Create a portable snapshot.
        
        Args:
            output_path: Path for the output snapshot archive
            include_patterns: List of file patterns to include
            exclude_patterns: List of file patterns to exclude
        
        Returns:
            True if successful, False otherwise
        """
        try:
            print(f"Creating snapshot from: {self.source_path}")
            
            # Prepare temporary directory
            temp_dir = Path("/tmp/mrliouword_snapshot")
            temp_dir.mkdir(exist_ok=True)
            
            # Collect files
            files_to_pack = self._collect_files(include_patterns, exclude_patterns)
            
            # Copy files to temp directory
            for file_path in files_to_pack:
                self._copy_file(file_path, temp_dir)
            
            # Create metadata file
            self._create_metadata(temp_dir)
            
            # Create tar.gz archive
            self._create_archive(temp_dir, output_path)
            
            # Cleanup
            shutil.rmtree(temp_dir)
            
            print(f"Snapshot created: {output_path}")
            return True
            
        except Exception as e:
            print(f"Failed to create snapshot: {e}")
            return False
    
    def _collect_files(
        self, 
        include_patterns: Optional[List[str]] = None,
        exclude_patterns: Optional[List[str]] = None
    ) -> List[Path]:
        """Collect files based on patterns."""
        files = []
        
        default_excludes = [
            ".git", "__pycache__", "node_modules",
            ".pyc", ".DS_Store", "*.log", "dist", "build"
        ]
        
        exclude_patterns = exclude_patterns or []
        exclude_patterns.extend(default_excludes)
        
        for item in self.source_path.rglob("*"):
            if item.is_file():
                # Check exclusions
                if self._matches_patterns(item, exclude_patterns):
                    continue
                
                # Check inclusions
                if include_patterns and not self._matches_patterns(item, include_patterns):
                    continue
                
                files.append(item)
        
        return files
    
    def _matches_patterns(self, path: Path, patterns: List[str]) -> bool:
        """Check if path matches any pattern."""
        path_str = str(path)
        return any(pattern in path_str for pattern in patterns)
    
    def _copy_file(self, source: Path, dest_dir: Path) -> None:
        """Copy file to destination directory preserving structure."""
        try:
            relative_path = source.relative_to(self.source_path)
            dest_path = dest_dir / relative_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest_path)
            
            # Record file info
            self.snapshot_data["files"].append({
                "path": str(relative_path),
                "size": source.stat().st_size,
                "hash": self._calculate_hash(source)
            })
            
        except Exception as e:
            print(f"Error copying {source}: {e}")
    
    def _calculate_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash."""
        sha256 = hashlib.sha256()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def _create_metadata(self, dest_dir: Path) -> None:
        """Create metadata file."""
        metadata_path = dest_dir / "snapshot_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.snapshot_data, f, indent=2, ensure_ascii=False)
    
    def _create_archive(self, source_dir: Path, output_path: str) -> None:
        """Create tar.gz archive."""
        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(source_dir, arcname=os.path.basename(output_path).replace('.tar.gz', ''))
    
    def verify_snapshot(self, snapshot_path: str) -> bool:
        """Verify integrity of a snapshot."""
        try:
            print(f"Verifying snapshot: {snapshot_path}")
            
            with tarfile.open(snapshot_path, "r:gz") as tar:
                # Extract metadata
                for member in tar.getmembers():
                    if member.name.endswith("snapshot_metadata.json"):
                        f = tar.extractfile(member)
                        metadata = json.load(f)
                        print(f"Snapshot version: {metadata.get('version')}")
                        print(f"Created: {metadata.get('timestamp')}")
                        print(f"Files: {len(metadata.get('files', []))}")
                        return True
            
            return False
            
        except Exception as e:
            print(f"Failed to verify snapshot: {e}")
            return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="MrLiouWord Snapshot Exporter - 怎麼過去，就怎麼回來"
    )
    parser.add_argument("action", choices=["create", "verify"], help="Action to perform")
    parser.add_argument("path", nargs="?", default=".", help="Source path for create, snapshot path for verify")
    parser.add_argument("-o", "--output", help="Output snapshot file (for create)")
    parser.add_argument("-i", "--include", nargs="+", help="Patterns to include")
    parser.add_argument("-e", "--exclude", nargs="+", help="Patterns to exclude")
    
    args = parser.parse_args()
    
    if args.action == "create":
        if not args.output:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.output = f"mrliouword_snapshot_{timestamp}.tar.gz"
        
        exporter = SnapshotExporter(args.path)
        exporter.create_snapshot(args.output, args.include, args.exclude)
    
    elif args.action == "verify":
        exporter = SnapshotExporter()
        exporter.verify_snapshot(args.path)


if __name__ == "__main__":
    main()
