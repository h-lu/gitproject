#!/bin/bash
# 批量添加学生为协作者
# 用法: ./add_collaborators.sh

cd "$(dirname "$0")/.."

if [ -z "$GITEA_ADMIN_TOKEN" ]; then
    echo "错误: GITEA_ADMIN_TOKEN 未设置"
    echo "请先通过 export 设置管理员 Token"
    exit 1
fi

if [ ! -f "scripts/students.txt" ]; then
    echo "错误: scripts/students.txt 不存在"
    exit 1
fi

echo "📝 开始添加协作者..."
echo "   Gitea: $GITEA_URL"
echo "   组织: $ORGANIZATION"
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
  
  repo_name="hw1-stu_${student_id}"
  echo -n "Adding $gitea_username to $repo_name... "
  
  response=$(curl -s -w "\n%{http_code}" -X PUT \
    -H "Authorization: token $GITEA_ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"permission":"write"}' \
    "$GITEA_URL/api/v1/repos/$ORGANIZATION/$repo_name/collaborators/$gitea_username")
  
  http_code=$(echo "$response" | tail -n1)
  
  if [ "$http_code" = "204" ] || [ "$http_code" = "201" ]; then
    echo "✅ OK"
    ((success++))
  else
    echo "❌ FAILED (HTTP $http_code)"
    ((failed++))
  fi
  
done < scripts/students.txt

echo ""
echo "✅ 完成！成功: $success, 失败: $failed"

if [ $failed -gt 0 ]; then
    echo ""
    echo "⚠️  失败可能的原因："
    echo "   1. 用户名不存在（学生未注册 Gitea）"
    echo "   2. 仓库不存在"
    echo "   3. Token 权限不足"
fi

