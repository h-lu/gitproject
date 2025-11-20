#!/usr/bin/env python3
"""
Sync autograde scripts from scripts/autograde to all assignment templates.
Usage: python3 scripts/sync_autograde.py [--course COURSE_DIR]
"""

import argparse
import os
import shutil
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(description="Sync autograde scripts to assignment templates")
    parser.add_argument("--course", help="Course directory (e.g., courses/CS101). If not specified, sync to all courses.")
    args = parser.parse_args()
    
    # Base paths
    project_root = Path(__file__).parent.parent
    common_autograde = project_root / "scripts" / "autograde"
    
    if not common_autograde.exists():
        print(f"Error: Autograde directory not found at {common_autograde}")
        sys.exit(1)

    print(f"Source: {common_autograde}")
    
    # Determine which courses to sync
    if args.course:
        course_dirs = [project_root / args.course]
    else:
        courses_root = project_root / "courses"
        if not courses_root.exists():
            print(f"Error: Courses directory not found at {courses_root}")
            sys.exit(1)
        course_dirs = [d for d in courses_root.iterdir() if d.is_dir() and not d.name.startswith(".")]
    
    # Sync to each course
    for course_dir in course_dirs:
        assignments_dir = course_dir / "assignments"
        if not assignments_dir.exists():
            continue
        
        print(f"\nSyncing to course: {course_dir.name}")

        # Iterate over assignments
        for assignment in assignments_dir.iterdir():
            if not assignment.is_dir() or assignment.name.startswith("."):
                continue
            
            template_autograde = assignment / "template" / ".autograde"
            
            if not (assignment / "template").exists():
                print(f"  Skipping {assignment.name}: No template directory")
                continue

            print(f"  Syncing to {assignment.name}...")
            
            # Ensure destination directory exists
            template_autograde.mkdir(parents=True, exist_ok=True)
            
            # Copy files using rsync-like behavior (overwrite)
            try:
                shutil.copytree(common_autograde, template_autograde, dirs_exist_ok=True)
                print(f"  ✅ Synced {assignment.name}")
            except Exception as e:
                print(f"  ❌ Failed to sync {assignment.name}: {e}")

if __name__ == "__main__":
    main()
