#!/bin/bash
# Gitea 自动化设置脚本

set -e

echo "=========================================="
echo "Gitea 自动化设置脚本"
echo "=========================================="

# 检查服务状态
echo ""
echo "1. 检查服务状态..."
docker compose ps

# 检查 Gitea 是否可访问
echo ""
echo "2. 检查 Gitea 可访问性..."
if curl -s -o /dev/null -w "%{http_code}" http://49.234.193.192:3000 | grep -q "200\|302"; then
    echo "✅ Gitea 可访问"
else
    echo "⚠️  Gitea 可能还未完全启动，请稍候..."
    sleep 5
fi

echo ""
echo "=========================================="
echo "下一步操作："
echo "=========================================="
echo ""
echo "1. 打开浏览器访问: http://49.234.193.192:3000"
echo ""
echo "2. 在安装页面填写以下信息："
echo ""
echo "   数据库设置："
echo "   - 数据库类型: PostgreSQL"
echo "   - 主机: db:5432"
echo "   - 用户名: gitea"
echo "   - 密码: Wshhwps000"
echo "   - 数据库名: gitea"
echo ""
echo "   一般设置："
echo "   - 站点标题: 作业提交与自动批改系统"
echo "   - 应用 URL: http://49.234.193.192:3000"
echo ""
echo "   管理员账号："
echo "   - 用户名: admin"
echo "   - 密码: Wshhwps000"
echo "   - 邮箱: hblu1985@163.com"
echo ""
echo "3. 完成安装后，按照 INITIALIZATION.md 继续配置"
echo ""
echo "=========================================="

