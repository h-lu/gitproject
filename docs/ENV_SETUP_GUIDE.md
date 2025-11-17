# 环境配置指南

本指南帮助你快速配置 Gitea 自动评分系统。

## 🚀 快速开始

### 1. 运行配置检查

```bash
./check_config.sh
```

这个脚本会检查：
- ✅ Gitea 服务器连接
- ✅ API Token 有效性
- ✅ `hw1-template` 和 `hw1-tests` 仓库
- ✅ 管理脚本
- ✅ Python 依赖

### 2. 配置环境变量

为后续脚本导出必要的环境变量，可直接在当前 shell 中执行，也可以写入 `~/.bashrc` 或其他启动脚本：

```bash
export GITEA_URL=http://49.234.193.192:3000
export GITEA_ADMIN_TOKEN=<你的管理员 Token>
export ORGANIZATION=course-test
export TEMPLATE_REPO=hw1-template
export PREFIX=hw1-stu_
export TESTS_REPO=hw1-tests           # 可选
export DEEPSEEK_API_KEY=<可选 LLM Key>
export DEADLINE=2025-12-31T23:59:59   # 可选
```

也可以使用 `direnv`、`dotenvx` 等工具在本地管理这些变量，无需额外的配置文件。

### 3. 生成 Gitea Token

1. 登录 Gitea
2. 点击右上角头像 → **设置**
3. 左侧菜单 → **应用** → **管理访问令牌**
4. 点击 **生成新令牌**
5. 设置令牌名称（如 `autograde-system`）
6. 选择以下权限：
   - ✅ `write:admin` - 创建用户
   - ✅ `write:organization` - 管理组织
   - ✅ `write:repository` - 创建/管理仓库
   - ✅ `write:issue` - 发布 PR 评论
7. 点击 **生成令牌**
8. **重要**：复制生成的 Token（只显示一次）
9. 在终端中执行 `export GITEA_ADMIN_TOKEN=<复制的值>`，或写入你的 shell 配置文件

### 4. 安装 Python 依赖

```bash
pip3 install requests python-dotenv
```

或者使用 requirements.txt：

```bash
pip3 install -r requirements.txt
```

### 5. 准备学生列表

编辑 `scripts/students.txt`：

```bash
vim scripts/students.txt
```

格式（每行一个学生）：
```
student_id1
student_id2
student_id3
```

或者包含 Gitea 用户名和邮箱：
```
student_id1,username1,email1@example.com
student_id2,username2,email2@example.com
```

### 6. 再次运行检查

```bash
./check_config.sh
```

确保所有检查通过（✅ 所有检查通过！系统可以直接使用）

## 📦 hw1-template 和 hw1-tests 状态

根据检查结果，这两个仓库**可以直接使用**，包含：

### hw1-template ✅
- ✅ Workflow 文件（`grade.yml`, `llm_autograde.yml`）
- ✅ 评分脚本（`grade.py`, `run_tests.py`, 等）
- ✅ 源代码模板（`src/models/logistic_regression.py`）
- ✅ 公开测试（4 个测试文件）
- ✅ 多语言示例（Java, R）
- ✅ 配置文件（`problem.yaml`, `README.md`）

### hw1-tests ✅
- ✅ 隐藏测试（4 个测试文件）
- ✅ 隐藏数据集（`breast_cancer_hidden.csv`）

**状态**：两个仓库都已完整，可以直接使用！

## 🎯 使用流程

### 方案 A：使用现有的 hw1-template（推荐）

hw1-template 是一个**机器学习课程**的 Python 作业，包含：
- 编程题：实现逻辑回归（70 分）
- 简答题：LLM 自动评分（30 分）

**步骤**：

1. **推送模板到 Gitea**（如果还没有）：
```bash
cd hw1-template
git remote add origin http://49.234.193.192:3000/course-test/hw1-template.git
git push -u origin main
```

2. **标记为模板**：
   - 在 Gitea Web UI 中打开 `hw1-template` 仓库
   - Settings → 勾选 "Template Repository"

3. **推送隐藏测试**：
```bash
cd ../hw1-tests
git remote add origin http://49.234.193.192:3000/course-test/hw1-tests.git
git push -u origin main
```

