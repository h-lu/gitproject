# hw1-template 模板自定义指南

`hw1-template` 是一个**通用的作业模板**，可以根据实际需求灵活配置题型、分数和内容。

## 📋 模板结构

```
hw1-template/
├── assignment_config.yaml      # 📌 作业配置文件（新增）
│
├── 📝 题目部分（可选）
│   ├── src/                   # 编程题源代码目录
│   ├── tests_public/          # 编程题公开测试
│   ├── objective_questions/   # 客观题题目
│   ├── questions/             # 简答题题目
│   └── data/                  # 数据集
│
├── 📋 答案部分（可选）
│   ├── objective_answers/     # 客观题答案
│   └── answers/               # 简答题答案
│
├── 🤖 评分系统
│   ├── .autograde/            # 评分脚本
│   └── .gitea/workflows/      # CI/CD workflows
│
└── 📚 文档
    ├── README.md              # 作业说明
    └── *.md                   # 其他文档
```

## 🎯 自定义作业结构

### 方法 1: 通过配置文件（推荐）

编辑 `assignment_config.yaml` 来启用/禁用题型：

```yaml
grading:
  components:
    programming:
      enabled: true      # 启用编程题
      weight: 60
      
    objective:
      enabled: false     # 禁用客观题
      weight: 0
      
    essay:
      enabled: true      # 启用简答题
      weight: 40
```

### 方法 2: 手动调整文件结构

根据需要删除或保留对应的目录和文件。

## 🔧 常见场景配置

### 场景 1: 纯编程作业（100 分编程题）

**配置**:
```yaml
grading:
  components:
    programming:
      enabled: true
      weight: 100
    objective:
      enabled: false
    essay:
      enabled: false
```

**删除的目录**:
- `objective_questions/`
- `objective_answers/`
- `questions/`
- `answers/`

**删除的 workflow**:
- `.gitea/workflows/objective_grade.yml`
- `.gitea/workflows/llm_autograde.yml`

### 场景 2: 理论作业（客观题 + 简答题）

**配置**:
```yaml
grading:
  components:
    programming:
      enabled: false
    objective:
      enabled: true
      weight: 50
    essay:
      enabled: true
      weight: 50
```

**删除的目录**:
- `src/`
- `tests_public/`
- `data/`

**删除的 workflow**:
- `.gitea/workflows/grade.yml`

### 场景 3: 综合作业（全部题型）

**配置**:
```yaml
grading:
  components:
    programming:
      enabled: true
      weight: 60
    objective:
      enabled: true
      weight: 20
    essay:
      enabled: true
      weight: 20
```

**保留所有目录和文件**（默认配置）

### 场景 4: 考试（纯客观题）

**配置**:
```yaml
grading:
  components:
    programming:
      enabled: false
    objective:
      enabled: true
      weight: 100
      multiple_choice:
        enabled: true
        questions: 20
        points_per_question: 4
      true_false:
        enabled: true
        questions: 10
        points_per_question: 2
    essay:
      enabled: false
```

## 📊 自定义分数分配

### 修改编程题分数

编辑 `.autograde/grade.py` 或 `problem.yaml` 中的权重配置。

### 修改客观题分数

两种方式：

1. **简单方式**：调整题目数量
   ```yaml
   objective:
     multiple_choice:
       questions: 10      # 10 道选择题
       points_per_question: 3  # 每题 3 分
   ```

2. **高级方式**：修改 `.autograde/objective_grade.py` 实现自定义权重
   ```python
   weights = {
       "MC1": 2,  # 第 1 题 2 分
       "MC2": 3,  # 第 2 题 3 分
       "TF1": 1,  # 第 1 题 1 分
   }
   ```

### 修改简答题分数

编辑 `.autograde/rubric.json`：

```json
{
  "SA1": {
    "max_score": 15,
    "criteria": {...}
  },
  "SA2": {
    "max_score": 10,
    "criteria": {...}
  }
}
```

## 🎨 自定义题目内容

### 编程题

1. 修改 `problem.yaml` - 题目描述和要求
2. 修改 `src/` - 初始代码结构
3. 修改 `tests_public/` - 公开测试用例
4. 修改 `data/` - 数据集

### 客观题

1. 编辑 `objective_questions/mc_questions.md` - 选择题题目
2. 编辑 `objective_questions/tf_questions.md` - 判断题题目
3. 更新 `objective_questions/standard_answers.json` - 标准答案
4. 更新 `objective_questions/question_texts.json` - 题目文本
5. 调整 `objective_answers/my_answers.json` - 答案模板

### 简答题

1. 编辑 `questions/sa*.md` - 题目文件
2. 编辑 `.autograde/rubric.json` - 评分标准
3. 调整 `answers/sa*.md` - 答案模板

## 🚀 快速创建新作业

### 基于 hw1-template 创建

```bash
# 1. 复制模板
cp -r hw1-template hw2-template

# 2. 修改配置
cd hw2-template
vim assignment_config.yaml

# 3. 删除不需要的题型目录
# 例如：如果不需要客观题
rm -rf objective_questions objective_answers
rm .gitea/workflows/objective_grade.yml

# 4. 修改题目内容
vim README.md
vim problem.yaml
# ... 编辑其他题目文件

# 5. 更新 README.md 中的成绩构成
vim README.md
```

### 使用脚本创建（推荐）

