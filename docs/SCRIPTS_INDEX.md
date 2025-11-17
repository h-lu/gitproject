# 脚本索引文档

本文档列出项目中所有脚本及其用途。

## 📂 目录结构

```
GitProject/
├── setup_gitea.sh                    # 系统初始化脚本
├── scripts/                          # 所有管理脚本
│   ├── create_users.py              # 批量创建用户 (Python)
│   ├── add_collaborators.sh         # 添加协作者
│   ├── generate_repos.py            # 生成学生仓库
│   ├── test_private_repo_access.py  # 验证测试仓库访问凭据
│   ├── delete_repos.py              # 删除仓库 (Python)
│   ├── quick_collect.sh             # 快速收集成绩 (包装脚本)
│   ├── collect_grades.py            # 成绩收集核心逻辑
│   ├── update_workflows_all_branches.py  # 更新所有分支的 workflow
│   └── create_course_template.py   # 课程模板生成器
└── hw1-template/.autograde/         # 自动评分脚本
    ├── grade.py                     # 编程题评分
    ├── run_tests.py                 # 通用测试运行器
    ├── llm_grade.py                 # LLM 简答题评分
    ├── objective_grade.py           # 选择题/判断题评分
    ├── aggregate_llm_grades.py      # 汇总 LLM 成绩
    ├── create_minimal_metadata.py   # 生成成绩元数据
    ├── post_comment.py              # 发布评论到 PR
    └── workflow_templates/          # 多语言 Workflow 模板
        ├── python.yml
        ├── java.yml
        └── r.yml
```

---

## 🎯 脚本分类

### 1. 系统初始化

#### `setup_gitea.sh`
- **位置**: 根目录
- **用途**: 初始化 Gitea 系统
- **运行**: `./setup_gitea.sh`

---

### 2. 用户管理

#### `scripts/create_users.py`
- **用途**: 批量创建 Gitea 用户（Python 版本）
- **输入**: `students.txt`
- **参数**:
  - `--gitea-url`: Gitea 服务器地址
  - `--token`: Admin token
  - `--students-file`: 学生列表文件
  - `--default-password`: 默认密码
- **运行**: `python3 scripts/create_users.py --gitea-url http://... --token XXX`

---

### 3. 仓库管理

#### `scripts/generate_repos.py`
- **用途**: 从模板生成学生仓库
- **参数**:
  - `--template`: 模板仓库名
  - `--org`: 组织名
  - `--prefix`: 仓库前缀（如 `hw1-stu_`）
  - `--students-file`: 学生列表文件
- **运行**: `python3 scripts/generate_repos.py --template hw1-template --org course-test --prefix hw1-stu_`

#### `scripts/test_private_repo_access.py`
- **用途**: 本地验证环境变量 `GITEA_TESTS_USERNAME` / `GITEA_TESTS_TOKEN` 是否能克隆 `hw1-tests`
- **原理**: 调用 `git ls-remote http://username:token@server/course-test/hw1-tests.git`
- **输出**: 成功/失败提示，便于在 Actions 之外排查凭据问题
- **运行**:
  ```bash
  python3 scripts/test_private_repo_access.py
  ```

#### `scripts/add_collaborators.sh`
- **用途**: 为学生仓库添加协作者（学生自己）
- **输入**: `students.txt`
- **运行**: `cd scripts && ./add_collaborators.sh`

#### `scripts/delete_repos.py`
- **用途**: 批量删除仓库（Python 版本）
- **参数**:
  - `--gitea-url`: Gitea 服务器地址
  - `--token`: Admin token
  - `--org`: 组织名
  - `--prefix`: 仓库前缀
- **运行**: `python3 scripts/delete_repos.py --org course-test --prefix hw1-stu_`

---

### 4. 成绩收集

- **用途**: 快速收集成绩（包装脚本）
- **功能**:
  - 读取当前 shell 中的 `GITEA_*` 与 `METADATA_*` 环境变量
  - 调用 `collect_grades.py --metadata-repo ...`
  - 显示快速统计（平均/最高/最低分与状态分布）
