#!/bin/bash
# 快速收集成绩脚本

# 配置（使用环境变量或默认值）
GITEA_URL="${GITEA_URL:-http://49.234.193.192:3000}"
ORGANIZATION="${ORGANIZATION:-course-test}"
PREFIX="${PREFIX:-hw1-}"

# 自动加载 .env（或通过 ENV_FILE 指定其他文件）
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
    echo "♻️  加载环境变量：$ENV_FILE"
    set -a
    # shellcheck source=/dev/null
    . "$ENV_FILE"
    set +a
fi

# 检查 Token
if [ -z "$GITEA_ADMIN_TOKEN" ]; then
    echo "❌ 错误: 请设置 GITEA_ADMIN_TOKEN 环境变量"
    echo "   示例: export GITEA_ADMIN_TOKEN=你的Token"
    exit 1
fi

# 生成输出文件名（带时间戳）
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
OUTPUT="grades_${PREFIX}${TIMESTAMP}.csv"

echo "📊 开始收集成绩..."
echo "   Gitea: $GITEA_URL"
echo "   组织: $ORGANIZATION"
echo "   前缀: $PREFIX"
echo "   输出: $OUTPUT"
echo ""

# 运行收集脚本
python3 scripts/collect_grades.py \
    --gitea-url "$GITEA_URL" \
    --token "$GITEA_ADMIN_TOKEN" \
    --prefix "$PREFIX" \
    --output "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 成绩收集完成！"
    echo "   文件: $OUTPUT"
    echo ""
    echo "📈 快速统计:"
    if [ -f "$OUTPUT" ] && command -v python3 &> /dev/null; then
        python3 << PYTHON
import csv
import sys
import os

try:
    output_file = '$OUTPUT'
    if not os.path.exists(output_file):
        print("   (文件不存在)")
        sys.exit(0)
    
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    if not rows:
        print("   (无数据)")
    else:
        print(f"   总人数: {len(rows)}")
        
        # 尝试统计分数（如果有 score 列）
        scores = []
        for row in rows:
            if 'score' in row and row['score'] and row['score'].strip():
                try:
                    scores.append(float(row['score']))
                except (ValueError, TypeError):
                    pass
        
        if scores:
            print(f"   平均分: {sum(scores)/len(scores):.2f}")
            print(f"   最高分: {max(scores):.2f}")
            print(f"   最低分: {min(scores):.2f}")
        else:
            print("   (暂无分数数据)")
            
        # 显示状态统计
        statuses = {}
        for row in rows:
            status = row.get('status', 'unknown')
            statuses[status] = statuses.get(status, 0) + 1
        
        if statuses:
            print("   状态分布:")
            for status, count in sorted(statuses.items()):
                print(f"     {status}: {count}")
except Exception as e:
    print(f"   (统计失败: {e})")
PYTHON
    fi
else
    echo ""
    echo "❌ 成绩收集失败，请检查错误信息"
    exit 1
fi
