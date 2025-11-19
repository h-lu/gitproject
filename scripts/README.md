# 🛠️ 脚本使用指南

本目录包含用于管理 Gitea 自动评分系统的各种脚本。所有脚本已更新为多课程模式。

## 📋 核心脚本

### 1. `generate_repos.py` - 生成学生仓库

批量创建学生作业仓库，包括模板仓库、测试仓库和学生仓库。

#### 用法

```bash
python3 scripts/generate_repos.py \
  --course courses/CS101 \
  --assignment hw1
```

#### 参数

- `--course` (必需): 课程目录路径 (例如: `courses/CS101`)
- `--assignment` (必需): 作业 ID (例如: `hw1`)
- `--students` (可选): 覆盖默认学生列表文件
- `--dry-run` (可选): 试运行模式，不实际创建仓库
- `--skip-collaborator` (可选): 跳过添加学生为协作者

#### 功能

1. 从课程配置读取组织名
2. 创建 Gitea 组织（如果不存在）
3. 创建/更新 `{assignment}-template` 公开仓库
4. 创建/更新 `{assignment}-tests` 私有仓库
5. 为每个学生创建私有仓库 `{assignment}-stu_{student_id}`
6. 添加学生为仓库协作者（除非使用 `--skip-collaborator`）

---

### 2. `collect_grades.py` - 收集成绩

从元数据仓库收集所有学生的成绩并生成 CSV 文件。

#### 用法

```bash
python3 scripts/collect_grades.py \
  --course courses/CS101 \
  --assignment hw1 \
  --output grades.csv
```

#### 参数

- `--course` (必需): 课程目录路径
- `--assignment` (必需): 作业 ID
- `--output` (可选): 输出 CSV 文件路径 (默认: `grades.csv`)
- `--metadata-repo` (可选): 覆盖自动推断的元数据仓库
- `--metadata-branch` (可选): 元数据仓库分支 (默认: `main`)

#### 输出格式

生成的 CSV 文件包含以下列：
- `student_repo`: 学生仓库名
- `student_id`: 学生ID
- `score`: 总分
- `status`: 状态 (success/failed)
- `timestamp`: 评分时间戳
- `components`: 各评分组件详情

---

### 3. `create_users.py` - 批量创建用户

批量创建 Gitea 用户账号。

#### 用法

```bash
# 试运行
python3 scripts/create_users.py \
  --students courses/CS101/students.txt \
  --dry-run

# 创建用户
python3 scripts/create_users.py \
  --students courses/CS101/students.txt \
  --password "InitialPassword123"
```

#### 参数

- `--students` (必需): 学生列表文件路径
- `--password` (可选): 默认密码 (默认: `12345678`)
- `--dry-run` (可选): 试运行模式
- `--skip-existing` (可选): 跳过已存在的用户

#### 学生列表格式

支持三种格式：

```text
# 格式 1: 只有用户名（会自动生成邮箱）
sit001
sit002

# 格式 2: 用户名,邮箱
sit001,sit001@school.edu
sit002,sit002@school.edu

# 格式 3: 用户名,邮箱,全名
sit001,sit001@school.edu,张三
sit002,sit002@school.edu,李四
```

---

### 4. `delete_repos.py` - 删除仓库

批量删除学生作业仓库（谨慎使用）。

#### 用法

```bash
# 试运行（推荐先查看将删除哪些仓库）
python3 scripts/delete_repos.py \
  --course courses/CS101 \
  --assignment hw1 \
  --dry-run

# 删除仓库
python3 scripts/delete_repos.py \
  --course courses/CS101 \
  --assignment hw1
```

#### 参数

- `--course` (必需): 课程目录路径
- `--assignment` (必需): 作业 ID
- `--dry-run` (可选): 试运行模式
- `--force` (可选): 跳过确认提示

⚠️ **警告**: 此操作不可逆！所有代码、Issues、PRs 都将被永久删除。

---

### 5. `update_workflows_all_branches.py` - 更新工作流

更新所有学生仓库的 workflow 文件（从模板同步）。

#### 用法

```bash
python3 scripts/update_workflows_all_branches.py \
  --course courses/CS101 \
  --assignment hw1
```

#### 参数

- `--course` (必需): 课程目录路径
- `--assignment` (必需): 作业 ID
- `--repo` (可选): 只更新指定的仓库
- `--branch` (可选): 只更新指定的分支（需要配合 `--repo`）

#### 功能

- 从模板仓库的 `.gitea/workflows/` 同步工作流文件
- 同时更新 `.autograde/` 目录中的辅助脚本
- 支持更新所有分支或指定分支

---

## 🔧 辅助脚本

### `quick_collect.sh` - 快速收集成绩

`collect_grades.py` 的便捷包装脚本，自动生成带时间戳的输出文件并显示统计信息。

#### 用法

```bash
./scripts/quick_collect.sh -c courses/CS101 -a hw1
```

#### 参数

- `-c`: 课程路径 (必需)
- `-a`: 作业 ID (必需)
- `-o`: 输出文件名 (可选，默认自动生成)

---

### `add_collaborators.sh` - 添加协作者

批量添加学生为仓库协作者。通常在学生注册 Gitea 后使用。

#### 用法

```bash
./scripts/add_collaborators.sh -c courses/CS101 -a hw1
```

