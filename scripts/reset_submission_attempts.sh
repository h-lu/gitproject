#!/usr/bin/env bash
#
# 重置指定仓库的提交次数（或全部仓库）。
#

set -euo pipefail

STATE_DIR="${SUBMISSION_LIMIT_STATE_DIR:-/home/ubuntu/Documents/GitProject/data/gitea/submission_limits}"

if [[ ! -d "${STATE_DIR}" ]]; then
  echo "State directory not found: ${STATE_DIR}" >&2
  exit 1
fi

if [[ $# -gt 0 ]]; then
  targets=("$@")
else
  mapfile -t targets < <(cd "${STATE_DIR}" && ls *.count 2>/dev/null | sed 's/\.count$//')
fi

if [[ ${#targets[@]} -eq 0 ]]; then
  echo "No submission counters to reset."
  exit 0
fi

for repo in "${targets[@]}"; do
  file="${STATE_DIR}/${repo}.count"
  lock="${STATE_DIR}/${repo}.lock"
  rm -f "${file}" "${lock}"
  echo "Reset counter for ${repo}"
done

echo "Done."


