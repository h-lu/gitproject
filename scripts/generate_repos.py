#!/usr/bin/env python3
"""
批量生成学生作业仓库

从模板仓库生成学生作业仓库，并添加学生为协作者
支持多课程/多作业模式
"""

import os
import sys
import argparse
import requests
import yaml
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def load_course_config(course_dir):
    config_path = Path(course_dir) / "course_config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Course config not found: {config_path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_assignment_config(course_dir, assignment_id):
    config_path = Path(course_dir) / "assignments" / assignment_id / "config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Assignment config not found: {config_path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run_git_cmd(cmd, cwd=None):
    try:
        subprocess.run(cmd, check=True, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e.cmd}\nStderr: {e.stderr.decode()}", file=sys.stderr)
        raise

def ensure_org_exists(gitea_url, token, org_name):
    """
    确保 Gitea 组织存在。如果不存在则创建。
    """
    api_url = f"{gitea_url}/api/v1/orgs/{org_name}"
    headers = {"Authorization": f"token {token}"}
    
    # 检查组织是否存在
    resp = requests.get(api_url, headers=headers)
    if resp.status_code == 200:
        print(f"Organization {org_name} already exists.")
        return True
    
    # 创建组织
    print(f"Creating organization {org_name}...")
    create_url = f"{gitea_url}/api/v1/orgs"
    data = {
        "username": org_name,
        "visibility": "public",
        "repo_admin_change_team_access": True
    }
    resp = requests.post(create_url, headers=headers, json=data)
    if resp.status_code == 201:
        print(f"✓ Organization {org_name} created successfully.")
        return True
    else:
        print(f"Failed to create organization: {resp.text}", file=sys.stderr)
        return False

def ensure_repo_exists(gitea_url, token, org, repo_name, source_dir, is_private=False, is_template=False):
    """
    确保仓库存在。如果不存在，创建并推送 source_dir 的内容。
    """
    api_url = f"{gitea_url}/api/v1/repos/{org}/{repo_name}"
    headers = {"Authorization": f"token {token}"}
    
    # Check if repo exists
    resp = requests.get(api_url, headers=headers)
    if resp.status_code == 200:
        print(f"Repository {org}/{repo_name} already exists.")
        # Update template setting if needed
        if is_template:
            patch_url = f"{gitea_url}/api/v1/repos/{org}/{repo_name}"
            patch_data = {"template": True}
            requests.patch(patch_url, headers=headers, json=patch_data)
            print(f"✓ Marked {repo_name} as template repository.")
        return True
    
    print(f"Creating repository {org}/{repo_name}...")
    # Create repo
    create_url = f"{gitea_url}/api/v1/orgs/{org}/repos"
    data = {
        "name": repo_name,
        "private": is_private,
        "template": is_template,
        "auto_init": False
    }
    resp = requests.post(create_url, headers=headers, json=data)
    if resp.status_code != 201:
        print(f"Failed to create repo: {resp.text}", file=sys.stderr)
        return False
    
    # Push content
    if source_dir and Path(source_dir).exists():
        print(f"Pushing content from {source_dir}...")
        
        # Copy autograde scripts from scripts/autograde to template/.autograde
        project_root = Path(__file__).parent.parent
        autograde_source = project_root / "scripts" / "autograde"
        autograde_dest = Path(source_dir) / ".autograde"
        
        if autograde_source.exists():
            print(f"  Copying autograde scripts to {autograde_dest}...")
            autograde_dest.mkdir(parents=True, exist_ok=True)
            shutil.copytree(autograde_source, autograde_dest, dirs_exist_ok=True)
            print(f"  ✅ Autograde scripts copied")
        else:
            print(f"  ⚠️  Warning: Autograde scripts not found at {autograde_source}")
        
        # Initialize git repo if needed
        git_dir = Path(source_dir) / ".git"
        if git_dir.exists():
             # If it's already a git repo, we need to commit the new autograde files
             run_git_cmd("git add .autograde", cwd=source_dir)
             run_git_cmd("git commit -m 'Add autograde scripts' || true", cwd=source_dir)
        else:
            run_git_cmd("git init", cwd=source_dir)
            run_git_cmd("git add .", cwd=source_dir)
            run_git_cmd("git commit -m 'Initial commit'", cwd=source_dir)
            
        # Add remote and push
        remote_url = f"{gitea_url}/{org}/{repo_name}.git"
        # Insert token for auth
        auth_remote_url = remote_url.replace("://", f"://{token}@")
        
        try:
            run_git_cmd(f"git remote add origin {auth_remote_url}", cwd=source_dir)
        except:
            run_git_cmd(f"git remote set-url origin {auth_remote_url}", cwd=source_dir)
            
        run_git_cmd("git branch -M main", cwd=source_dir)
        run_git_cmd("git push -u origin main", cwd=source_dir)
        print("Content pushed successfully.")
        import time
        print("Waiting 5 seconds for Gitea to process the push...")
        time.sleep(5)
        
    return True

