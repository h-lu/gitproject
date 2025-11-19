# 客观题使用指南

本文档说明如何在作业中使用客观题（选择题和判断题）功能。

## 📚 目录结构

```
hw1-template/
├── objective_questions/          # 题目目录（教师维护）
│   ├── mc_questions.md          # 选择题题目
│   ├── tf_questions.md          # 判断题题目
│   ├── standard_answers.json   # 标准答案（保密）
│   ├── question_texts.json     # 题目文本（机器可读）
│   └── README.md               # 题目说明
│
├── objective_answers/            # 答案目录（学生填写）
│   ├── my_answers.json         # 学生答案（JSON 格式）
│   └── README.md               # 答题说明
│
├── .autograde/                   # 评分脚本
│   ├── objective_grade.py      # 客观题评分脚本
│   └── test_objective_grade.sh # 测试脚本
│
└── .gitea/workflows/
    └── objective_grade.yml      # 客观题评分 workflow
```

## 🎯 功能特性

### 1. 支持的题型

- **选择题（Multiple Choice）**
  - 题号格式：MC1, MC2, MC3, ...
  - 答案格式：A, B, C, D（大小写不敏感）
  - 单选题，只有一个正确答案

- **判断题（True/False）**
  - 题号格式：TF1, TF2, TF3, ...
  - 答案格式：true/false（或 t/f, 1/0）
  - 布尔值判断

### 2. 评分特点

- ✅ **自动评分**：提交后自动运行评分
- ✅ **即时反馈**：评分结果发布到 PR 评论
- ✅ **完整详情**：显示每道题的对错和正确答案
- ✅ **JSON 元数据**：评分结果包含在统一的成绩格式中

### 3. 答案格式

支持两种答案格式：

**JSON 格式（推荐）**:
```json
{
  "MC1": "D",
  "MC2": "A",
  "MC3": "C",
  "TF1": true,
  "TF2": false
}
```

**文本格式**:
```
D
A
C
true
false
```

## 📝 教师使用指南

### 1. 创建题目

#### 编辑题目文件

在 `objective_questions/` 目录下：

**mc_questions.md** (选择题):
```markdown
## MC1
题目文本...

A. 选项 A  
B. 选项 B  
C. 选项 C  
D. 选项 D

**正确答案**：D
```

**tf_questions.md** (判断题):
```markdown
## TF1
判断题题目文本...

**正确答案**：True
```

#### 更新标准答案

**standard_answers.json**:
```json
{
  "MC1": "D",
  "MC2": "A",
  "MC3": "C",
  "TF1": true,
  "TF2": false
}
```

#### 更新题目文本

**question_texts.json**:
```json
{
  "MC1": "题目文本...",
  "MC2": "题目文本...",
  "TF1": "题目文本...",
  "TF2": "题目文本..."
}
```

### 2. 测试评分

在模板目录下运行测试：

```bash
cd hw1-template
./.autograde/test_objective_grade.sh
```

或手动测试：

```bash
python3 ./.autograde/objective_grade.py \
  --answers objective_questions/standard_answers.json \
  --standard objective_questions/standard_answers.json \
  --questions objective_questions/question_texts.json \
  --out test_grade.json \
  --summary test_summary.md \
  --type both
```

### 3. 部署到学生仓库

使用部署脚本更新所有学生仓库：

```bash
python3 scripts/update_workflows_all_branches.py \
  --template-dir hw1-template \
  --prefix hw1-stu
```

这会自动同步：
- `.gitea/workflows/objective_grade.yml`
- `.autograde/objective_grade.py`
- `objective_questions/` 目录（不包含标准答案）
- `objective_answers/` 目录模板

### 4. 保密标准答案

**重要**: `standard_answers.json` 只应存在于：
- 模板仓库（教师维护）
- 私有测试仓库（如果有）
- **不应该**推送到学生仓库

在 workflow 中，标准答案应该从私有仓库获取：

```yaml
- name: Fetch standard answers
  run: |
    AUTH_HEADER=$(printf "%s:%s" "${{ secrets.TESTS_USERNAME }}" "${{ secrets.TESTS_TOKEN }}" | base64 | tr -d '\n')
    git -c http.extraHeader="Authorization: Basic ${AUTH_HEADER}" \
      clone --depth=1 http://gitea.example.com/course/hw1-tests.git /tmp/tests
    cp /tmp/tests/objective/standard_answers.json objective_questions/
```

## 👨‍🎓 学生使用指南

