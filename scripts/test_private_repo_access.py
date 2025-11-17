#!/usr/bin/env python3
"""
快速验证是否能够通过 GITEA_TESTS_USERNAME / GITEA_TESTS_TOKEN 访问私有 hw1-tests 仓库。

Usage:
  python3 scripts/test_private_repo_access.py

提示：只有在 `push` / `workflow_dispatch` 事件中，Gitea 才会把这些 Secrets 注入 workflow，
因此在 PR 中若看到长度为 8 的 `********` 属于正常安全限制。
"""

import os
import sys
import subprocess
from urllib.parse import urlparse


def build_auth_url(base_url: str, org: str, repo: str, username: str, token: str) -> str:
    parsed = urlparse(base_url)
    scheme = parsed.scheme or "http"
    netloc = parsed.netloc or parsed.path
    if not netloc:
        raise ValueError(f"Invalid GITEA_URL: {base_url}")
    # 统一使用 http，方便与 Actions 中的配置保持一致
    scheme = "http"
    return f"{scheme}://{username}:{token}@{netloc}/{org}/{repo}.git"


def main() -> int:
    base_url = os.getenv("GITEA_URL", "http://49.234.193.192:3000")
    org = (
        os.getenv("GITEA_ORG")
        or os.getenv("ORGANIZATION")
        or "course-test"
    )
    repo = os.getenv("TESTS_REPO", "hw1-tests")
    username = os.getenv("GITEA_TESTS_USERNAME")
    token = os.getenv("GITEA_TESTS_TOKEN")

    missing = [name for name, value in [
        ("GITEA_TESTS_USERNAME", username),
        ("GITEA_TESTS_TOKEN", token),
    ] if not value]

    if missing:
        print(f"❌ 缺少配置: {', '.join(missing)}", file=sys.stderr)
        print("   请先在当前 shell 中通过 export 设置上述环境变量。", file=sys.stderr)
        return 1

    auth_url = build_auth_url(base_url, org, repo, username, token)  # type: ignore[arg-type]

    print("🔐 正在测试私有仓库访问权限:")
    print(f"   仓库: {base_url.rstrip('/')}/{org}/{repo}.git")
    print(f"   使用账号: {username}")

    try:
        subprocess.run(
            ["git", "ls-remote", auth_url],
            check=True,
            capture_output=True,
        )
        print("✅ 访问成功，可以在 Actions 中使用该凭据拉取 hw1-tests")
        return 0
    except subprocess.CalledProcessError as exc:
        print("❌ 访问失败，git 返回错误：", file=sys.stderr)
        if exc.stderr:
            print(exc.stderr.decode(), file=sys.stderr)
        else:
            print(exc, file=sys.stderr)
        return exc.returncode or 1


if __name__ == "__main__":
    sys.exit(main())

