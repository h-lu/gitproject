#!/bin/bash
# 从 .env 文件同步配置到 runner config.yaml
# 用法: ./scripts/sync_runner_config.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"
CONFIG_FILE="$PROJECT_ROOT/data/runner/config.yaml"

if [ ! -f "$ENV_FILE" ]; then
    echo "❌ Error: .env file not found at $ENV_FILE"
    exit 1
fi

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Error: config.yaml not found at $CONFIG_FILE"
    exit 1
fi

echo "📝 Syncing configuration from .env to runner config.yaml..."

# 从 .env 读取配置
source "$ENV_FILE"

# 使用 sed 更新 config.yaml 中的值
# 注意：这需要 envs 部分已经存在这些键

# 更新 EXTERNAL_GITEA_HOST
if [ -n "$EXTERNAL_GITEA_HOST" ]; then
    sed -i '' "s|EXTERNAL_GITEA_HOST:.*|EXTERNAL_GITEA_HOST: $EXTERNAL_GITEA_HOST|g" "$CONFIG_FILE"
    echo "  ✓ EXTERNAL_GITEA_HOST: $EXTERNAL_GITEA_HOST"
fi

# 更新 RUNNER_TESTS_USERNAME
if [ -n "$RUNNER_TESTS_USERNAME" ]; then
    sed -i '' "s|RUNNER_TESTS_USERNAME:.*|RUNNER_TESTS_USERNAME: $RUNNER_TESTS_USERNAME|g" "$CONFIG_FILE"
    echo "  ✓ RUNNER_TESTS_USERNAME: $RUNNER_TESTS_USERNAME"
fi

# 更新 RUNNER_TESTS_TOKEN
if [ -n "$RUNNER_TESTS_TOKEN" ]; then
    sed -i '' "s|RUNNER_TESTS_TOKEN:.*|RUNNER_TESTS_TOKEN: $RUNNER_TESTS_TOKEN|g" "$CONFIG_FILE"
    echo "  ✓ RUNNER_TESTS_TOKEN: [REDACTED]"
fi

# 更新 LLM_API_KEY
if [ -n "$LLM_API_KEY" ]; then
    sed -i '' "s|LLM_API_KEY:.*|LLM_API_KEY: $LLM_API_KEY|g" "$CONFIG_FILE"
    echo "  ✓ LLM_API_KEY: [REDACTED]"
fi

# 更新 LLM_API_URL
if [ -n "$LLM_API_URL" ]; then
    # 需要转义 URL 中的特殊字符
    ESCAPED_URL=$(echo "$LLM_API_URL" | sed 's/[\/&]/\\&/g')
    sed -i '' "s|LLM_API_URL:.*|LLM_API_URL: $LLM_API_URL|g" "$CONFIG_FILE"
    echo "  ✓ LLM_API_URL: $LLM_API_URL"
fi

# 更新 LLM_MODEL
if [ -n "$LLM_MODEL" ]; then
    sed -i '' "s|LLM_MODEL:.*|LLM_MODEL: $LLM_MODEL|g" "$CONFIG_FILE"
    echo "  ✓ LLM_MODEL: $LLM_MODEL"
fi

echo ""
echo "✅ Configuration synced successfully!"
echo ""
echo "⚠️  Remember to restart the runner for changes to take effect:"
echo "   cd $PROJECT_ROOT && docker-compose restart runner"