### 1. 查看题目

题目位于 `objective_questions/` 目录：
- `mc_questions.md`: 选择题
- `tf_questions.md`: 判断题

### 2. 填写答案

在 `objective_answers/my_answers.json` 中填写答案：

```json
{
  "MC1": "D",
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
```

### 3. 提交作业

```bash
git add objective_answers/my_answers.json
git commit -m "完成客观题"
git push
```

### 4. 查看结果

提交后，在 Pull Request 中查看评分结果评论，包含：
- 总分和分项得分
- 每道题的对错情况
- 错误题目的正确答案

## 🔧 高级配置

### 自定义分值

当前每题 1 分，如需自定义，修改 `objective_grade.py`:

```python
# 在 grade_multiple_choice 或 grade_true_false 函数中
weights = {
    "MC1": 2,  # 2 分
    "MC2": 3,  # 3 分
    "TF1": 1,  # 1 分
}

score = weights.get(question_id, 1) if is_correct else 0
```

### 只评特定题型

可以在 workflow 中指定只评选择题或判断题：

```yaml
# 只评选择题
--type mc

# 只评判断题
--type tf

# 评所有题型（默认）
--type both
```

### 添加其他题型

评分脚本支持扩展，可添加：
- 多选题（Multiple Select）
- 填空题（Fill in the Blank）
- 匹配题（Matching）

参考现有的 `grade_multiple_choice` 和 `grade_true_false` 函数实现。

## 📊 评分结果格式

### 评分 JSON

```json
{
  "score": 9,
  "max_score": 10,
  "components": [
    {
      "type": "multiple_choice",
      "score": 4,
      "max_score": 5,
      "details": {
        "correct": 4,
        "total": 5,
        "questions": [
          {
            "question_id": "MC1",
            "question_text": "题目文本...",
            "correct_answer": "D",
            "student_answer": "A",
            "correct": false,
            "score": 0,
            "max_score": 1
          },
          ...
        ]
      }
    },
    {
      "type": "true_false",
      "score": 5,
      "max_score": 5,
      "details": {
        "correct": 5,
        "total": 5,
        "questions": [...]
      }
    }
  ],
  "timestamp": 1234567890
}
```

### 评分摘要（Markdown）

```markdown
# 客观题评分

- **总分**：9 / 10
- **组件数**：2

## 选择题

- **正确**：4 / 5

## 判断题

- **正确**：5 / 5
```

## 🐛 故障排查

### 问题 1: 找不到答案文件

**错误**: `❌ 未找到答案文件！`

**解决**:
- 确保 `objective_answers/my_answers.json` 存在
- 或创建 `objective_answers/my_answers.txt`
- 检查文件名是否正确

### 问题 2: JSON 格式错误

**错误**: `Expecting ',' delimiter`

**解决**:
- 检查 JSON 语法是否正确
- 使用 JSON 验证器验证格式
- 注意布尔值不加引号：`true`, `false`

### 问题 3: 题号不匹配

**错误**: 题目没有被评分

**解决**:
- 确保题号格式正确（MC1, TF1）
- 题号必须与 `standard_answers.json` 中一致
- 题号区分大小写

### 问题 4: Workflow 未触发

**解决**:
- 确保修改了 `objective_answers/` 目录下的文件
- 检查 workflow 的 `paths` 触发条件
- 手动触发 workflow（如果支持）

## 📖 相关文档

- [客观题题目说明](objective_questions/README.md)
- [学生答题指南](objective_answers/README.md)
- [评分脚本代码](.autograde/objective_grade.py)
- [Workflow 配置](.gitea/workflows/objective_grade.yml)

## 💡 最佳实践

1. **题目设计**
   - 题目简洁明确，避免歧义
   - 选项长度相近，避免明显错误
   - 判断题陈述清晰，避免双重否定

2. **答案保密**
   - 标准答案只存在模板仓库
   - 不要在公开仓库中暴露答案
   - 使用私有测试仓库存储敏感数据

3. **测试验证**
   - 部署前先测试评分脚本
   - 确保标准答案正确无误
   - 验证所有题型都能正常评分

4. **学生体验**
   - 提供清晰的答题说明
   - 答案格式简单易懂
   - 评分结果详细友好

5. **维护更新**
   - 定期检查评分 workflow 运行状态
   - 及时处理学生反馈的问题
   - 记录常见问题和解决方案

---

**版本**: 1.0  
**更新时间**: 2024-11-14


