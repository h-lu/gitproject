# 客观题题目

本目录包含作业的客观题（选择题、判断题、多选题、填空题）。

## 📁 文件说明

### 题目文件

- **`mc_questions.md`**: 单选题题目
- **`tf_questions.md`**: 判断题题目
- **`ms_questions.md`**: 多选题题目
- **`fb_questions.md`**: 填空题题目
- **`standard_answers.json`**: 标准答案（学生不可见，仅用于评分）

### 答题文件

学生答案应提交到 `objective_answers/` 目录，详见该目录的 README。

## 📋 题型说明

### 1. 单选题（Multiple Choice）

- **题号格式**: MC1, MC2, MC3, ...
- **答案格式**: 单个选项字母（A/B/C/D）
- **示例**: `"MC1": "A"`

### 2. 判断题（True/False）

- **题号格式**: TF1, TF2, TF3, ...
- **答案格式**: 布尔值（true/false）
- **示例**: `"TF1": true`

### 3. 多选题（Multiple Select）

- **题号格式**: MS1, MS2, MS3, ...
- **答案格式**: 选项字母数组（["A", "B", "C"]）
- **评分规则**: 必须完全正确才得分（选多、选少、选错都不得分）
- **示例**: `"MS1": ["A", "B", "C"]`

### 4. 填空题（Fill in the Blank）

- **题号格式**: FB1, FB2, FB3, ...
- **答案格式**: 
  - 单个空: 字符串 `"答案"`
  - 多个空: 数组 `["答案1", "答案2"]`
- **评分规则**: 
  - 不区分大小写
  - 自动去除首尾空格
  - 多空题必须顺序和内容都完全正确
- **示例**: 
  - `"FB1": "1 / (1 + e^(-z))"`
  - `"FB3": ["训练误差", "测试误差"]`

## 🎯 题目内容

### 单选题（5 道）
- 机器学习基础概念
- 损失函数、Sigmoid、梯度下降
- 特征标准化、算法分类

### 判断题（5 道）
- 逻辑回归、权重初始化
- 梯度下降目标、学习率
- 特征标准化作用

### 多选题（3 道）
- 正则化方法
- 梯度下降算法
- 模型泛化能力

### 填空题（5 道）
- Sigmoid 函数公式
- 梯度下降更新公式
- 训练误差与测试误差
- L1/L2 正则化特点
- Precision/Recall 公式

## ⚙️ 评分说明

### 自动评分

- 所有客观题由自动评分系统评分
- 评分脚本：`.autograde/objective_grade.py`
- 评分触发：提交 PR 后自动运行

### 评分规则

| 题型 | 评分规则 | 部分分 |
|------|---------|-------|
| 单选题 | 选项正确得分 | 无 |
| 判断题 | 判断正确得分 | 无 |
| 多选题 | 完全正确得分 | 无 |
| 填空题 | 答案匹配得分 | 无 |

**注意**：
- 所有题型均为全对才得分，无部分分
- 多选题选多、选少、选错都不得分
- 填空题不区分大小写，但内容必须完全匹配

## 📝 答案格式示例

```json
{
  "MC1": "A",
  "MC2": "B",
  "TF1": true,
  "TF2": false,
  "MS1": ["A", "B", "C"],
  "MS2": ["A", "C"],
  "FB1": "答案",
  "FB2": "梯度",
  "FB3": ["答案1", "答案2"]
}
```

## 🔒 标准答案管理

**重要**：`standard_answers.json` 包含所有题目的标准答案，应该：

1. ✅ 保留在模板仓库（教师维护）
2. ❌ 不推送到学生仓库（在部署脚本中排除）
3. ✅ 通过私有测试仓库提供给 CI/CD

建议在 workflow 中动态获取：

```yaml
- name: Fetch standard answers
  env:
    TESTS_USERNAME: ${{ secrets.TESTS_USERNAME }}
    TESTS_TOKEN: ${{ secrets.TESTS_TOKEN }}
  run: |
    AUTH_HEADER=$(printf "%s:%s" "$TESTS_USERNAME" "$TESTS_TOKEN" | base64 | tr -d '\n')
    git -c http.extraHeader="Authorization: Basic ${AUTH_HEADER}" \
      clone --depth=1 http://gitea.example.com/course/hw1-tests.git /tmp/tests
    cp /tmp/tests/objective/standard_answers.json objective_questions/
```

## 🛠️ 出题建议

### 添加新题目

1. 编辑对应的 markdown 文件（mc/tf/ms/fb_questions.md）
2. 更新 `standard_answers.json`
3. 更新学生答案模板 `objective_answers/my_answers.json`

### 题号规范

- 单选题：MC1, MC2, MC3, ...
- 判断题：TF1, TF2, TF3, ...
- 多选题：MS1, MS2, MS3, ...
- 填空题：FB1, FB2, FB3, ...

### 多选题注意事项

- 明确标注"（多选）"
- 至少 2 个正确选项
- 建议 2-4 个选项中选 2-3 个

### 填空题注意事项

- 用 _____ 表示填空位置
- 多个空用明确的分隔符
- 答案要考虑多种表达方式
- 如果答案固定，建议提供格式要求

## 📊 分数配置

当前配置（可在 `assignment_config.yaml` 中修改）：

```yaml
objective:
  enabled: true
  weight: 20
  multiple_choice:
    questions: 5
    points_per_question: 2
  true_false:
    questions: 5
    points_per_question: 2
  multiple_select:
    questions: 3
    points_per_question: 2
  fill_blank:
    questions: 5
    points_per_question: 2
```

总分：5×2 + 5×2 + 3×2 + 5×2 = 36 分

## 🧪 测试评分

在模板目录下测试评分：

```bash
python3 ./.autograde/objective_grade.py \
  --answers objective_questions/standard_answers.json \
  --standard objective_questions/standard_answers.json \
  --out test_grade.json \
  --summary test_summary.md \
  --type all
```

## 📖 相关文档

- [学生答题指南](../objective_answers/README.md)
- [模板自定义指南](../TEMPLATE_CUSTOMIZATION.md)
- [客观题使用指南](../OBJECTIVE_QUESTIONS_GUIDE.md)
