#!/usr/bin/env python3
"""
Sync autograde scripts from courses/CS101/common/autograde to all assignment templates.
Usage: python3 scripts/sync_autograde.py
"""

import os
import shutil
import sys
from pathlib import Path

def main():
    # Base paths
    project_root = Path(__file__).parent.parent
    course_dir = project_root / "courses" / "CS101"
    common_autograde = course_dir / "common" / "autograde"
    assignments_dir = course_dir / "assignments"

    if not common_autograde.exists():
        print(f"Error: Common autograde directory not found at {common_autograde}")
        sys.exit(1)

    print(f"Source: {common_autograde}")

    # Iterate over assignments
    if not assignments_dir.exists():
        print(f"Error: Assignments directory not found at {assignments_dir}")
        sys.exit(1)

    for assignment in assignments_dir.iterdir():
        if not assignment.is_dir() or assignment.name.startswith("."):
            continue
        
        template_autograde = assignment / "template" / ".autograde"
        
        if not (assignment / "template").exists():
            print(f"Skipping {assignment.name}: No template directory")
            continue

        print(f"Syncing to {assignment.name}...")
        
        # Ensure destination directory exists
        template_autograde.mkdir(parents=True, exist_ok=True)
        
        # Copy files using rsync-like behavior (overwrite)
        try:
            shutil.copytree(common_autograde, template_autograde, dirs_exist_ok=True)
            print(f"✅ Synced {assignment.name}")
        except Exception as e:
            print(f"❌ Failed to sync {assignment.name}: {e}")

if __name__ == "__main__":
    main()
