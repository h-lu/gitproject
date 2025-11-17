#!/usr/bin/env python3
"""
批量生成学生作业仓库

从模板仓库生成学生作业仓库，并添加学生为协作者
"""

import os
import sys
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def generate_student_repo(gitea_url, token, org, template_repo, student_login, repo_name):
    """
    从模板生成学生作业仓库
    
    Parameters
    ----------
    gitea_url : str
        Gitea 服务器 URL
    token : str
        Gitea API Token（需要管理员权限）
    org : str
        组织名称
    template_repo : str
        模板仓库名称
    student_login : str
        学生登录名
    repo_name : str
        新仓库名称
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
        "description": f"HW1 assignment for {student_login}",
        "git_content": True,  # 包含 Git 数据（默认分支）
        "git_hooks": False,   # 不包含 Git 钩子
        "webhooks": False,    # 不包含 Web 钩子
        "topics": False,      # 不包含主题
        "avatar": False,      # 不包含头像
        "labels": False       # 不包含工单标签
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
    
    Parameters
    ----------
    gitea_url : str
        Gitea 服务器 URL
    token : str
        Gitea API Token
    org : str
        组织名称
    repo_name : str
        仓库名称
    student_login : str
        学生登录名
    permission : str
        权限级别（"read", "write", "admin"）
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
    """
    从文件读取学生列表
    
    文件格式：每行一个学生登录名，或 "学号,登录名" 格式
    """
    students = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # 支持 "学号,登录名" 或仅 "登录名"
            if "," in line:
                student_id, login = line.split(",", 1)
                students.append((student_id.strip(), login.strip()))
            else:
                students.append((None, line.strip()))
    return students


def main():
    parser = argparse.ArgumentParser(description="Generate student assignment repositories from template")
    parser.add_argument("--students", required=True, help="Student list file (one per line: student_id,login or just login)")
    parser.add_argument("--prefix", default="hw1-stu", help="Repository name prefix")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    parser.add_argument("--org", default=os.getenv("ORGANIZATION", "course-test"))
    parser.add_argument("--template", default=os.getenv("TEMPLATE_REPO", "hw1-template"))
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode (don't actually create repos)")
    parser.add_argument("--skip-collaborator", action="store_true", help="Skip adding collaborators (only create repos)")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    students = read_student_list(args.students)
    print(f"Found {len(students)} students")
    
    success_count = 0
    fail_count = 0
    
    for student_id, login in students:
        if student_id:
            repo_name = f"{args.prefix}_{student_id}"
        else:
            repo_name = f"{args.prefix}_{login}"
        
        if args.dry_run:
            print(f"[DRY RUN] Would create {repo_name} for {login}")
            continue
        
        print(f"Creating {repo_name} for {login}...", end=" ")
        
        # 生成仓库
        repo_data = generate_student_repo(
            args.gitea_url, args.token, args.org, 
            args.template, login, repo_name
        )
        
        if repo_data is None:
            fail_count += 1
            print("FAILED (repo creation)")
            continue
        
        # 添加协作者
        if args.skip_collaborator:
            success_count += 1
            print("OK (no collaborator)")
        else:
            if add_collaborator(args.gitea_url, args.token, args.org, repo_name, login):
                success_count += 1
                print("OK")
            else:
                # 仓库已创建，只是协作者添加失败，记为成功但带警告
                success_count += 1
                print("OK (repo created, collaborator failed - user may not exist)")
    
    print(f"\nSummary: {success_count} succeeded, {fail_count} failed")


if __name__ == "__main__":
    main()