```bash
python3 scripts/create_assignment.py \
  --name hw2 \
  --title "数据结构基础" \
  --enable-programming \
  --enable-objective \
  --disable-essay \
  --programming-score 70 \
  --objective-score 30
```

## 📝 更新作业说明

编辑 `README.md`，确保更新以下部分：

1. **作业标题和说明**
2. **成绩构成**：匹配实际启用的题型
3. **提交规范**：只说明需要提交的部分
4. **题目说明**：只包含实际存在的题型

示例：

```markdown
## 成绩构成（100 分）

### 编程题（100 分）

- 数据结构实现（40 分）
- 算法实现（40 分）
- 性能优化（20 分）

## 提交规范

1. **编程题提交**：在 `src/` 目录中实现相关代码
2. **提交方式**：完成后提交 PR
```

## ⚙️ 更新 Workflows

如果禁用某个题型，记得删除或禁用对应的 workflow 文件：

```bash
# 禁用客观题 workflow
rm .gitea/workflows/objective_grade.yml

# 或者在 workflow 中添加条件
# on:
#   pull_request:
#     types: [opened, synchronize]
#     paths-ignore:
#       - '**'  # 禁用此 workflow
```

## 🔒 标准答案管理

### 客观题标准答案

**重要**：`objective_questions/standard_answers.json` 包含标准答案，应该：

1. **保留在模板仓库**（教师维护）
2. **不推送到学生仓库**（在 `.gitignore` 中排除）
3. **通过私有测试仓库提供**（在 workflow 中动态获取）

在 workflow 中动态获取标准答案：

```yaml
- name: Fetch standard answers
  run: |
    AUTH_HEADER=$(printf "%s:%s" "${{ secrets.TESTS_USERNAME }}" "${{ secrets.TESTS_TOKEN }}" | base64 | tr -d '\n')
    git -c http.extraHeader="Authorization: Basic ${AUTH_HEADER}" \
      clone --depth=1 http://gitea.example.com/course/hw1-tests.git /tmp/tests
    cp /tmp/tests/objective/standard_answers.json objective_questions/
```

### 简答题评分标准

类似地，`rubric.json` 也应该只在教师侧维护。

## 📚 示例配置

### 示例 1: Python 编程基础课

```yaml
assignment:
  id: python-basics-hw1
  title: "Python 编程基础"

grading:
  total_score: 100
  components:
    programming:
      enabled: true
      weight: 80
    objective:
      enabled: true
      weight: 20
      multiple_choice:
        questions: 10
        points_per_question: 2
    essay:
      enabled: false
```

### 示例 2: 机器学习理论课

```yaml
assignment:
  id: ml-theory-hw1
  title: "机器学习理论"

grading:
  total_score: 100
  components:
    programming:
      enabled: false
    objective:
      enabled: true
      weight: 50
      multiple_choice:
        questions: 15
        points_per_question: 2
      true_false:
        questions: 10
        points_per_question: 2
    essay:
      enabled: true
      weight: 50
      questions: 5
```

### 示例 3: 算法竞赛

```yaml
assignment:
  id: algorithm-contest
  title: "算法竞赛"

grading:
  total_score: 100
  components:
    programming:
      enabled: true
      weight: 100
    objective:
      enabled: false
    essay:
      enabled: false

late_penalty:
  enabled: false  # 竞赛不允许迟交
```

## 🛠️ 工具脚本

### 创建自定义作业脚本（建议创建）

创建 `scripts/create_custom_assignment.py` 脚本，自动根据配置生成作业：

```bash
python3 scripts/create_custom_assignment.py \
  --config assignment_config.yaml \
  --output hw2-template
```

脚本会自动：
1. 读取配置文件
2. 复制模板结构
3. 删除禁用的题型目录
4. 删除禁用的 workflows
5. 生成对应的 README.md

## 📖 最佳实践

1. **明确题型需求**：先确定作业需要哪些题型，再配置模板
2. **保持一致性**：配置文件、目录结构、README.md 应该保持一致
3. **测试完整性**：创建新作业后，先在测试仓库验证所有 workflows
4. **文档更新**：删除题型后，更新所有相关文档
5. **版本管理**：为不同的作业类型维护不同的模板分支

## 🆘 常见问题

**Q: 如何完全禁用某个题型？**

A: 三步走：
1. 在 `assignment_config.yaml` 中设置 `enabled: false`
2. 删除对应的目录
3. 删除对应的 workflow 文件

**Q: 可以只使用客观题吗？**

A: 可以！禁用 programming 和 essay，只启用 objective。

**Q: 如何调整题目数量？**

A: 直接添加/删除题目文件，并更新 `standard_answers.json`。

**Q: 标准答案会被学生看到吗？**

A: 不会，只要你不推送到学生仓库。建议通过私有仓库动态获取。

## 📞 相关文档

- [完整系统文档](docs/README.md)
- [客观题使用指南](OBJECTIVE_QUESTIONS_GUIDE.md)
- [创建课程模板](docs/COURSE_TEMPLATE_GUIDE.md)
- [评分元数据规范](docs/GRADING_METADATA_SPEC.md)

---

**总结**：`hw1-template` 是一个灵活的通用模板，可以根据实际课程需求自由组合题型和调整分数。通过配置文件和目录结构的调整，可以快速创建适合不同课程的作业模板。