4. **设置为私有**：
   - 在 Gitea Web UI 中打开 `hw1-tests` 仓库
   - Settings → Visibility → Private

5. **配置 Secrets**（在 hw1-template 中）：
   - Settings → Secrets → Actions Secrets
   - 添加 `TESTS_USERNAME`：值为拥有 `hw1-tests` 访问权限的管理员账号（如 `course-admin`）
   - 添加 `TESTS_TOKEN`：上述账号的 PAT（需要 `read:repository`）
   - 添加 `EXTERNAL_GITEA_HOST`：值为 `49.234.193.192:3000`
   - 添加 `DEADLINE`：值为 `2025-12-31T23:59:59`
   - 添加 `DEEPSEEK_API_KEY`：值为你的 DeepSeek API Key（如果使用 LLM）

6. **生成学生仓库**：
```bash
cd scripts
python3 generate_repos.py
```

7. **添加协作者**：
```bash
./add_collaborators.sh
```

### 方案 B：创建新的课程模板

如果你要创建 **Java 课程** 或 **R 课程**：

```bash
# 创建 Java 课程
python3 scripts/create_course_template.py \
  --name java-ds-hw1 \
  --language java \
  --title "数据结构（Java）" \
  --output java-ds-hw1-template

# 创建 R 课程
python3 scripts/create_course_template.py \
  --name stats-r-hw1 \
  --language r \
  --title "统计学与R语言" \
  --output stats-r-hw1-template
```

然后按照方案 A 的步骤推送和配置新模板。

详见：[COURSE_TEMPLATE_GUIDE.md](COURSE_TEMPLATE_GUIDE.md)

## 🔧 常用环境变量

所有脚本都会读取当前 shell 中的环境变量，因此在执行脚本前请确保已设置以下键值：

| 脚本 | 依赖的环境变量 |
|------|---------------|
| `generate_repos.py` | `GITEA_URL`, `GITEA_ADMIN_TOKEN`, `ORGANIZATION`, `TEMPLATE_REPO`, `PREFIX` |
| `add_collaborators.sh` | `GITEA_URL`, `GITEA_ADMIN_TOKEN`, `ORGANIZATION`, `PREFIX`, `STUDENTS_FILE` |
| `collect_grades.py` | `GITEA_URL`, `GITEA_ADMIN_TOKEN`, `ORGANIZATION`, `PREFIX`, `METADATA_REPO`, `METADATA_BRANCH` |
| `quick_collect.sh` | `GITEA_URL`, `GITEA_ADMIN_TOKEN`, `ORGANIZATION`, `PREFIX`, `METADATA_REPO`, `METADATA_BRANCH` |
| `update_workflows_all_branches.py` | `GITEA_URL`, `GITEA_ADMIN_TOKEN`, `ORGANIZATION`, `PREFIX`, `TEMPLATE_REPO` |

建议在 shell 中运行一次以下命令，之后所有脚本即可直接使用：

```bash
cat >> ~/.bashrc <<'EOF'
export GITEA_URL=http://49.234.193.192:3000
export GITEA_ADMIN_TOKEN=<your-admin-token>
export ORGANIZATION=course-test
export TEMPLATE_REPO=hw1-template
export TESTS_REPO=hw1-tests
export PREFIX=hw1-stu_
export STUDENTS_FILE=scripts/students.txt
export DEADLINE=2025-12-31T23:59:59
# metadata 收集参数
export METADATA_REPO=course-test/hw1-metadata
export METADATA_BRANCH=main
export METADATA_TOKEN=<your-metadata-token>
# 可选：LLM
export DEEPSEEK_API_KEY=<your-deepseek-key>
export DEEPSEEK_API_BASE=https://api.deepseek.com
export LLM_MODEL=deepseek-chat
EOF
source ~/.bashrc
```

## 🛡️ Push 次数限制与元数据安全

### 限制 Push 次数

