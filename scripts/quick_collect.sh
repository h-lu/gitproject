#!/bin/bash
# 快速收集成绩脚本 - 多课程模式

# 显示用法
usage() {
    echo "用法: $0 -c <course> -a <assignment> [-o <output>]"
    echo ""
    echo "参数:"
    echo "  -c  课程路径 (例如: courses/CS101)"
    echo "  -a  作业ID (例如: hw1)"
    echo "  -o  输出文件 (默认: grades_<assignment>_<timestamp>.csv)"
    echo ""
    echo "示例:"
    echo "  $0 -c courses/CS101 -a hw1"
    echo "  $0 -c courses/STAT202 -a hw2 -o stat_hw2_grades.csv"
    exit 1
}

# 解析参数
COURSE=""
ASSIGNMENT=""
OUTPUT=""

while getopts "c:a:o:h" opt; do
  case $opt in
    c) COURSE="$OPTARG" ;;
    a) ASSIGNMENT="$OPTARG" ;;
    o) OUTPUT="$OPTARG" ;;
    h) usage ;;
    *) usage ;;
  esac
done

# 检查必需参数
if [ -z "$COURSE" ] || [ -z "$ASSIGNMENT" ]; then
    echo "❌ 错误: 必须指定 -c (course) 和 -a (assignment) 参数"
    usage
fi

# 自动加载 .env（如果存在）
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
if [ -z "$OUTPUT" ]; then
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    OUTPUT="grades_${ASSIGNMENT}_${TIMESTAMP}.csv"
fi

echo "📊 开始收集成绩..."
echo "   课程: $COURSE"
echo "   作业: $ASSIGNMENT"
echo "   输出: $OUTPUT"
echo ""

# 运行收集脚本
python3 scripts/collect_grades.py \
    --course "$COURSE" \
    --assignment "$ASSIGNMENT" \
    --output "$OUTPUT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 成绩收集完成！"
    echo "   文件: $OUTPUT"
    echo ""
    echo "📈 快速统计:"
    if [ -f "$OUTPUT" ] && command -v python3 &> /dev/null; then
        python3 <<PYTHON
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
