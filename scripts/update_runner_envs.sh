#!/bin/bash
# 为 act_runner 配置 RUNNER_TESTS_USERNAME / RUNNER_TESTS_TOKEN，并重启 runner
# 用法：
#   bash scripts/update_runner_envs.sh <username> <token>
# 或者提前 export RUNNER_TESTS_USERNAME / RUNNER_TESTS_TOKEN 后直接运行

set -euo pipefail

CONFIG_PATH=${CONFIG_PATH:-data/runner/config.yaml}
USERNAME=${1:-${RUNNER_TESTS_USERNAME:-}}
TOKEN=${2:-${RUNNER_TESTS_TOKEN:-}}

if [ -z "${USERNAME}" ] || [ -z "${TOKEN}" ]; then
  echo "用法: CONFIG_PATH=data/runner/config.yaml \\"
  echo "      RUNNER_TESTS_USERNAME=hblu RUNNER_TESTS_TOKEN=xxx bash scripts/update_runner_envs.sh"
  echo "或:   bash scripts/update_runner_envs.sh <username> <token>"
  exit 1
fi

if docker compose version >/dev/null 2>&1; then
  DOCKER_COMPOSE_CMD=(docker compose)
elif docker-compose version >/dev/null 2>&1; then
  DOCKER_COMPOSE_CMD=(docker-compose)
else
  echo "未找到 docker compose，请先安装 Docker/Compose"
  exit 1
fi

# 如果配置文件不存在，先生成一份默认配置
if [ ! -f "${CONFIG_PATH}" ]; then
  echo "未检测到 ${CONFIG_PATH}，正在从 act_runner 生成默认配置..."
  "${DOCKER_COMPOSE_CMD[@]}" exec runner act_runner generate-config > "${CONFIG_PATH}"
fi

python3 - "${CONFIG_PATH}" "${USERNAME}" "${TOKEN}" <<'PY'
import pathlib, sys, re

config_path = pathlib.Path(sys.argv[1])
username = sys.argv[2]
token = sys.argv[3]

text = config_path.read_text()
replacement = (
    "  envs:\n"
    f"    RUNNER_TESTS_USERNAME: {username}\n"
    f"    RUNNER_TESTS_TOKEN: {token}\n"
)

pattern = re.compile(r"(  envs:\n)(?:    .*\n)*", re.MULTILINE)
new_text, count = pattern.subn(lambda m: replacement, text, count=1)
if count == 0:
    raise SystemExit("未能在 config.yaml 中找到 envs: 区块，请手动检查文件。")

config_path.write_text(new_text)
PY

echo "已写入 ${CONFIG_PATH}，正在重启 runner ..."
"${DOCKER_COMPOSE_CMD[@]}" restart runner >/dev/null
echo "✅ runner 已重启，新的环境变量将自动注入到每个 Workflow Job 中。"

