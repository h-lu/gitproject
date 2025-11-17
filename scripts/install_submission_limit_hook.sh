#!/usr/bin/env bash
#
# 将限制提交次数的 pre-receive 钩子安装到所有学生仓库。
#

set -euo pipefail

ROOT_DIR="/home/ubuntu/Documents/GitProject"
REPO_DIR="${ROOT_DIR}/data/gitea/git/repositories/course-test"
HOST_HOOK_SRC="${ROOT_DIR}/scripts/limit_submission_hook.sh"
CONTAINER_HOOK_DIR="${ROOT_DIR}/data/gitea/custom_hooks"
CONTAINER_HOOK_SRC="${CONTAINER_HOOK_DIR}/limit_submission_hook.sh"
HOOK_ENTRY="/data/custom_hooks/limit_submission_hook.sh"
TARGET_REPOS=()

if [[ ! -x "${HOST_HOOK_SRC}" ]]; then
  echo "Hook script not found or not executable: ${HOST_HOOK_SRC}" >&2
  exit 1
fi

mkdir -p "${CONTAINER_HOOK_DIR}"
cp "${HOST_HOOK_SRC}" "${CONTAINER_HOOK_SRC}"
chmod +x "${CONTAINER_HOOK_SRC}"

if [[ $# -gt 0 ]]; then
  TARGET_REPOS=("$@")
else
  mapfile -t TARGET_REPOS < <(cd "${REPO_DIR}" && find . -maxdepth 1 -type d -name 'hw1-stu_*.git' -printf '%f\n')
fi

if [[ ${#TARGET_REPOS[@]} -eq 0 ]]; then
  echo "No student repositories found." >&2
  exit 0
fi

for repo in "${TARGET_REPOS[@]}"; do
  REPO_PATH="${REPO_DIR}/${repo}"
  HOOK_DIR="${REPO_PATH}/hooks/pre-receive.d"
  HOOK_FILE="${HOOK_DIR}/limit_submissions"

  if [[ ! -d "${HOOK_DIR}" ]]; then
    echo "Skipping ${repo}: ${HOOK_DIR} not found" >&2
    continue
  fi

  cat > "${HOOK_FILE}" <<EOF
#!/usr/bin/env bash
exec "${HOOK_ENTRY}" "\$@"
EOF
  chmod +x "${HOOK_FILE}"
  echo "Installed submission limit hook for ${repo}"
done

echo "Done."


