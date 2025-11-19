#!/usr/bin/env python3
"""
成绩收集器

从 metadata 仓库中收集所有学生的成绩，生成汇总 CSV
支持多课程/多作业模式
"""

import os
import sys
from typing import Optional
import argparse
import requests
import csv
import json
import base64
import yaml
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

load_dotenv()


def load_course_config(course_dir):
    config_path = Path(course_dir) / "course_config.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"Course config not found: {config_path}")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def detect_host(server_url: str, external_host: Optional[str]) -> str:
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
    Path format: {assignment_id}/{student_repo}/{filename}
    """
    try:
        # 移除 records/ 前缀 (兼容旧格式)
        if file_path.startswith("records/"):
            file_path = file_path[8:]
            parts = file_path.split("/")
            if len(parts) >= 2:
                student_safe = parts[0]
                filename = parts[1]
                return student_safe.replace("__", "/"), filename.split("_")[0]
        
        # 新格式: hw1/hw1-stu_20250001/grade_...json
        parts = file_path.split("/")
        if len(parts) >= 3:
            # parts[0] is assignment_id (e.g. hw1)
            student_repo = parts[1]  # hw1-stu_20250001
            filename = parts[-1]     # grade_...json
            
            # 提取 workflow 类型（文件名第一部分）
            workflow_type = filename.split("_")[0]
            
            return student_repo, workflow_type
            
        return None, None
    except Exception as e:
        print(f"Error extracting student repo from path {file_path}: {e}", file=sys.stderr)
        return None, None


def merge_components(components_list):
    """
    合并多个 metadata 的 components，按 type 去重（保留最新的）
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
    
    # Required arguments
    parser.add_argument("--course", required=True, help="Path to course directory (e.g., courses/CS101)")
    parser.add_argument("--assignment", required=True, help="Assignment ID (e.g., hw1)")
    
    parser.add_argument("--output", default="grades.csv", help="Output CSV file")
    
    # Optional/Override arguments
    parser.add_argument("--metadata-repo", help="Metadata repository (owner/repo) - auto-inferred if not specified")
    parser.add_argument("--metadata-branch", default=os.getenv("METADATA_BRANCH", "main"),
                       help="Metadata repository branch")
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_URL", "http://localhost:3000"))
    parser.add_argument("--token", default=os.getenv("GITEA_ADMIN_TOKEN", ""))
    parser.add_argument("--prefix", help="Student repository name prefix (for filtering) - auto-inferred if not specified")
    
    args = parser.parse_args()
    
    if not args.token:
        print("Error: GITEA_ADMIN_TOKEN not set", file=sys.stderr)
        print("Hint: Set it via --token or GITEA_ADMIN_TOKEN environment variable", file=sys.stderr)
        sys.exit(1)
    
    print(f"Collecting grades: {args.course} / {args.assignment}")
    course_config = load_course_config(args.course)
    org = course_config.get("organization")
    if not org:
        print("Error: 'organization' not defined in course config", file=sys.stderr)
        sys.exit(1)
        
    # Infer metadata repo and prefix
    # Default to course-metadata, but allow override
    metadata_repo = args.metadata_repo or f"{org}/course-metadata"
    repo_prefix = args.prefix or f"{args.assignment}-stu"

    print(f"📦 Collecting grades from metadata repository: {metadata_repo}")
    print(f"   Branch: {args.metadata_branch}")
    print(f"   Gitea URL: {args.gitea_url}")
    print(f"   Prefix Filter: {repo_prefix}")
    print(f"   Path: {args.assignment}/")
    
    # 列出所有 metadata 文件
    print("\n🔍 Scanning metadata files...")
    metadata_files = list_metadata_files(
        args.gitea_url, 
        args.token, 
        metadata_repo,
        args.metadata_branch,
        path=args.assignment
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
        if repo_prefix and not student_repo.endswith(repo_prefix.split("_")[0] + "_"):
            # 检查仓库名是否包含前缀
            repo_name = student_repo.split("/")[-1] if "/" in student_repo else student_repo
            if not repo_name.startswith(repo_prefix):
                continue
        
        # 下载并解析 metadata
        metadata = download_metadata_file(
            args.gitea_url,
            args.token,
            metadata_repo,
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
            if repo_name.startswith(repo_prefix):
                student_id = repo_name[len(repo_prefix) + 1:]
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
