#!/bin/bash
# 批量添加学生为协作者 - 多课程模式
# 用法: ./add_collaborators.sh -c courses/CS101 -a hw1

# 显示用法
usage() {
    echo "用法: $0 -c <course> -a <assignment>"
    echo ""
    echo "参数:"
    echo "  -c  课程路径 (例如: courses/CS101)"
    echo "  -a  作业ID (例如: hw1)"
    echo ""
    echo "示例:"
    echo "  $0 -c courses/CS101 -a hw1"
    exit 1
}

# 解析参数
COURSE=""
ASSIGNMENT=""

while getopts "c:a:h" opt; do
  case $opt in
    c) COURSE="$OPTARG" ;;
    a) ASSIGNMENT="$OPTARG" ;;
    h) usage ;;
    *) usage ;;
  esac
done

# 检查必需参数
if [ -z "$COURSE" ] || [ -z "$ASSIGNMENT" ]; then
    echo "❌ 错误: 必须指定 -c (course) 和 -a (assignment) 参数"
    usage
fi

cd "$(dirname "$0")/.."

# 自动加载 .env（如果存在）
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    echo "♻️  加载环境变量：$ENV_FILE"
    set -a
    # shellcheck source=/dev/null
    . "$ENV_FILE"
    set +a
fi

if [ -z "$GITEA_ADMIN_TOKEN" ]; then
    echo "❌ 错误: GITEA_ADMIN_TOKEN 未设置"
    echo "   请先通过 export 设置管理员 Token"
    exit 1
fi

# 检查课程配置文件
COURSE_CONFIG="$COURSE/course_config.yaml"
if [ ! -f "$COURSE_CONFIG" ]; then
    echo "❌ 错误: 课程配置文件不存在: $COURSE_CONFIG"
    exit 1
fi

# 检查学生列表
STUDENTS_FILE="$COURSE/students.txt"
if [ ! -f "$STUDENTS_FILE" ]; then
    echo "❌ 错误: 学生列表文件不存在: $STUDENTS_FILE"
    exit 1
fi

# 从配置文件读取组织名
ORGANIZATION=$(python3 -c "import yaml; print(yaml.safe_load(open('$COURSE_CONFIG'))['organization'])" 2>/dev/null)
if [ -z "$ORGANIZATION" ]; then
    echo "❌ 错误: 无法从配置文件读取 organization"
    exit 1
fi

REPO_PREFIX="${ASSIGNMENT}-stu_"

echo "📝 开始添加协作者..."
echo "   Gitea: ${GITEA_URL:-http://localhost:3000}"
echo "   组织: $ORGANIZATION"
echo "   前缀: $REPO_PREFIX"
echo ""

success=0
failed=0

while IFS=, read -r student_id gitea_username || [ -n "$student_id" ]; do
  # 跳过注释和空行
  [[ "$student_id" =~ ^#.*$ ]] && continue
  [[ -z "$student_id" ]] && continue
  
  # 如果没有提供 gitea_username，使用 student_id
  if [ -z "$gitea_username" ]; then
    gitea_username="$student_id"
  fi
  
  repo_name="${REPO_PREFIX}${student_id}"
  echo -n "Adding $gitea_username to $repo_name... "
  
  response=$(curl -s -w "\n%{http_code}" -X PUT \
    -H "Authorization: token $GITEA_ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"permission":"write"}' \
    "${GITEA_URL:-http://localhost:3000}/api/v1/repos/$ORGANIZATION/$repo_name/collaborators/$gitea_username")
  
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "204" ] || [ "$http_code" = "201" ]; then
    echo "✅ OK"
    ((success++))
  else
    echo "❌ FAILED (HTTP $http_code)"
    ((failed++))
  fi
  
done < "$STUDENTS_FILE"

echo ""
echo "✅ 完成！成功: $success, 失败: $failed"

if [ $failed -gt 0 ]; then
    echo ""
    echo "⚠️  失败可能的原因："
    echo "   1. 用户名不存在（学生未注册 Gitea）"
    echo "   2. 仓库不存在"
    echo "   3. Token 权限不足"
fi