- **运行**: `./scripts/quick_collect.sh`
- **输出**: `grades_hw1-stu_YYYYMMDD_HHMMSS.csv`

#### `scripts/collect_grades.py`
- **用途**: 通过 metadata 仓库汇总所有学生的成绩
- **功能**:
  - 遍历 `hw1-metadata` 中 `records/{org}__{repo}` 下的 JSON 文件
  - 合并不同 workflow 生成的 `components`（按 type 去重，保留最新）
  - 计算总分、最大分并记录最新运行时间戳
  - 生成包含 `student_id` / `repo` / `score` / `timestamp` / `components` 的 CSV
- **参数**:
  - `--metadata-repo`: metadata 仓库（默认 `course-test/hw1-metadata`）
  - `--metadata-branch`: metadata 分支（默认 `main`）
  - `--gitea-url`: Gitea 服务器地址
  - `--token`: 管理员 token
  - `--prefix`: 仓库前缀（用于过滤）
  - `--output`: 输出 CSV 文件
- **运行**: `python3 scripts/collect_grades.py --metadata-repo course-test/hw1-metadata --token XXX --org course-test --prefix hw1-stu_`

---

### 5. 工作流更新

#### `scripts/update_workflows_all_branches.py`
- **用途**: 更新所有学生仓库的所有分支的 workflow 和 .autograde 脚本
- **功能**:
  - 克隆每个学生仓库
  - 遍历所有分支
  - 复制 `.gitea/workflows/` 文件
  - 复制 `.autograde/` 脚本
  - 删除旧的 `create_grade_metadata.py`
  - 提交并推送
- **参数**:
  - `--template-dir`: 模板目录
  - `--prefix`: 仓库前缀
- **运行**: `python3 scripts/update_workflows_all_branches.py --template-dir hw1-template --prefix hw1-stu`

---

### 6. 课程模板管理

#### `scripts/create_course_template.py`
- **用途**: 快速创建不同编程语言的课程模板
- **功能**:
  - 复制基础模板结构
  - 配置语言特定的文件和目录
  - 生成对应的 workflow
  - 创建示例代码和测试
  - 生成 problem.yaml 和 README.md
- **参数**:
  - `--name`: 作业名称（如 java-ds-hw1）
  - `--language`: 编程语言（python/java/r）
  - `--title`: 作业标题
  - `--output`: 输出目录路径
  - `--base-template`: 基础模板目录（默认: hw1-template）
- **运行**: 
```bash
python3 scripts/create_course_template.py \
  --name java-ds-hw1 \
  --language java \
  --title "数据结构（Java）" \
  --output java-ds-hw1-template
```
- **详细文档**: 见 [COURSE_TEMPLATE_GUIDE.md](COURSE_TEMPLATE_GUIDE.md)

---

## 🤖 自动评分脚本 (`.autograde/`)

这些脚本在 Gitea Actions workflow 中自动运行。

### `hw1-template/.autograde/run_tests.py`
- **用途**: 通用测试运行器（支持多种编程语言）
- **功能**:
  - 根据语言运行对应的测试框架
  - 生成 JUnit XML 格式的测试报告
  - 支持 Python (pytest), Java (Maven), R (testthat)
- **参数**:
  - `--language`: 编程语言（python/java/r）
  - `--test-dir`: 测试目录
  - `--output-xml`: JUnit XML 输出文件
  - `--source-dir`: 源代码目录（可选，用于覆盖率）
- **环境变量**:
  - `LANGUAGE`: 编程语言
  - `TEST_DIR`: 测试目录路径
  - `SOURCE_DIR`: 源代码目录路径

### `hw1-template/.autograde/grade.py`
- **用途**: 编程题自动评分（语言无关）
- **功能**:
  - 解析 JUnit XML 测试报告
  - 计算通过率和分数
  - 计算迟交扣分
  - 生成 `grade.json`
