#!/usr/bin/env bash
#
# 该脚本由 pre-receive 钩子调用，用于限制学生 push 到 main 的次数。
# 每次 push 成功视为一次自动评分尝试，次数超过阈值后拒绝 push。
#

set -euo pipefail

MAX_SUBMISSIONS="${MAX_SUBMISSIONS:-3}"
STATE_DIR="${SUBMISSION_LIMIT_STATE_DIR:-/data/submission_limits}"

mkdir -p "${STATE_DIR}"

if [[ "${GITEA_PUSHER:-}" =~ ^(course-test|hblu)$ ]]; then
  exit 0
fi

REPO_PATH=$(cd "${GIT_DIR:-.}" && pwd)
REPO_NAME="$(basename "${REPO_PATH}")"
REPO_NAME="${REPO_NAME%.git}"

ATTEMPT_FILE="${STATE_DIR}/${REPO_NAME}.count"
LOCK_FILE="${STATE_DIR}/${REPO_NAME}.lock"

updates=()
while read -r oldrev newrev refname; do
  updates+=("$oldrev $newrev $refname")
done

needs_check=0
for entry in "${updates[@]}"; do
  read -r oldrev newrev refname <<< "${entry}"
  if [[ "${refname}" == "refs/heads/main" && "${newrev}" != "0000000000000000000000000000000000000000" ]]; then
    needs_check=1
    break
  fi
done

if [[ "${needs_check}" -eq 0 ]]; then
  exit 0
fi

exec 9> "${LOCK_FILE}"
flock 9

count=0
if [[ -f "${ATTEMPT_FILE}" ]]; then
  if ! count=$(cat "${ATTEMPT_FILE}"); then
    count=0
  fi
fi

if [[ "${count}" =~ ^[0-9]+$ ]]; then
  :
else
  count=0
fi

if (( count >= MAX_SUBMISSIONS )); then
  echo "🚫 push 被拒绝：${REPO_NAME} 已达到 ${MAX_SUBMISSIONS} 次自动评分上限。" >&2
  echo "如需额外机会，请联系教师或助教。" >&2
  exit 1
fi

echo $((count + 1)) > "${ATTEMPT_FILE}"
echo "ℹ️ 已记录第 $((count + 1)) 次自动评分尝试（上限 ${MAX_SUBMISSIONS}）" >&2

exec 9>&-
exit 0


