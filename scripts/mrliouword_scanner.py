#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MrLiouWord Scanner
Author: MR.liou
Date: 2026-01-26
origin_signature: MrLiouWord

This module scans and analyzes the MrLiouWord system components.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class MrLiouWordScanner:
    """
    Scanner for MrLiouWord system components.
    
    怎麼過去，就怎麼回來
    """
    
    def __init__(self, root_path: str = "."):
        """Initialize scanner with root path."""
        self.root_path = Path(root_path)
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "origin_signature": "MrLiouWord",
            "files": [],
            "modules": [],
            "statistics": {}
        }
    
    def scan_directory(self, directory: Optional[Path] = None) -> Dict[str, Any]:
        """Scan a directory for MrLiouWord components."""
        if directory is None:
            directory = self.root_path
        
        print(f"Scanning directory: {directory}")
        
        for item in directory.rglob("*"):
            if item.is_file() and not self._should_ignore(item):
                self._scan_file(item)
        
        self._calculate_statistics()
        return self.scan_results
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        ignore_patterns = [
            ".git", "__pycache__", "node_modules", 
            ".pyc", ".DS_Store", "dist", "build"
        ]
        return any(pattern in str(path) for pattern in ignore_patterns)
    
    def _scan_file(self, filepath: Path) -> None:
        """Scan individual file."""
        try:
            file_info = {
                "path": str(filepath.relative_to(self.root_path)),
                "size": filepath.stat().st_size,
                "extension": filepath.suffix,
                "hash": self._calculate_hash(filepath)
            }
            
            # Check for origin_signature
            if self._has_origin_signature(filepath):
                file_info["origin_signature"] = "MrLiouWord"
            
            self.scan_results["files"].append(file_info)
            
        except Exception as e:
            print(f"Error scanning {filepath}: {e}")
    
    def _calculate_hash(self, filepath: Path) -> str:
        """Calculate SHA256 hash of file."""
        try:
            sha256 = hashlib.sha256()
            with open(filepath, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return ""
    
    def _has_origin_signature(self, filepath: Path) -> bool:
        """Check if file contains origin_signature."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(1024)  # Check first 1KB
                return "origin_signature" in content or "MrLiouWord" in content
        except (IOError, OSError) as e:
            logger.warning(f"Could not read {filepath}: {e}")
            return False
    
    def _calculate_statistics(self) -> None:
        """Calculate scan statistics."""
        self.scan_results["statistics"] = {
            "total_files": len(self.scan_results["files"]),
            "files_with_signature": sum(
                1 for f in self.scan_results["files"] 
                if "origin_signature" in f
            ),
            "total_size": sum(
                f["size"] for f in self.scan_results["files"]
            )
        }
    
    def export_results(self, output_path: str) -> bool:
        """Export scan results to JSON file."""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.scan_results, f, indent=2, ensure_ascii=False)
            print(f"Results exported to {output_path}")
            return True
        except Exception as e:
            print(f"Failed to export results: {e}")
            return False
    
    def print_summary(self) -> None:
        """Print scan summary."""
        stats = self.scan_results["statistics"]
        print("\n=== MrLiouWord Scanner Summary ===")
        print(f"Total files scanned: {stats['total_files']}")
        print(f"Files with origin_signature: {stats['files_with_signature']}")
        print(f"Total size: {stats['total_size']:,} bytes")
        print("=" * 40)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MrLiouWord System Scanner")
    parser.add_argument("path", nargs="?", default=".", help="Path to scan")
    parser.add_argument("-o", "--output", help="Output JSON file")
    
    args = parser.parse_args()
    
    scanner = MrLiouWordScanner(args.path)
    scanner.scan_directory()
    scanner.print_summary()
    
    if args.output:
        scanner.export_results(args.output)


if __name__ == "__main__":
    main()
