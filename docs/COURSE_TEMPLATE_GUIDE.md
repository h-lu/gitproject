# 课程模板创建指南

本指南说明如何使用通用评分框架创建不同编程语言的课程作业模板。

## 目录

- [快速开始](#快速开始)
- [手动创建模板](#手动创建模板)
- [支持的语言](#支持的语言)
- [架构说明](#架构说明)
- [最佳实践](#最佳实践)
- [常见问题](#常见问题)

---

## 快速开始

使用 `create_course_template.py` 工具快速创建新课程模板：

### 创建 Java 课程模板

```bash
python3 scripts/create_course_template.py \
  --name java-ds-hw1 \
  --language java \
  --title "数据结构（Java）" \
  --output java-ds-hw1-template
```

### 创建 R 课程模板

```bash
python3 scripts/create_course_template.py \
  --name stats-r-hw1 \
  --language r \
  --title "统计学与R语言" \
  --output stats-r-hw1-template
```

### 创建 Python 课程模板

```bash
python3 scripts/create_course_template.py \
  --name python-intro-hw1 \
  --language python \
  --title "Python程序设计" \
  --output python-intro-hw1-template
```

工具会自动：
1. 复制基础模板结构
2. 复制语言特定的示例代码
3. 生成对应的 workflow 文件
4. 创建 problem.yaml 配置
5. 生成 README.md 和 .gitignore

---

## 手动创建模板

如果需要更多控制，可以手动创建模板：

### 步骤 1: 复制基础结构

```bash
# 选择一个基础模板（通常使用 hw1-template）
cp -r hw1-template my-course-template
cd my-course-template
```

### 步骤 2: 选择语言示例

根据目标语言，复制对应的示例：

```bash
# 对于 Java 课程
cp -r examples/java_example/* .

# 对于 R 课程
cp -r examples/r_example/* .

# 对于 Python 课程（已经有了，无需复制）
```

### 步骤 3: 配置 Workflow

```bash
# 选择对应语言的 workflow 模板
cp .autograde/workflow_templates/java.yml .gitea/workflows/grade.yml

# 或 R
cp .autograde/workflow_templates/r.yml .gitea/workflows/grade.yml

# 或 Python
cp .autograde/workflow_templates/python.yml .gitea/workflows/grade.yml
```

### 步骤 4: 修改 problem.yaml

编辑 `problem.yaml` 文件：

```yaml
assignment:
  id: my-course-hw1              # 修改为你的作业 ID
  title: 我的课程作业             # 修改标题
  language: java                  # 设置语言: python/java/r
  type: programming

description: |
  作业描述...

language_config:
  test_framework: junit5          # 根据语言修改
  dependencies_file: pom.xml      # 根据语言修改
  source_dir: src/main/java       # 根据语言修改
  test_dir: src/test/java         # 根据语言修改

grading:
  max_score: 100
  components:
    - name: programming
      weight: 100
      type: auto
      language: java                # 与上面保持一致
```

### 步骤 5: 创建作业内容

根据语言创建源代码和测试：

#### Python
```
src/
  ├── __init__.py
  └── mymodule.py
tests_public/
  ├── __init__.py
  └── test_mymodule.py
requirements.txt
pytest.ini
```

#### Java
```
src/
  ├── main/java/com/example/
  │   └── MyClass.java
  └── test/java/com/example/
      └── MyClassTest.java
pom.xml
```

#### R
```
R/
  └── myfunctions.R
tests/
  └── testthat/
      └── test_myfunctions.R
DESCRIPTION
```

### 步骤 6: 测试和部署

```bash
# 1. 初始化 Git 仓库
git init
git add .
git commit -m "Initial course template"

# 2. 推送到 Gitea（作为模板仓库）
git remote add origin http://your-gitea.com/your-org/my-course-template.git
git push -u origin main

# 3. 在 Gitea 中将仓库标记为模板

# 4. 使用 generate_repos.py 为学生创建仓库
python3 scripts/generate_repos.py \
  --template my-course-template \
  --org course-org \
  --prefix hw1-stu \
  --students-file students.txt
```

---

## 支持的语言

| 语言   | 测试框架 | 容器镜像                      | 依赖管理      | 状态 |
|--------|----------|-------------------------------|---------------|------|
| Python | pytest   | python:3.11                   | requirements.txt | ✅ 完整支持 |
| Java   | JUnit 5  | maven:3.9-eclipse-temurin-17  | pom.xml       | ✅ 完整支持 |
| R      | testthat | r-base:4.3                    | DESCRIPTION   | ✅ 完整支持 |

### 添加新语言支持

如需添加新语言（如 C++, JavaScript），需要：

1. 在 `.autograde/run_tests.py` 中添加测试运行器
2. 创建对应的 workflow 模板
3. 在 `examples/` 中添加示例
4. 更新 `create_course_template.py` 中的 `LANGUAGE_CONFIGS`

---

## 架构说明

### 通用评分流程

所有语言共享相同的评分流程：

```
学生 push 到 main（或教师手动触发 workflow_dispatch）
    ↓
1. 运行测试 → JUnit XML
   ├─ Python: pytest --junit-xml
   ├─ Java: mvn test (Surefire)
   └─ R: testthat JUnitReporter
    ↓
2. 解析 JUnit XML → 计算分数（`grade.py`）
    ↓
3. 生成 metadata → `create_minimal_metadata.py` 输出 `metadata.json`
    ↓
4. 上传 metadata 到 `hw1-metadata`（私有仓库，`upload_metadata.py`）
    ↓
5. 教师运行 `collect_grades.py` / `quick_collect.sh` 汇总 CSV
```

### 语言特定 vs 语言无关

**语言无关的组件**（可复用）：
- `grade.py` - JUnit XML 解析和评分
- `create_minimal_metadata.py` - JSON 元数据生成
- `upload_metadata.py` - 上传 metadata 到私有仓库（workflow 默认运行）
- `collect_grades.py` - 成绩收集
- `post_comment.py` - PR 评论发布（可选，仅在人工通知或旧流程时使用）

**语言特定的组件**（需配置）：
- Workflow 文件（`.gitea/workflows/grade.yml`）
- 测试运行命令
- Docker 容器镜像
- 依赖管理文件

---

## 最佳实践

### 1. 目录结构

保持清晰的目录结构：

```
course-template/
├── .gitea/workflows/        # CI/CD 配置
├── .autograde/              # 评分脚本（通用）
├── src/                     # 源代码目录（学生编写）
├── tests_public/            # 公开测试（学生可见）
├── problem.yaml             # 作业配置
├── README.md                # 作业说明
└── [依赖文件]               # requirements.txt/pom.xml/DESCRIPTION
```

### 2. 测试设计

- **公开测试**：放在模板仓库中，学生可见用于开发
- **隐藏测试**：放在私有 `*-tests` 仓库中，用于最终评分
- **测试命名**：使用清晰的测试名称，失败时学生能理解

### 3. 评分配置

在 `problem.yaml` 中合理配置评分点：

```yaml
grading:
  max_score: 100
  components:
    - name: basic_functionality
      weight: 40
      description: 基本功能
    
    - name: edge_cases
      weight: 30
      description: 边界情况处理
    
    - name: performance
      weight: 20
      description: 性能要求
    
    - name: code_quality
      weight: 10
      description: 代码质量
```

### 4. 文档完善

确保 README.md 包含：
- 作业目标和要求
- 本地开发环境设置
- 测试运行方法
- 提交流程
- 评分标准

### 5. 依赖管理

- 明确列出所有依赖
- 固定版本号避免兼容性问题
- 使用镜像源加速安装（中国地区）

### 6. 迟交扣分

在 Gitea 仓库的 Secrets 中设置 `DEADLINE`：

```bash
# 格式: YYYY-MM-DDTHH:MM:SS
DEADLINE=2025-12-31T23:59:59
```

`grade.py` 会自动计算迟交扣分：
- 第一天：扣 10 分
- 之后每天：扣 5 分
- 最多扣：30 分

---

## 常见问题

### Q: 如何为现有课程添加新作业？

A: 使用相同的模板创建新的作业仓库（如 hw2-template），修改 `assignment.id` 和内容即可。

### Q: 可以混合多种语言吗？

A: 技术上可以，但**不推荐**。建议每个课程/作业使用单一语言，保持简单清晰。

### Q: 如何添加简答题？

A: 在模板中添加 `questions/` 和 `answers/` 目录，配置 LLM 评分 workflow。参考 `hw1-template` 的 `llm_autograde.yml`。

### Q: 测试框架必须输出 JUnit XML 吗？

A: 是的。通用评分框架依赖 JUnit XML 格式。幸运的是，大多数测试框架都支持：
- Python pytest: `--junit-xml`
- Java JUnit: Maven Surefire 插件
- R testthat: `JunitReporter`
- JavaScript Mocha: `mocha-junit-reporter`
- C++ GoogleTest: `--gtest_output=xml`

### Q: 如何调试 workflow 失败？

A: 
1. 查看 Gitea Actions 的日志
2. 本地使用相同的容器测试：
   ```bash
   docker run -it --rm -v $(pwd):/workspace python:3.11 bash
   cd /workspace
   # 手动运行 workflow 步骤
   ```
3. 检查 JUnit XML 是否正确生成
4. 验证 `grade.json` 和 `metadata.json` 的格式

### Q: 学生如何知道他们的成绩？

A: 学生将代码 push 到 `main`，新提交会立即触发 workflow：
1. Actions 页面显示测试日志、总分与状态
2. 详细的 `metadata.json` 上传到私有 `hw1-metadata`（学生无法读取）
3. 教师通过 `collect_grades.py` / `quick_collect.sh` 汇总所有 metadata 并生成 CSV

若仍想为个别 PR 发布注释，可手动运行 `post_comment.py`（不在自动流程中）。

### Q: 如何更新已部署的学生仓库？

A: 使用 `update_workflows_all_branches.py`：

```bash
python3 scripts/update_workflows_all_branches.py \
  --template-dir my-course-template \
  --prefix hw1-stu
```

这会更新所有学生仓库的所有分支。

---

## 示例：创建完整的 Java 课程

### 1. 创建模板

```bash
python3 scripts/create_course_template.py \
  --name java-ds \
  --language java \
  --title "数据结构（Java）" \
  --output java-ds-template
```

### 2. 实现作业内容

```bash
cd java-ds-template

# 编辑源代码
vim src/main/java/com/example/LinkedList.java

# 编辑测试
vim src/test/java/com/example/LinkedListTest.java

# 编辑配置
vim problem.yaml
vim README.md
```

### 3. 本地测试

```bash
# 运行测试
mvn test

# 查看报告
ls target/surefire-reports/
```

### 4. 推送到 Gitea

```bash
git init
git add .
git commit -m "Java 数据结构 HW1"
git remote add origin http://gitea.example.com/course/java-ds-template.git
git push -u origin main
```

### 5. 标记为模板

在 Gitea Web UI 中：Settings → Template → ✓ Make this repository a template

### 6. 创建学生仓库

```bash
python3 scripts/generate_repos.py \
  --template java-ds-template \
  --org java-course \
  --prefix hw1-stu \
  --students-file students.txt
```

### 7. 添加协作者

```bash
cd scripts
./add_collaborators.sh
```

### 8. 收集成绩

```bash
./scripts/quick_collect.sh
# 查看 grades_hw1-stu_*.csv
```

---

## 相关文档

- [脚本索引](SCRIPTS_INDEX.md) - 所有脚本的详细说明
- [成绩元数据格式](GRADING_METADATA_SPEC.md) - JSON 格式规范
- [Workflow 模板](hw1-template/.autograde/workflow_templates/) - 各语言模板
- [示例](hw1-template/examples/) - Python/Java/R 示例

---

## 贡献指南

欢迎为框架添加新语言支持！请：

1. 在 `examples/` 中添加完整示例
2. 在 `.autograde/workflow_templates/` 中创建 workflow
3. 更新 `run_tests.py` 支持新语言
4. 更新本文档
5. 提交 Pull Request

---

最后更新: 2025-11-13
版本: 1.0

