#!/usr/bin/env python3
"""
更新所有分支的 workflow 文件

将模板仓库的 workflow 文件更新到学生仓库的所有分支
"""

import os
import sys
import argparse
import requests
import tempfile
import subprocess
from dotenv import load_dotenv

load_dotenv()


def get_repos(gitea_url, token, org, prefix):
    """获取所有匹配前缀的仓库列表"""
    api_url = f"{gitea_url}/api/v1/orgs/{org}/repos"
    headers = {"Authorization": f"token {token}"}
    
    repos = []
    page = 1
    per_page = 50
    
    while True:
        params = {"page": page, "limit": per_page}
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                break
            
            for repo in data:
                if repo["name"].startswith(prefix):
                    repos.append(repo["name"])
            
            if len(data) < per_page:
                break
            
            page += 1
        except Exception as e:
            print(f"Error fetching repos: {e}", file=sys.stderr)
            break
    
    return repos


def get_branches(gitea_url, token, org, repo_name):
    """获取仓库的所有分支"""
    api_url = f"{gitea_url}/api/v1/repos/{org}/{repo_name}/branches"
    headers = {"Authorization": f"token {token}"}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        branches = [b["name"] for b in response.json()]
        return branches
    except Exception as e:
        print(f"Error fetching branches: {e}", file=sys.stderr)
        return []


