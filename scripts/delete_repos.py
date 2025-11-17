#!/usr/bin/env python3
"""
批量删除学生作业仓库

用法:
    python scripts/delete_repos.py --prefix hw1-stu
    python scripts/delete_repos.py --prefix hw1-stu --force
"""

import os
import sys
import argparse
import requests
from dotenv import load_dotenv

load_dotenv()


def list_repos(gitea_url, token, org, prefix):
    """
    列出组织下所有匹配前缀的仓库
    """
    api_url = f"{gitea_url}/api/v1/orgs/{org}/repos"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "limit": 100,
        "page": 1
    }
    
    all_repos = []
    
    while True:
        try:
            response = requests.get(api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            repos = response.json()
            if not repos:
                break
            
            # 过滤匹配前缀的仓库
            matching_repos = [r for r in repos if r["name"].startswith(prefix)]
            all_repos.extend(matching_repos)
            
            params["page"] += 1
            
            # 如果返回数量少于 limit，说明已经是最后一页
            if len(repos) < params["limit"]:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"Error listing repositories: {e}", file=sys.stderr)
            return []
    
    return all_repos


def delete_repo(gitea_url, token, org, repo_name):
    """
    删除指定仓库
    """
    api_url = f"{gitea_url}/api/v1/repos/{org}/{repo_name}"
    
    headers = {
        "Authorization": f"token {token}"
    }
    
    try:
        response = requests.delete(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Error deleting repo {repo_name}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error deleting repo {repo_name}: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(
        description="批量删除学生作业仓库",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/delete_repos.py --prefix hw1-stu
  python scripts/delete_repos.py --prefix hw1-stu --force
  python scripts/delete_repos.py --prefix hw2-stu --dry-run
        """
    )
    
    parser.add_argument("--prefix", default="hw1-stu", help="仓库名前缀（默认: hw1-stu）")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    parser.add_argument("--org", default=os.getenv("ORGANIZATION", "course-test"))
    parser.add_argument("--force", action="store_true", help="跳过确认提示")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式（不实际删除）")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        sys.exit(1)
    
    print(f"🔍 正在查找仓库...")
    print(f"   Gitea: {args.gitea_url}")
    print(f"   组织: {args.org}")
    print(f"   前缀: {args.prefix}")
    print()
    
    # 获取仓库列表
    repos = list_repos(args.gitea_url, args.token, args.org, args.prefix)
    
    if not repos:
        print("✅ 没有找到匹配的仓库")
        return
    
    # 显示找到的仓库
    print(f"📋 找到以下仓库：")
    for repo in repos:
        private_flag = "🔒" if repo["private"] else "🌐"
        print(f"   {private_flag} {repo['name']}")
    
    print()
    print(f"📊 共 {len(repos)} 个仓库")
    print()
    
    # 确认删除
    if not args.force and not args.dry_run:
        print("⚠️  警告：此操作不可逆！")
        print("⚠️  所有代码、Issues、PRs 都将被永久删除！")
        print()
        confirm = input("确认删除？请输入 'DELETE' 继续，或按 Ctrl+C 取消: ")
        
        if confirm != "DELETE":
            print("❌ 已取消操作")
            sys.exit(0)
    
    if args.dry_run:
        print("🧪 试运行模式 - 不会实际删除仓库")
        print()
        for repo in repos:
            print(f"[DRY RUN] 将删除: {repo['name']}")
        print()
        print(f"✅ 试运行完成，共 {len(repos)} 个仓库将被删除")
        return
    
    print()
    print("🗑️  开始删除...")
    print()
    
    success_count = 0
    fail_count = 0
    
    for repo in repos:
        repo_name = repo["name"]
        print(f"删除 {repo_name}... ", end="", flush=True)
        
        if delete_repo(args.gitea_url, args.token, args.org, repo_name):
            success_count += 1
            print("✅ 成功")
        else:
            fail_count += 1
            print("❌ 失败")
    
    print()
    print(f"✅ 完成！成功: {success_count}, 失败: {fail_count}")
    
    if fail_count > 0:
        print()
        print("⚠️  失败可能的原因：")
        print("   1. Token 权限不足（需要 delete:repository 权限）")
        print("   2. 仓库不存在")
        print("   3. 网络错误")


if __name__ == "__main__":
    main()

