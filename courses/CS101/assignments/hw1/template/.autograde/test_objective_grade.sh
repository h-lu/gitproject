#!/bin/bash
# 测试客观题评分脚本

set -e

echo "=== 测试客观题评分脚本 ==="

cd "$(dirname "$0")/.."

# 测试 1: 使用 JSON 格式答案
echo ""
echo "测试 1: JSON 格式答案（全对）"
python3 ./.autograde/objective_grade.py \
  --answers objective_questions/standard_answers.json \
  --standard objective_questions/standard_answers.json \
  --questions objective_questions/question_texts.json \
  --out test_grade1.json \
  --summary test_summary1.md \
  --type both

echo "分数："
python3 -c "import json; data=json.load(open('test_grade1.json')); print(f\"{data['score']}/{data['max_score']}\")"

echo ""
echo "摘要："
cat test_summary1.md

# 测试 2: 使用部分错误的答案
echo ""
echo "测试 2: 部分错误答案"
cat > test_answers2.json << 'EOF'
{
  "MC1": "A",
  "MC2": "A",
  "MC3": "C",
  "MC4": "B",
  "MC5": "C",
  "TF1": true,
  "TF2": false,
  "TF3": true,
  "TF4": true,
  "TF5": false
}
EOF

python3 ./.autograde/objective_grade.py \
  --answers test_answers2.json \
  --standard objective_questions/standard_answers.json \
  --questions objective_questions/question_texts.json \
  --out test_grade2.json \
  --summary test_summary2.md \
  --type both

echo "分数："
python3 -c "import json; data=json.load(open('test_grade2.json')); print(f\"{data['score']}/{data['max_score']}\")"

echo ""
echo "摘要："
cat test_summary2.md

# 测试 3: 只评选择题
echo ""
echo "测试 3: 只评选择题"
python3 ./.autograde/objective_grade.py \
  --answers objective_questions/standard_answers.json \
  --standard objective_questions/standard_answers.json \
  --questions objective_questions/question_texts.json \
  --out test_grade3.json \
  --summary test_summary3.md \
  --type mc

echo "分数："
python3 -c "import json; data=json.load(open('test_grade3.json')); print(f\"{data['score']}/{data['max_score']}\")"

# 测试 4: 只评判断题
echo ""
echo "测试 4: 只评判断题"
python3 ./.autograde/objective_grade.py \
  --answers objective_questions/standard_answers.json \
  --standard objective_questions/standard_answers.json \
  --questions objective_questions/question_texts.json \
  --out test_grade4.json \
  --summary test_summary4.md \
  --type tf

echo "分数："
python3 -c "import json; data=json.load(open('test_grade4.json')); print(f\"{data['score']}/{data['max_score']}\")"

# 清理测试文件
rm -f test_grade*.json test_summary*.md test_answers*.json

echo ""
echo "✅ 所有测试通过！"