def update_workflow_in_branch(gitea_url, token, org, repo_name, branch, template_workflow_dir):
    """更新指定分支的 workflow 文件"""
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_dir = os.path.join(temp_dir, repo_name)
        
        # 克隆仓库
        if token:
            clone_url = f"http://oauth2:{token}@{gitea_url.replace('http://', '').replace('https://', '')}/{org}/{repo_name}.git"
        else:
            clone_url = f"{gitea_url}/{org}/{repo_name}.git"
        
        try:
            # 克隆
            subprocess.run(
                ["git", "clone", "--depth", "1", clone_url, repo_dir],
                check=True,
                capture_output=True,
                text=True
            )
            
            # 获取所有分支
            subprocess.run(
                ["git", "-C", repo_dir, "fetch", "--all"],
                check=True,
                capture_output=True
            )
            
            # 切换到目标分支
            try:
                # 先尝试从远程获取分支
                subprocess.run(
                    ["git", "-C", repo_dir, "fetch", "origin", f"{branch}:{branch}"],
                    capture_output=True
                )
                # 切换到分支
                subprocess.run(
                    ["git", "-C", repo_dir, "checkout", branch],
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError:
                # 如果分支不存在，从 main 创建
                try:
                    subprocess.run(
                        ["git", "-C", repo_dir, "checkout", "main"],
                        check=True,
                        capture_output=True
                    )
                    subprocess.run(
                        ["git", "-C", repo_dir, "checkout", "-b", branch],
                        check=True,
                        capture_output=True
                    )
                except:
                    # 如果 main 也不存在，使用当前分支
                    pass
            
            # 更新 workflow 文件
            repo_workflow_dir = os.path.join(repo_dir, ".gitea", "workflows")
            os.makedirs(repo_workflow_dir, exist_ok=True)
            
            updated = False
            if os.path.isdir(template_workflow_dir):
                for filename in os.listdir(template_workflow_dir):
                    if filename.endswith(('.yml', '.yaml')):
                        src = os.path.join(template_workflow_dir, filename)
                        dst = os.path.join(repo_workflow_dir, filename)
                        
                        with open(src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        with open(dst, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        updated = True
            
            # 同时更新 .autograde 目录
            template_autograde_dir = os.path.join(os.path.dirname(template_workflow_dir), "..", ".autograde")
            template_autograde_dir = os.path.normpath(template_autograde_dir)
            repo_autograde_dir = os.path.join(repo_dir, ".autograde")
            
            if os.path.isdir(template_autograde_dir):
                os.makedirs(repo_autograde_dir, exist_ok=True)
                
                # 删除旧的 create_grade_metadata.py（已被 create_minimal_metadata.py 替代）
                old_metadata_script = os.path.join(repo_autograde_dir, "create_grade_metadata.py")
                if os.path.exists(old_metadata_script):
                    os.remove(old_metadata_script)
                    updated = True
                
                for filename in os.listdir(template_autograde_dir):
                    if filename.endswith('.py'):
                        src = os.path.join(template_autograde_dir, filename)
                        dst = os.path.join(repo_autograde_dir, filename)
                        
                        with open(src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        with open(dst, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        # 设置执行权限
                        os.chmod(dst, 0o755)
                        updated = True
            
            if not updated:
                return True
            
            # 配置 git
            subprocess.run(
                ["git", "-C", repo_dir, "config", "user.name", "Gitea Actions"],
                check=True,
                capture_output=True
            )
            subprocess.run(
                ["git", "-C", repo_dir, "config", "user.email", "gitea-actions@noreply.localhost"],
                check=True,
                capture_output=True
            )
            
            # 添加文件
            subprocess.run(
                ["git", "-C", repo_dir, "add", ".gitea/workflows/", ".autograde/"],
                check=True,
                capture_output=True
            )
            
            # 检查是否有更改
            result = subprocess.run(
                ["git", "-C", repo_dir, "diff", "--cached", "--quiet"],
                capture_output=True
            )
            
            if result.returncode == 0:
                return True  # 没有更改
            
            # 提交
            subprocess.run(
                ["git", "-C", repo_dir, "commit", "-m", f"Update workflow files from template (branch: {branch})"],
                check=True,
                capture_output=True
            )
            
            # 推送
            if token:
                push_url = f"http://oauth2:{token}@{gitea_url.replace('http://', '').replace('https://', '')}/{org}/{repo_name}.git"
            else:
                push_url = f"{gitea_url}/{org}/{repo_name}.git"
            
            subprocess.run(
                ["git", "-C", repo_dir, "push", push_url, branch],
                check=True,
                capture_output=True
            )
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  ⚠️ Error updating branch {branch}: {e.stderr.decode() if e.stderr else str(e)}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(description="Update workflow files in all branches of student repositories")
    parser.add_argument("--prefix", default="hw1-stu", help="Repository name prefix")
    parser.add_argument("--template-dir", required=True, help="Template repository directory")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    parser.add_argument("--org", default=os.getenv("ORGANIZATION", "course-test"))
    parser.add_argument("--repo", help="Update specific repository only")
    parser.add_argument("--branch", help="Update specific branch only (requires --repo)")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    template_workflow_dir = os.path.join(args.template_dir, ".gitea", "workflows")
    if not os.path.isdir(template_workflow_dir):
        print(f"Error: Template workflow directory not found: {template_workflow_dir}", file=sys.stderr)
        sys.exit(1)
    
    # 获取仓库列表
    if args.repo:
        repos = [args.repo]
    else:
        print(f"🔍 Searching for repositories with prefix: {args.prefix}")
        repos = get_repos(args.gitea_url, args.token, args.org, args.prefix)
        print(f"Found {len(repos)} repositories")
    
    success_count = 0
    fail_count = 0
    
    for repo_name in repos:
        print(f"\n📦 Processing {repo_name}...")
        
        # 获取分支列表
        if args.branch:
            branches = [args.branch]
        else:
            branches = get_branches(args.gitea_url, args.token, args.org, repo_name)
            if not branches:
                branches = ["main"]  # 默认分支
        
        print(f"  Found {len(branches)} branches: {', '.join(branches)}")
        
        for branch in branches:
            print(f"  📝 Updating branch: {branch}")
            if update_workflow_in_branch(args.gitea_url, args.token, args.org, repo_name, branch, template_workflow_dir):
                print(f"    ✅ Success")
                success_count += 1
            else:
                print(f"    ❌ Failed")
                fail_count += 1
    
    print(f"\n📊 Summary: {success_count} succeeded, {fail_count} failed")


if __name__ == "__main__":
    main()