- 通过 `data/gitea/custom_hooks/limit_submission_hook.sh` 对所有学生仓库安装 pre-receive 钩子，默认最多允许 **3 次** push 到 `main`。
- 教师账号（`hblu` / `course-test`）推送不会触发计数，可继续批量同步模板。
- 计数文件位于 `./data/gitea/submission_limits`。
- 常用指令：
  - 安装/更新钩子：`env -i PATH=$PATH HOME=$HOME /bin/bash ./scripts/install_submission_limit_hook.sh`
  - 重置某些仓库：`env -i PATH=$PATH HOME=$HOME /bin/bash ./scripts/reset_submission_attempts.sh hw1-stu_sit001`
  - 调整上限：编辑 `scripts/limit_submission_hook.sh` 或在 runner 环境中设置 `MAX_SUBMISSIONS=5`

### 私有化存储 metadata

- Workflow 不再在日志或 artifact 中展示 `metadata.json`。
- 生成的 metadata 会自动上传到私有仓库 `course-test/hw1-metadata`，路径：
  ```
  records/<course-test__hw1-stu_xxx>/<workflow>_<run>.json
  ```
- 在 `data/runner/config.yaml`（以及 `docker-compose.yml`）中设置以下环境变量：

  ```yaml
  RUNNER_METADATA_REPO: course-test/hw1-metadata
  RUNNER_METADATA_TOKEN: <PAT，建议与 RUNNER_TESTS_TOKEN 共用>
  RUNNER_METADATA_BRANCH: main
  ```

- 重启 runner (`docker compose restart runner`) 使配置生效。
- 教师可以直接 clone `hw1-metadata` 或通过 API 下载，再由 `collect_grades.py` 等脚本集中处理成绩。
- 为避免重复修改配置，可运行 `./scripts/update_runner_envs.sh --username <USER> --token <TOKEN>` 自动生成 `data/runner/config.yaml`/`.env` 并重启。每次更新测试凭据后，先验证 `python scripts/test_private_repo_access.py` 能访问 `hw1-tests`。

## 🐛 常见问题

### Q1: API Token 无效或权限不足

**症状**：
```
✗ API Token 无效或权限不足 (HTTP 403)
```

**解决方案**：
1. 在终端运行 `echo $GITEA_ADMIN_TOKEN` 确认变量已生效
2. 确保 Token 有足够权限（见上文"生成 Gitea Token"）
3. 尝试重新生成 Token

### Q2: Python 依赖未安装

**症状**：
```
✗ requests 未安装
✗ python-dotenv 未安装
```

**解决方案**：
```bash
pip3 install requests python-dotenv
```

### Q3: 学生列表文件格式错误

**症状**：
生成仓库或添加协作者时出错

**解决方案**：
检查 `scripts/students.txt` 格式：
- 每行一个学生
- 格式：`student_id` 或 `student_id,username,email`
- 文件末尾需要有换行符

### Q4: hw1-template 和 hw1-tests 可以直接使用吗？

**答案**：**可以！**

根据检查结果：
- ✅ hw1-template 包含所有必需文件
- ✅ hw1-tests 包含隐藏测试和数据
- ✅ 多语言示例（Java, R）已创建
- ✅ 所有脚本和工具都已就绪

只需：
1. 推送到 Gitea
2. 配置 Secrets
3. 生成学生仓库

## 📚 相关文档

- [COURSE_TEMPLATE_GUIDE.md](COURSE_TEMPLATE_GUIDE.md) - 创建新课程模板
- [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md) - 所有脚本说明
- [MULTILANG_SUMMARY.md](MULTILANG_SUMMARY.md) - 多语言系统实现
- [GRADING_METADATA_SPEC.md](GRADING_METADATA_SPEC.md) - JSON 格式规范

## 🎓 下一步

1. ✅ 运行 `./check_config.sh` 确保配置正确
2. 📤 推送 `hw1-template` 和 `hw1-tests` 到 Gitea
3. 🏷️ 标记 `hw1-template` 为模板仓库
4. 🔒 设置 `hw1-tests` 为私有仓库
5. 🔑 在 Gitea 中配置 Secrets
6. 👥 运行 `python3 scripts/generate_repos.py` 生成学生仓库
7. 🤝 运行 `./scripts/add_collaborators.sh` 添加协作者
8. 📊 等待学生提交，然后运行 `./scripts/quick_collect.sh` 收集成绩

祝使用顺利！

