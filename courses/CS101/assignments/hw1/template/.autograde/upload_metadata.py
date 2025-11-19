#!/usr/bin/env python3
"""
Upload metadata.json to teacher-only repository via Gitea API.
"""

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


def detect_host(server_url: str, external_host: str | None) -> str:
    """Detect the Gitea host to use for API calls.
    
    If server_url uses internal name (like 'gitea'), use external_host instead.
    """
    parsed = urlparse(server_url)
    raw_host = parsed.netloc or parsed.path.split("/")[0]
    host = raw_host
    if raw_host.lower().startswith("gitea"):
        if not external_host:
            raise ValueError(
                f"Server URL uses internal name '{raw_host}' but EXTERNAL_GITEA_HOST is not set. "
                "Please configure EXTERNAL_GITEA_HOST in .env and run sync_runner_config.sh"
            )
        host = external_host
    return host


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload metadata.json to course metadata repo")
    parser.add_argument("--metadata-file", required=True)
    parser.add_argument("--metadata-repo", required=True, help="owner/repo of metadata store")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--student-repo", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--commit-sha", required=True)
    parser.add_argument("--workflow", required=True, choices=["grade", "objective", "llm"])
    parser.add_argument("--server-url", required=True)
    parser.add_argument("--external-host")
    parser.add_argument("--assignment-id", help="Assignment ID (e.g., hw1)")
    args = parser.parse_args()

    token = os.environ.get("METADATA_TOKEN")
    if not token:
        print("METADATA_TOKEN is not set", file=sys.stderr)
        return 1

    path = Path(args.metadata_file)
    if not path.is_file():
        print(f"metadata file not found: {path}", file=sys.stderr)
        return 0

    try:
        owner, repo_name = args.metadata_repo.split("/", 1)
    except ValueError:
        print(f"Invalid metadata repo: {args.metadata_repo}", file=sys.stderr)
        return 1

    # Extract student ID from student repo name
    # student repo format: hw1-stu_20250001 or hw1-stu_student1
    student_id = args.student_repo.split("/")[-1]  # Get repo name
    
    # Auto-detect assignment ID from student repo if not provided
    assignment_id = args.assignment_id
    if not assignment_id:
        # Try to extract from student_repo format: hw1-stu_xxx
        repo_name_part = args.student_repo.split("/")[-1]
        if "-stu_" in repo_name_part:
            assignment_id = repo_name_part.split("-stu_")[0]
        elif "-template" in repo_name_part:
             assignment_id = repo_name_part.split("-template")[0]
        elif "-tests" in repo_name_part:
             assignment_id = repo_name_part.split("-tests")[0]
        else:
            assignment_id = "unknown"
    
    # New path structure: {assignment_id}/{student_id}/{workflow}_{run_id}_{sha}.json
    target_path = f"{assignment_id}/{student_id}/{args.workflow}_{args.run_id}_{args.commit_sha[:7]}.json"

    host = detect_host(args.server_url, args.external_host)
    api_url = f"http://{host}/api/v1/repos/{owner}/{repo_name}/contents/{target_path}"
    message = f"Upload {args.workflow} metadata for {args.student_repo} {args.commit_sha}"

    content = base64.b64encode(path.read_bytes()).decode()
    data = json.dumps({
        "content": content,
        "message": message,
        "branch": args.branch
    }).encode()

    req = urllib.request.Request(
        api_url,
        data=data,
        headers={
            "Authorization": f"token {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            resp_body = resp.read().decode()
            print(resp_body)
    except urllib.error.HTTPError as exc:
        print(f"Metadata upload failed: {exc.status} {exc.reason}", file=sys.stderr)
        print(exc.read().decode(), file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Metadata upload failed: {exc}", file=sys.stderr)
        return 1

    print(f"✅ Metadata stored at {args.metadata_repo}:{target_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


