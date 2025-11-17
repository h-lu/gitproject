#!/usr/bin/env python3
"""
成绩收集器

从 metadata 仓库中收集所有学生的成绩，生成汇总 CSV
"""

import os
import sys
import argparse
import requests
import csv
import json
import base64
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

load_dotenv()


def detect_host(server_url: str, external_host: str | None) -> str:
    """检测 Gitea 主机地址"""
    parsed = urlparse(server_url)
    raw_host = parsed.netloc or parsed.path.split("/")[0]
    host = raw_host
    if raw_host.lower().startswith("gitea"):
        host = external_host or "49.234.193.192:3000"
    return host


def list_metadata_files(gitea_url, token, metadata_repo, branch="main", path="records"):
    """
    列出 metadata 仓库中指定路径下的所有文件
    
    Parameters
    ----------
    gitea_url : str
        Gitea 服务器 URL
    token : str
        Gitea API Token
    metadata_repo : str
        metadata 仓库名称（格式：owner/repo）
    branch : str
        分支名称
    path : str
        要列出的路径
    
    Returns
    -------
    list
        文件信息列表，每个元素包含 path, sha, type 等
    """
    try:
        owner, repo_name = metadata_repo.split("/", 1)
    except ValueError:
        print(f"Error: Invalid metadata repo format: {metadata_repo}", file=sys.stderr)
        print(f"Expected format: owner/repo", file=sys.stderr)
        return []
    
    # 检测主机地址
    external_host = os.getenv("EXTERNAL_GITEA_HOST")
    host = detect_host(gitea_url, external_host)
    
    api_url = f"http://{host}/api/v1/repos/{owner}/{repo_name}/contents/{path}"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "ref": branch
    }
    
    all_files = []
    
    def traverse_directory(current_path):
        """递归遍历目录"""
        current_api_url = f"http://{host}/api/v1/repos/{owner}/{repo_name}/contents/{current_path}"
        
        try:
            response = requests.get(current_api_url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            items = response.json()
            
            # 如果返回的是单个文件而不是列表
            if isinstance(items, dict):
                items = [items]
            
            for item in items:
                if item.get("type") == "dir":
                    # 递归遍历子目录
                    traverse_directory(item["path"])
                elif item.get("type") == "file" and item["path"].endswith(".json"):
                    # 只收集 JSON 文件
                    all_files.append(item)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # 目录不存在，忽略
                return
            else:
                print(f"Error listing {current_path}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"Error traversing {current_path}: {e}", file=sys.stderr)
    
    traverse_directory(path)
    return all_files


def download_metadata_file(gitea_url, token, metadata_repo, file_path, branch="main"):
    """
    下载并解析 metadata JSON 文件
    
    Parameters
    ----------
    gitea_url : str
        Gitea 服务器 URL
    token : str
        Gitea API Token
    metadata_repo : str
        metadata 仓库名称（格式：owner/repo）
    file_path : str
        文件路径
    branch : str
        分支名称
    
    Returns
    -------
    dict or None
        解析后的 metadata JSON，如果失败则返回 None
    """
    try:
        owner, repo_name = metadata_repo.split("/", 1)
    except ValueError:
        return None
    
    # 检测主机地址
    external_host = os.getenv("EXTERNAL_GITEA_HOST")
    host = detect_host(gitea_url, external_host)
    
    api_url = f"http://{host}/api/v1/repos/{owner}/{repo_name}/contents/{file_path}"
    
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    params = {
        "ref": branch
    }
    
    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        file_info = response.json()
        
        # 解码 base64 内容
        content = file_info.get("content", "")
        # 移除可能的换行符
        content = content.replace("\n", "")
        decoded_content = base64.b64decode(content).decode("utf-8")
        
        # 解析 JSON
        metadata = json.loads(decoded_content)
        return metadata
    except Exception as e:
        print(f"Error downloading {file_path}: {e}", file=sys.stderr)
        return None


def extract_student_repo_from_path(file_path):
    """
    从文件路径提取学生仓库名称
    
    路径格式：records/{org}__{repo}/{workflow}_{run_id}_{commit_sha}.json
    例如：records/course-test__hw1-stu_sit001/grade_123_abc1234.json
    
    Returns
    -------
    tuple
        (student_repo, workflow_type) 或 (None, None)
    """
    try:
        # 移除 records/ 前缀
        if file_path.startswith("records/"):
            file_path = file_path[8:]
        
        # 分割路径
        parts = file_path.split("/")
        if len(parts) < 2:
            return None, None
        
        student_safe = parts[0]  # course-test__hw1-stu_sit001
        filename = parts[1]  # grade_123_abc1234.json
        
        # 恢复学生仓库名称
        student_repo = student_safe.replace("__", "/")
        
        # 提取 workflow 类型（文件名第一部分）
        workflow_type = filename.split("_")[0]
        
        return student_repo, workflow_type
    except Exception as e:
        print(f"Error extracting student repo from path {file_path}: {e}", file=sys.stderr)
        return None, None


def merge_components(components_list):
    """
    合并多个 metadata 的 components，按 type 去重（保留最新的）
    
    Parameters
    ----------
    components_list : list
        多个 components 列表的列表
    
    Returns
    -------
    list
        合并后的 components
    """
    component_dict = {}  # {type: component}
    
    # 按时间戳排序（最新的在前）
    # 这里简化处理，直接按顺序合并，后面的会覆盖前面的
    for components in components_list:
        for comp in components:
            comp_type = comp.get("type", "unknown")
            # 对于同一类型，保留最新的（后面覆盖前面）
            component_dict[comp_type] = comp
    
    return list(component_dict.values())


def main():
    parser = argparse.ArgumentParser(description="Collect grades from metadata repository")
    parser.add_argument("--output", default="grades.csv", help="Output CSV file")
    parser.add_argument("--metadata-repo", default=os.getenv("METADATA_REPO", "course-test/hw1-metadata"), 
                       help="Metadata repository (owner/repo)")
    parser.add_argument("--metadata-branch", default=os.getenv("METADATA_BRANCH", "main"),
                       help="Metadata repository branch")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    parser.add_argument("--prefix", default="hw1-stu", help="Student repository name prefix (for filtering)")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        print("Hint: Set it via --token or GITEA_ADMIN_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)
    
    print(f"📦 Collecting grades from metadata repository: {args.metadata_repo}")
    print(f"   Branch: {args.metadata_branch}")
    print(f"   Gitea URL: {args.gitea_url}")
    
    # 列出所有 metadata 文件
    print("\n🔍 Scanning metadata files...")
    metadata_files = list_metadata_files(
        args.gitea_url, 
        args.token, 
        args.metadata_repo,
        args.metadata_branch
    )
    
    print(f"   Found {len(metadata_files)} metadata files")
    
    if len(metadata_files) == 0:
        print("⚠️  No metadata files found", file=sys.stderr)
        print(f"   Hint: Check if metadata repository exists and contains files in 'records/' directory", file=sys.stderr)
        # 创建空 CSV
        fieldnames = ["student_id", "repo", "status", "score", "max_score", "timestamp", "component_summary", "components"]
        with open(args.output, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
        print(f"\nEmpty CSV created: {args.output}")
        return
    
    # 按学生分组收集成绩
    student_grades = defaultdict(lambda: {
        "student_id": None,
        "repo": None,
        "components": [],
        "timestamps": [],
        "status": "no_grade"
    })
    
    print("\n📥 Downloading and parsing metadata files...")
    processed = 0
    for file_info in metadata_files:
        file_path = file_info["path"]
        
        # 提取学生仓库信息
        student_repo, workflow_type = extract_student_repo_from_path(file_path)
        if not student_repo:
            continue
        
        # 过滤：只处理匹配前缀的学生仓库
        if args.prefix and not student_repo.endswith(args.prefix.split("_")[0] + "_"):
            # 检查仓库名是否包含前缀（例如 hw1-stu_sit001）
            repo_name = student_repo.split("/")[-1] if "/" in student_repo else student_repo
            if not repo_name.startswith(args.prefix):
                continue
        
        # 下载并解析 metadata
        metadata = download_metadata_file(
            args.gitea_url,
            args.token,
            args.metadata_repo,
            file_path,
            args.metadata_branch
        )
        
        if not metadata:
            continue
        
        processed += 1
        
        # 提取学生信息
        student_id = metadata.get("student_id")
        if not student_id:
            # 从仓库名提取
            repo_name = student_repo.split("/")[-1] if "/" in student_repo else student_repo
            if repo_name.startswith(args.prefix):
                student_id = repo_name[len(args.prefix) + 1:]
            else:
                student_id = repo_name
        
        # 更新学生成绩信息
        if student_grades[student_repo]["student_id"] is None:
            student_grades[student_repo]["student_id"] = student_id
        if student_grades[student_repo]["repo"] is None:
            student_grades[student_repo]["repo"] = student_repo.split("/")[-1] if "/" in student_repo else student_repo
        
        # 合并 components
        components = metadata.get("components", [])
        if components:
            student_grades[student_repo]["components"].append(components)
        
        # 记录时间戳
        timestamp = metadata.get("timestamp")
        if timestamp:
            student_grades[student_repo]["timestamps"].append(timestamp)
        
        if processed % 10 == 0:
            print(f"   Processed {processed}/{len(metadata_files)} files...", end="\r")
    
    print(f"\n   ✅ Processed {processed} metadata files")
    
    # 生成成绩汇总
    print("\n📊 Generating grade summary...")
    grades = []
    
    for student_repo, grade_info in student_grades.items():
        # 合并所有 components
        all_components = merge_components(grade_info["components"])
        
        if all_components:
            # 计算总分
            total_score = sum(c.get("score", 0) for c in all_components)
            total_max_score = sum(c.get("max_score", 0) for c in all_components)
            status = "graded"
        else:
            total_score = None
            total_max_score = None
            status = "no_grade"
        
        # 获取最新时间戳
        timestamps = grade_info["timestamps"]
        latest_timestamp = max(timestamps) if timestamps else None
        
        # 生成 component 摘要
        component_summary = ""
        if all_components:
            component_list = []
            for comp in all_components:
                comp_type = comp.get("type", "unknown")
                comp_score = comp.get("score", 0)
                comp_max = comp.get("max_score", 0)
                component_list.append(f"{comp_type}:{comp_score}/{comp_max}")
            component_summary = " | ".join(component_list)
        
        student_id = grade_info["student_id"] or grade_info["repo"]
        repo_name = grade_info["repo"]
        
        if status == "graded":
            print(f"   ✅ {student_id}: {total_score}/{total_max_score} [{component_summary}]")
        else:
            print(f"   ⏳ {student_id}: No grade found")
        
        grades.append({
            "student_id": student_id,
            "repo": repo_name,
            "status": status,
            "score": total_score,
            "max_score": total_max_score,
            "timestamp": latest_timestamp,
            "component_summary": component_summary,
            "components": json.dumps(all_components, ensure_ascii=False) if all_components else None
        })
    
    # 按学号排序
    grades.sort(key=lambda x: x["student_id"] or "")
    
    # 写入 CSV
    fieldnames = ["student_id", "repo", "status", "score", "max_score", "timestamp", "component_summary", "components"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if grades:
            writer.writerows(grades)
    
    graded_count = sum(1 for g in grades if g["status"] == "graded")
    print(f"\n✅ Grades saved to {args.output}")
    print(f"   Total students: {len(grades)}")
    print(f"   Graded: {graded_count}")
    print(f"   Not graded: {len(grades) - graded_count}")


if __name__ == "__main__":
    main()