- **参数**:
  - `--junit`: JUnit XML 文件路径
  - `--out`: 输出文件 (默认: `grade.json`)
  - `--summary`: 摘要 Markdown 文件 (默认: `summary.md`)

### `hw1-template/.autograde/llm_grade.py`
- **用途**: LLM 简答题自动评分
- **功能**:
  - 使用 DeepSeek API 评分
  - 根据 rubric.json 评分标准
  - 生成 `llm_grade.json`
- **参数**:
  - `--question-file`: 题目文件
  - `--answer-file`: 学生答案文件
  - `--rubric-file`: 评分标准文件
  - `--out`: 输出文件

### `hw1-template/.autograde/objective_grade.py`
- **用途**: 选择题/判断题自动评分
- **功能**:
  - 对比标准答案
  - 支持 JSON/文本格式
  - 生成 `objective_grade.json`
- **参数**:
  - `--question-file`: 题目定义文件
  - `--answer-file`: 学生答案文件
  - `--out`: 输出文件
  - `--type`: 题型 (`multiple_choice` 或 `true_false`)

### `hw1-template/.autograde/create_minimal_metadata.py`
- **用途**: 生成结构化成绩元数据
- **功能**:
  - 从 `grade.json` 或 `llm_grade.json` 生成 `metadata.json`
  - 自动提取 `student_id` (从 `REPO` 环境变量)
  - 包含完整的详细信息（failed_tests, criteria 等）
- **环境变量**:
  - `ASSIGNMENT_ID`: 作业 ID (如 `hw1`)
  - `REPO`: 仓库名 (如 `course-test/hw1-stu_sit001`)
  - `GRADE_TYPE`: 成绩类型 (`programming` 或 `llm`)
  - `LANGUAGE`: 编程语言 (`python`, `java`, `r`)
- **输出**: `metadata.json` (stdout)

### `hw1-template/.autograde/upload_metadata.py`
- **用途**: 把 grading workflow 生成的 `metadata.json` 上传到 `hw1-metadata` 私有仓库
- **功能**:
  - 读取指定的 `metadata.json` 并 base64 编码
  - 构造 `records/{org}__{repo}/{workflow}_{run_id}_{commit}.json` 路径
  - 根据 `server_url` / `external_host` 自动选择可访问的 Gitea host
  - 通过 Gitea API 创建或更新文件，保存运行信息
- **参数**:
  - `--metadata-file`: `metadata.json` 的路径
  - `--metadata-repo`: 私有 metadata 仓库（如 `course-test/hw1-metadata`）
  - `--branch`: 目标分支（默认 `main`）
  - `--student-repo`, `--run-id`, `--workflow`, `--commit-sha`: 构建目标路径
  - `--server-url`, `--external-host`: 用于 host 检测
- **环境变量**:
  - `METADATA_TOKEN`: 拥有写权限的 PAT，workflow 运行时设置
### `hw1-template/.autograde/aggregate_llm_grades.py`
- **用途**: 汇总多个 LLM 简答题的成绩
- **功能**: 合并多个 `*_grade.json` 文件为 `llm_grade.json`
- **参数**:
  - `--grade-files`: 成绩文件列表
  - `--out`: 输出文件

### `hw1-template/.autograde/post_comment.py`
- **用途**: 可选地将分数与 metadata 发布为 PR/Issue 评论（自动流程中默认不启用）
- **功能**:
  - 构建 Markdown 成绩报告并嵌入 `metadata.json`
  - 调用 Gitea API 发布当前 commit/PR
- **环境变量**:
  - `GITEA_TOKEN`: API token
  - `TARGET_URL`: 目标仓库 URL
  - `COMMENT_SUMMARY`: 提示文本
  - `GRADE_METADATA`: JSON 字符串
  - `COMMIT_SHA`: Commit SHA
  - `PR_NUMBER`（可选）：当需要注释某个 PR 时提供

---

## 📊 工作流程

### 完整的作业生命周期

