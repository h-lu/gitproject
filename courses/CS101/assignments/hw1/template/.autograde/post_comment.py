#!/usr/bin/env python3
"""
发送评论到 Gitea PR

从环境变量读取配置，发送评论到指定的 PR
支持在 Markdown 评论中嵌入 JSON 数据，便于后续结构化提取
"""

import os
import sys
import json
import requests
from datetime import datetime


def create_comment_with_metadata(summary, commit_sha, comment_type='grade', metadata=None):
    """
    创建包含元数据的评论内容
    
    Parameters
    ----------
    summary : str
        人类可读的 Markdown 格式总结
    commit_sha : str
        提交 SHA
    comment_type : str
        评论类型 ('grade', 'llm', 'combined')
    metadata : dict, optional
        结构化的成绩数据，将嵌入为 JSON
    
    Returns
    -------
    str
        完整的评论内容（Markdown + JSON）
    """
    commit_short = commit_sha[:7] if commit_sha else 'unknown'
    
    # 根据类型设置标题和图标
    if comment_type == 'llm':
        title = "🤖 LLM 简答题评分结果"
        footer = "*此评论由 Gitea Actions 自动生成（使用 DeepSeek API） | Commit: `{}`*"
    elif comment_type == 'combined':
        title = "📊 综合评分结果"
        footer = "*此评论由 Gitea Actions 自动生成 | Commit: `{}`*"
    else:
        title = "🤖 自动评分结果"
        footer = "*此评论由 Gitea Actions 自动生成 | Commit: `{}`*"
    
    # 构建评论
    parts = [
        f"## {title}",
        "",
        summary,
        ""
    ]
    
    # 如果提供了元数据，嵌入 JSON
    if metadata:
        # 确保元数据包含版本和时间戳
        if 'version' not in metadata:
            metadata['version'] = '1.0'
        if 'timestamp' not in metadata:
            metadata['timestamp'] = datetime.now().isoformat()
        
        # 使用 Markdown 代码块嵌入 JSON（更可靠，Gitea 会保留）
        # 放在评论末尾，对学生不太显眼
        json_str = json.dumps(metadata, ensure_ascii=False, indent=2)
        parts.extend([
            "",
            "---",
            "",
            "<!-- GRADE_METADATA -->",
            "```json",
            json_str,
            "```",
            ""
        ])
    
    parts.extend([
        footer.format(commit_short)
    ])
    
    return "\n".join(parts)


def main():
    # 从环境变量读取配置
    api_url = os.environ.get('API_URL', '')
    repo = os.environ.get('REPO', '')
    pr_number = os.environ.get('PR_NUMBER', '')
    token = os.environ.get('GITEA_TOKEN', '')
    summary = os.environ.get('SUMMARY', '')
    commit_sha = os.environ.get('COMMIT_SHA', '')
    comment_type = os.environ.get('COMMENT_TYPE', 'grade')
    
    # 可选：从环境变量读取 JSON 元数据
    metadata_str = os.environ.get('GRADE_METADATA', '')
    metadata = None
    if metadata_str:
        try:
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError as e:
            print(f"Warning: Failed to parse GRADE_METADATA: {e}", file=sys.stderr)
    
    # 验证必需参数
    if not all([api_url, repo, pr_number, token, summary]):
        print("Error: Missing required environment variables", file=sys.stderr)
        print(f"API_URL: {api_url}", file=sys.stderr)
        print(f"REPO: {repo}", file=sys.stderr)
        print(f"PR_NUMBER: {pr_number}", file=sys.stderr)
        print(f"GITEA_TOKEN: {'set' if token else 'not set'}", file=sys.stderr)
        print(f"SUMMARY: {'set' if summary else 'not set'}", file=sys.stderr)
        sys.exit(1)
    
    # 构建评论内容（包含元数据）
    comment_body = create_comment_with_metadata(
        summary=summary,
        commit_sha=commit_sha,
        comment_type=comment_type,
        metadata=metadata
    )
    
    # 构建 API URL
    comment_url = f"{api_url}/repos/{repo}/issues/{pr_number}/comments"
    
    # 发送请求
    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json"
    }
    
    data = {"body": comment_body}
    
    try:
        print(f"Posting comment to: {comment_url}")
        if metadata:
            print("✓ Comment includes structured metadata")
        response = requests.post(comment_url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        print("✅ Comment posted successfully to PR")
        return 0
    except requests.exceptions.Timeout:
        print("⚠️ Request timeout", file=sys.stderr)
        return 1
    except requests.exceptions.HTTPError as e:
        print(f"⚠️ HTTP error: {e}", file=sys.stderr)
        print(f"Response: {response.text}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"⚠️ Failed to post comment: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