#### 参数

- `-c`: 课程路径 (必需)
- `-a`: 作业 ID (必需)

---

### `sync_runner_config.sh` - 同步 Runner 配置

从 `.env` 文件同步配置到 Gitea Actions Runner 的 `config.yaml`。

#### 用法

```bash
./scripts/sync_runner_config.sh
```

#### 功能

- 读取 `.env` 中的配置
- 更新 `data/runner/config.yaml` 中的 `envs` 部分
- 同步以下变量：
  - `EXTERNAL_GITEA_HOST`
  - `RUNNER_TESTS_USERNAME`
  - `RUNNER_TESTS_TOKEN`
  - `LLM_API_KEY`
  - `LLM_API_URL`
  - `LLM_MODEL`

#### 何时使用

- 修改了 `.env` 中的任何 Runner 相关配置
- 初次部署系统
- 更换 API Key 或访问凭据

#### 完整流程

```bash
# 1. 编辑 .env 文件
vim .env

# 2. 同步配置
./scripts/sync_runner_config.sh

# 3. 重启 Runner
docker-compose restart runner
```

> ⚠️ **重要**: 由于 Gitea act_runner 的限制，`config.yaml` 的 `envs` 部分不支持变量替换。每次修改 `.env` 后都必须运行此脚本同步配置。


---

## 📝 完整工作流示例

### 创建新课程和作业

```bash
# 1. 创建课程目录结构
mkdir -p courses/CS101

# 2. 创建课程配置
cat > courses/CS101/course_config.yaml << EOF
name: "计算机科学导论"
organization: "CS101-2025Fall"
admins: ["instructor"]
EOF

# 3. 创建学生列表
cat > courses/CS101/students.txt << EOF
20250001,student1
20250002,student2
EOF

# 4. 创建作业目录
mkdir -p courses/CS101/assignments/hw1/{template,tests}

# 5. 创建作业配置
cat > courses/CS101/assignments/hw1/config.yaml << EOF
title: "作业 1"
deadline: "2025-12-01T23:59:59"
language: "python"
grading:
  enable_llm: true
  enable_tests: true
EOF

# 6. 准备模板代码和测试（手动）
# 编辑 courses/CS101/assignments/hw1/template/
# 编辑 courses/CS101/assignments/hw1/tests/

# 7. 创建用户账户
python3 scripts/create_users.py \
  --students courses/CS101/students.txt \
  --password "Welcome2025"

# 8. 生成仓库
python3 scripts/generate_repos.py \
  --course courses/CS101 \
  --assignment hw1

# 9. 收集成绩（在学生提交后）
python3 scripts/collect_grades.py \
  --course courses/CS101 \
  --assignment hw1 \
  --output grades_hw1.csv
```

---

## 🔑 环境变量

脚本需要以下环境变量（在 `.env` 文件或系统环境中设置）：

### 必需变量

- `GITEA_URL`: Gitea 服务器地址 (例如: `http://192.168.1.100:3000`)
- `GITEA_ADMIN_TOKEN`: Gitea 管理员访问令牌

### Runner 配置变量

这些变量在 `.env` 中配置，通过 `sync_runner_config.sh` 同步到 Runner：

- `EXTERNAL_GITEA_HOST`: 外部可访问的 Gitea 地址（用于 Workflow，例如: `192.168.1.100:3000`）
- `RUNNER_TESTS_USERNAME`: 访问测试仓库的用户名
- `RUNNER_TESTS_TOKEN`: 访问测试仓库的 Token

### LLM 评分配置（可选）

如果使用简答题 LLM 评分功能：

- `LLM_API_KEY`: LLM API 密钥（例如 DeepSeek API Key）
- `LLM_API_URL`: LLM API 端点（例如: `https://api.deepseek.com/v1/chat/completions`）
- `LLM_MODEL`: LLM 模型名称（例如: `deepseek-chat`）

### 配置同步流程

```bash
# 1. 编辑 .env 文件
vim .env

# 2. 同步 Runner 配置
./scripts/sync_runner_config.sh

# 3. 重启 Runner
docker-compose restart runner
```

---

## ⚠️ 重要提示

1. **Token 权限**: `GITEA_ADMIN_TOKEN` 需要以下权限：
   - `write:admin` - 创建组织和用户
   - `write:organization` - 管理组织
   - `write:repository` - 管理仓库
   - `read:user` - 读取用户信息

2. **备份**: 删除操作不可逆，请务必在执行 `delete_repos.py` 前使用 `--dry-run` 确认

3. **Runner 配置**: 
   - **重要**: Runner 环境变量现在通过 `.env` 统一管理
   - 每次修改 `.env` 中的 Runner 相关配置后，必须运行 `./scripts/sync_runner_config.sh` 并重启 Runner
   - 不再建议直接编辑 `docker-compose.yml` 或 `data/runner/config.yaml`

4. **多课程模式**: 所有脚本都需要 `--course` 和 `--assignment` 参数，不再支持旧的环境变量模式

---

## 📚 更多文档

- [教师指南](../docs/INSTRUCTOR_GUIDE.md) - 课程管理和作业发布
- [学生指南](../docs/STUDENT_GUIDE.md) - 学生提交作业流程
- [开发者指南](../docs/DEVELOPER_GUIDE.md) - 系统架构和故障排除
