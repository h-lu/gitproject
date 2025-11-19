#!/usr/bin/env python3
"""
批量创建 Gitea 用户账号

用法:
    python scripts/create_users.py --students scripts/students.txt
    python scripts/create_users.py --students scripts/students.txt --password mypass123
"""

import os
import sys
import argparse
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def create_user(gitea_url, token, username, password, email=None, full_name=None):
    """
    创建 Gitea 用户
    
    Parameters
    ----------
    gitea_url : str
        Gitea 服务器 URL
    token : str
        Gitea 管理员 Token
    username : str
        用户名
    password : str
        密码
    email : str, optional
        邮箱（如果不提供，自动生成）
    full_name : str, optional
        全名
    """
    # 如果没有提供邮箱，自动生成
    if not email:
        # 使用 .local 顶级域名（RFC 6762 保留用于本地网络）
        # 这是一个有效且不会与真实域名冲突的测试域名
        email = f"{username}@gitea.local"
    
    # 如果没有提供全名，使用用户名
    if not full_name:
        full_name = username
    
    api_url = f"{gitea_url}/api/v1/admin/users"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "username": username,
        "email": email,
        "password": password,
        "full_name": full_name,
        "login_name": username,
        "send_notify": False,  # 不发送通知邮件
        "must_change_password": False  # 不强制修改密码
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_detail = ""
        try:
            error_data = response.json()
            error_detail = error_data.get("message", "")
        except:
            pass
        
        if response.status_code == 422:
            if "already exists" in error_detail.lower() or "already exists" in str(e).lower():
                return {"error": "user_exists", "message": "用户已存在"}
        
        print(f"Error creating user {username}: {e}", file=sys.stderr)
        if error_detail:
            print(f"  Detail: {error_detail}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error creating user {username}: {e}", file=sys.stderr)
        return None


def read_student_list(file_path):
    """
    从文件读取学生列表
    
    文件格式：
    - 每行一个用户名
    - 或 "用户名,邮箱" 格式
    - 或 "用户名,邮箱,全名" 格式
    """
    students = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            
            # 跳过空行和注释
            if not line or line.startswith("#"):
                continue
            
            parts = [p.strip() for p in line.split(",")]
            
            if len(parts) == 1:
                # 只有用户名
                username = parts[0]
                email = None
                full_name = None
            elif len(parts) == 2:
                # 用户名,邮箱
                username, email = parts
                full_name = None
            elif len(parts) >= 3:
                # 用户名,邮箱,全名
                username, email, full_name = parts[0], parts[1], parts[2]
            else:
                print(f"Warning: Invalid format at line {line_num}: {line}", file=sys.stderr)
                continue
            
            students.append((username, email, full_name))
    
    return students


def main():
    parser = argparse.ArgumentParser(
        description="批量创建 Gitea 用户账号",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认密码 12345678
  python scripts/create_users.py --students scripts/students.txt
  
  # 指定密码
  python scripts/create_users.py --students scripts/students.txt --password mypass123
  
  # 试运行
  python scripts/create_users.py --students scripts/students.txt --dry-run

文件格式:
  sit001
  sit002
  sit003
  
  或者带邮箱:
  sit001,sit001@school.edu
  sit002,sit002@school.edu
  
  或者带邮箱和全名:
  sit001,sit001@school.edu,张三
  sit002,sit002@school.edu,李四
        """
    )
    
    parser.add_argument("--students", required=True, help="学生列表文件路径")
    parser.add_argument("--password", default="12345678", help="新用户的默认密码")
    parser.add_argument("--output", help="账号信息输出文件路径 (默认: user_accounts.txt)")
    parser.add_argument("--dry-run", action="store_true", help="试运行模式，不实际创建用户")
    parser.add_argument("--skip-existing", action="store_true", help="跳过已存在的用户")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        print("提示: 需要管理员 Token 才能创建用户", file=sys.stderr)
        sys.exit(1)
    
    # 检查文件是否存在
    if not Path(args.students).exists():
        print(f"Error: File not found: {args.students}", file=sys.stderr)
        sys.exit(1)
    
    print(f"📝 读取学生列表...")
    students = read_student_list(args.students)
    print(f"   找到 {len(students)} 个用户")
    print()
    
    if args.dry_run:
        print("🧪 试运行模式 - 不会实际创建用户")
        print()
        for username, email, full_name in students:
            display_email = email if email else f"{username}@example.com"
            display_name = full_name if full_name else username
            print(f"[DRY RUN] 将创建用户: {username}")
            print(f"          邮箱: {display_email}")
            print(f"          全名: {display_name}")
            print(f"          密码: {args.password}")
            print()
        print(f"✅ 试运行完成，共 {len(students)} 个用户将被创建")
        return
    
    print(f"👥 开始创建用户...")
    print(f"   Gitea: {args.gitea_url}")
    print(f"   密码: {args.password}")
    print()
    
    success_count = 0
    skip_count = 0
    fail_count = 0
    
    for username, email, full_name in students:
        display_email = email if email else f"{username}@example.com"
        print(f"创建用户 {username} ({display_email})... ", end="", flush=True)
        
        result = create_user(
            args.gitea_url, 
            args.token, 
            username, 
            args.password, 
            email, 
            full_name
        )
        
        if result is None:
            fail_count += 1
            print("❌ 失败")
        elif isinstance(result, dict) and result.get("error") == "user_exists":
            if args.skip_existing:
                skip_count += 1
                print("⏭️  已存在（跳过）")
            else:
                fail_count += 1
                print("❌ 用户已存在")
        else:
            success_count += 1
            user_id = result.get("id", "?")
            print(f"✅ 成功 (ID: {user_id})")
    
    print()
    print(f"✅ 完成！")
    print(f"   成功: {success_count}")
    if skip_count > 0:
        print(f"   跳过: {skip_count}")
    print(f"   失败: {fail_count}")
    
    if fail_count > 0:
        print()
        print("⚠️  失败可能的原因：")
        print("   1. Token 权限不足（需要管理员权限）")
        print("   2. 用户名或邮箱已存在")
        print("   3. 用户名或邮箱格式不合法")
        print("   4. 密码不符合安全要求")
    
    
    # 输出账号信息到文件
    if args.output:
        output_file = args.output
    else:
        # 默认放在学生文件所在目录
        students_dir = os.path.dirname(args.students) or "."
        output_file = os.path.join(students_dir, "user_accounts.txt")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Gitea 用户账号信息\n")
        f.write(f"# 生成时间: {__import__('datetime').datetime.now()}\n")
        f.write(f"# Gitea URL: {args.gitea_url}\n")
        f.write("\n")
        f.write("用户名\t密码\t邮箱\n")
        f.write("-" * 60 + "\n")
        for username, email, full_name in students:
            display_email = email if email else f"{username}@gitea.local"
            f.write(f"{username}\t{args.password}\t{display_email}\n")
    
    print()
    print(f"📄 账号信息已保存到: {output_file}")
    print(f"   ⚠️  请妥善保管此文件，不要提交到 Git！")


if __name__ == "__main__":
    main()