```
1. 初始化
   └─> setup_gitea.sh

2. 创建用户
   └─> create_users.py (从 students.txt)

3. 生成学生仓库
   └─> generate_repos.py (从 hw1-template)

4. 添加协作者
   └─> add_collaborators.sh

5. 学生提交作业 (push 到 `main`)
   └─> Gitea Actions 自动运行:
       ├─> grade.py (编程题)
       ├─> llm_grade.py (LLM 简答题)
       ├─> create_minimal_metadata.py (生成 JSON 元数据)
       └─> upload_metadata.py (推送 metadata 到 `hw1-metadata`)

6. 收集成绩
   └─> quick_collect.sh
       └─> collect_grades.py（读取 private metadata repo）
           └─> grades_hw1-stu_YYYYMMDD_HHMMSS.csv

7. 更新 workflow (如需)
   └─> update_workflows_all_branches.py
```

---

## 🔧 配置文件

### 常用环境变量

所有脚本都依赖当前 shell 中的环境变量。可以在执行任务前 `export`，或写入 `~/.bashrc`：

```bash
export GITEA_URL=http://49.234.193.192:3000
export GITEA_ADMIN_TOKEN=your_token_here
export GITEA_TESTS_USERNAME=course-admin
export GITEA_TESTS_TOKEN=pat_for_hw1_tests
export ORGANIZATION=course-test
export PREFIX=hw1-stu_
export DEEPSEEK_API_KEY=your_deepseek_key_here   # 如果使用 LLM
```

### `scripts/students.txt`
学生列表，格式：

```
student_id,gitea_username
sit001,sit001
sit002,sit002
...
```

---

## 📝 使用建议

1. **所有管理脚本都在 `scripts/` 目录中**
   - 便于组织和维护
   - 避免根目录混乱

2. **使用 Python 版本优先**
   - 更易维护和扩展
   - 更好的错误处理

3. **使用 `quick_collect.sh` 而非直接调用 `collect_grades.py`**
   - 统一读取环境变量
   - 提供友好的输出格式

4. **更新 workflow 时使用 `update_workflows_all_branches.py`**
   - 确保所有分支都更新
   - 自动清理旧文件

---

## 🗑️ 已清理的文件

以下文件已被删除（2025-11-13）：

- ❌ `./quick_collect.sh` (根目录旧版本，已移至 scripts/)
- ❌ `scripts/test_extract_with_real_comment.py` (临时测试脚本)
- ❌ `scripts/test_metadata_method.py` (临时测试脚本)
- ❌ `scripts/update_workflows.py` (被 update_workflows_all_branches.py 取代)
- ❌ `hw1-template/.autograde/create_grade_metadata.py` (旧版本，被 create_minimal_metadata.py 取代)

---

## 📦 Workflow 模板

位置: `hw1-template/.autograde/workflow_templates/`

### Python Workflow (`python.yml`)
- **容器**: python:3.11
- **测试框架**: pytest
- **特性**: 自动安装 requirements.txt, 支持代码覆盖率

### Java Workflow (`java.yml`)  
- **容器**: maven:3.9-eclipse-temurin-17
- **测试框架**: JUnit 5
- **特性**: Maven 自动管理依赖, Surefire 报告

### R Workflow (`r.yml`)
- **容器**: r-base:4.3
- **测试框架**: testthat
- **特性**: 从 DESCRIPTION 安装依赖, JUnit Reporter

使用方法：
```bash
# 复制对应语言的模板
cp hw1-template/.autograde/workflow_templates/java.yml .gitea/workflows/grade.yml
```

详见: [COURSE_TEMPLATE_GUIDE.md](COURSE_TEMPLATE_GUIDE.md)

---

## 📚 相关文档

- [课程模板创建指南](COURSE_TEMPLATE_GUIDE.md) - 如何创建不同语言的课程模板
- [成绩元数据格式规范](GRADING_METADATA_SPEC.md) - JSON 格式详细说明
- [示例](hw1-template/examples/) - Python/Java/R 完整示例

---

最后更新: 2025-11-13