def generate_student_repo(gitea_url, token, org, template_repo, student_login, repo_name):
    """
    从模板生成学生作业仓库
    """
    api_url = f"{gitea_url}/api/v1/repos/{org}/{template_repo}/generate"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "owner": org,
        "name": repo_name,
        "private": True,
        "description": f"Assignment for {student_login}",
        "git_content": True,
        "git_hooks": False,
        "webhooks": False,
        "topics": False,
        "avatar": False,
        "labels": False
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"Error generating repo {repo_name}: {e}", file=sys.stderr)
        if response.status_code == 409:
            print(f"  Repository {repo_name} already exists", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error generating repo {repo_name}: {e}", file=sys.stderr)
        return None


def add_collaborator(gitea_url, token, org, repo_name, student_login, permission="write"):
    """
    添加学生为仓库协作者
    """
    api_url = f"{gitea_url}/api/v1/repos/{org}/{repo_name}/collaborators/{student_login}"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    data = {"permission": permission}
    
    try:
        response = requests.put(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error adding collaborator {student_login} to {repo_name}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error adding collaborator {student_login} to {repo_name}: {e}", file=sys.stderr)
        return False


def read_student_list(file_path):
    students = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "," in line:
                student_id, login = line.split(",", 1)
                students.append((student_id.strip(), login.strip()))
            else:
                students.append((None, line.strip()))
    return students


def main():
    parser = argparse.ArgumentParser(description="Generate student assignment repositories")
    
    # Required arguments
    parser.add_argument("--course", required=True, help="Path to course directory (e.g., courses/CS101)")
    parser.add_argument("--assignment", required=True, help="Assignment ID (e.g., hw1)")
    
    # Optional arguments
    parser.add_argument("--students", help="Student list file (overrides course default)")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode")
    parser.add_argument("--skip-collaborator", action="store_true", help="Skip adding collaborators")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        sys.exit(1)

    print(f"Running in Course Mode: {args.course} / {args.assignment}")
    course_config = load_course_config(args.course)
    assign_config = load_assignment_config(args.course, args.assignment)
    
    org = course_config.get("organization")
    if not org:
        print("Error: 'organization' not defined in course config", file=sys.stderr)
        sys.exit(1)
        
    # Default paths
    students_file = Path(args.course) / "students.txt"
    if args.students:
        students_file = args.students
        
    assignment_dir = Path(args.course) / "assignments" / args.assignment
    template_dir = assignment_dir / "template"
    tests_dir = assignment_dir / "tests"
    
    template_repo_name = f"{args.assignment}-template"
    tests_repo_name = f"{args.assignment}-tests"
    repo_prefix = f"{args.assignment}-stu"
    
    # Ensure organization exists (create if needed)
    if not args.dry_run:
        if not ensure_org_exists(args.gitea_url, args.token, org):
            print(f"Error: Failed to create organization {org}", file=sys.stderr)
            sys.exit(1)
        
        # Ensure Template and Tests repos exist
        ensure_repo_exists(args.gitea_url, args.token, org, template_repo_name, template_dir, is_private=False, is_template=True)
        ensure_repo_exists(args.gitea_url, args.token, org, tests_repo_name, tests_dir, is_private=True, is_template=False)

    # Read students
    if not Path(students_file).exists():
         print(f"Error: Student list file not found: {students_file}", file=sys.stderr)
         sys.exit(1)
         
    students = read_student_list(students_file)
    print(f"Found {len(students)} students in {students_file}")
    
    success_count = 0
    fail_count = 0
    
    for student_id, login in students:
        if student_id:
            repo_name = f"{repo_prefix}_{student_id}"
        else:
            repo_name = f"{repo_prefix}_{login}"
        
        if args.dry_run:
            print(f"[DRY RUN] Would create {repo_name} for {login} in org {org}")
            continue
        
        print(f"Creating {repo_name} for {login}...", end=" ")
        
        # Generate repo
        repo_data = generate_student_repo(
            args.gitea_url, args.token, org, 
            template_repo_name, login, repo_name
        )
        
        if repo_data is None:
            fail_count += 1
            print("FAILED (repo creation)")
            continue
        
        # Add collaborator
        if args.skip_collaborator:
            success_count += 1
            print("OK (no collaborator)")
        else:
            if add_collaborator(args.gitea_url, args.token, org, repo_name, login):
                success_count += 1
                print("OK")
            else:
                success_count += 1
                print("OK (repo created, collaborator failed)")
    
    print(f"\nSummary: {success_count} succeeded, {fail_count} failed")

if __name__ == "__main__":
    main()
