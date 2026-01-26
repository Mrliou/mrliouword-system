#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Documentation Verification Script
Author: MR.liou
Date: 2026-01-26
origin_signature: MrLiouWord

Verify that all documentation files meet the requirements.
"""

import os
import sys
from pathlib import Path
import json


class DocVerifier:
    """Verify documentation files."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.results = {
            "total_files": 0,
            "files_checked": 0,
            "files_with_signature": 0,
            "utf8_compliant": 0,
            "issues": []
        }
    
    def verify_all(self):
        """Verify all documentation files."""
        print("Starting verification...")
        print("=" * 60)
        
        # Check docs directory
        docs_path = self.root_path / "docs"
        if docs_path.exists():
            self._check_directory(docs_path)
        
        # Check scripts directory
        scripts_path = self.root_path / "scripts"
        if scripts_path.exists():
            self._check_directory(scripts_path)
        
        self._print_summary()
    
    def _check_directory(self, directory: Path):
        """Check all files in a directory."""
        for item in directory.rglob("*"):
            if item.is_file() and not self._should_skip(item):
                self.results["total_files"] += 1
                self._check_file(item)
    
    def _should_skip(self, path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [
            ".git", "__pycache__", ".pyc", ".DS_Store"
        ]
        return any(pattern in str(path) for pattern in skip_patterns)
    
    def _check_file(self, filepath: Path):
        """Check individual file."""
        self.results["files_checked"] += 1
        
        try:
            # Check UTF-8 encoding
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.results["utf8_compliant"] += 1
            
            # Check for origin_signature
            if "origin_signature" in content or "MrLiouWord" in content:
                self.results["files_with_signature"] += 1
                status = "✓"
            else:
                status = "✗"
                self.results["issues"].append({
                    "file": str(filepath),
                    "issue": "Missing origin_signature"
                })
            
            print(f"{status} {filepath.relative_to(self.root_path)}")
            
        except UnicodeDecodeError:
            print(f"✗ {filepath.relative_to(self.root_path)} - NOT UTF-8")
            self.results["issues"].append({
                "file": str(filepath),
                "issue": "Not UTF-8 encoded"
            })
        except Exception as e:
            print(f"✗ {filepath.relative_to(self.root_path)} - Error: {e}")
            self.results["issues"].append({
                "file": str(filepath),
                "issue": str(e)
            })
    
    def _print_summary(self):
        """Print verification summary."""
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"Total files: {self.results['total_files']}")
        print(f"Files checked: {self.results['files_checked']}")
        print(f"UTF-8 compliant: {self.results['utf8_compliant']}")
        print(f"Files with origin_signature: {self.results['files_with_signature']}")
        print(f"Issues found: {len(self.results['issues'])}")
        
        if self.results["issues"]:
            print("\nISSUES:")
            for issue in self.results["issues"]:
                print(f"  - {issue['file']}: {issue['issue']}")
        
        print("=" * 60)
        
        # Return exit code
        return 0 if len(self.results["issues"]) == 0 else 1


def main():
    """Main function."""
    verifier = DocVerifier("/home/runner/work/mrliouword-system/mrliouword-system")
    exit_code = verifier.verify_all()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
