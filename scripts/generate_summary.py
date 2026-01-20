#!/usr/bin/env python3
"""
Generate GitHub Actions Step Summary from Sync Report
======================================================

Extracts sync report data and formats it for GitHub Actions step summary.

Author: MR.liou
"""

import json
import sys
import os


def generate_summary(report_path: str) -> int:
    """
    Generate summary from sync report
    
    Args:
        report_path: Path to sync report JSON file
        
    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        if not report_path:
            print("Error: REPORT_PATH environment variable is not set", file=sys.stderr)
            return 1
            
        if not os.path.exists(report_path):
            print(f"Error: Report file not found: {report_path}", file=sys.stderr)
            return 1
        
        with open(report_path) as f:
            report = json.load(f)

        print(f"**Pattern:** {report.get('pattern', 'N/A')}")
        print(f"**GitHub Results:** {report.get('github_results', 0)}")
        print(f"**Particles Created:** {report.get('particles_created', 0)}")
        print(f"**Particles Merged:** {report.get('particles_merged', 0)}")
        print(f"**Naming Decisions:** {report.get('naming_decisions', 0)}")

        if report.get('test_results'):
            tr = report['test_results']
            if 'passed' in tr and 'total' in tr:
                print(f"**Tests:** {tr['passed']}/{tr['total']} passed")

        if report.get('errors'):
            print(f"**Errors:** {len(report['errors'])}")
        
        return 0

    except Exception as e:
        print(f"Error reading report: {e}", file=sys.stderr)
        return 0  # Don't fail the workflow


if __name__ == '__main__':
    report_path = os.environ.get("REPORT_PATH", sys.argv[1] if len(sys.argv) > 1 else "")
    sys.exit(generate_summary(report_path))
