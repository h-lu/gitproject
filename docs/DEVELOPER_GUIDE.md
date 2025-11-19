# 🛠️ 开发者指南

本指南说明 Gitea 自动评分系统的内部架构和脚本。

## 1. 系统架构

### 核心组件

系统整合了 Gitea、Gitea Actions 和自定义 Python 脚本。

*   **Gitea**: 托管仓库（模板、测试、学生仓库）。
*   **Gitea Actions**: 运行评分的 CI/CD 流水线。
*   **脚本**: 自动化仓库管理和成绩收集。

### 配置管理策略

系统采用**环境变量 + YAML 配置文件**的混合管理策略：

#### 环境变量（`.env` 文件）
用于全局系统配置，主要是 Gitea 连接信息：
*   `GITEA_URL` - Gitea 服务器地址
*   `GITEA_ADMIN_TOKEN` - 管理员 Token（脚本使用）
*   `EXTERNAL_GITEA_HOST` - 外部访问地址（Workflow 使用）

#### YAML 配置文件
用于课程和作业的特定配置：
*   `courses/{course_id}/course_config.yaml` - 课程配置
    *   `organization` - Gitea 组织名（如 `CS101-2025Fall`）
    *   `admins` - 管理员列表
*   `courses/{course_id}/assignments/{assignment_id}/config.yaml` - 作业配置
    *   `title` - 作业标题
    *   `deadline` - 截止时间
    *   `language` - 编程语言
    *   `grading` - 评分选项

#### Runner 环境变量配置

**集中式配置管理**：
所有 Runner 环境变量现在统一在 `.env` 文件中管理：
*   `EXTERNAL_GITEA_HOST` - 外部访问地址（Workflow 使用）
*   `RUNNER_TESTS_USERNAME` - 访问测试仓库的用户名
*   `RUNNER_TESTS_TOKEN` - 访问测试仓库的 Token
*   `LLM_API_KEY` - LLM API 密钥（简答题评分）
*   `LLM_API_URL` - LLM API 端点
*   `LLM_MODEL` - LLM 模型名称

**同步机制**：
由于 Gitea act_runner 的限制，`config.yaml` 的 `envs` 部分不支持变量替换。
使用同步脚本将 `.env` 中的配置同步到 `data/runner/config.yaml`:

```bash
./scripts/sync_runner_config.sh
docker-compose restart runner
```

> ⚠️ **重要**: 每次修改 `.env` 中的 Runner 相关配置后，必须运行同步脚本。

### 工作流程
1.  **生成**: `generate_repos.py --course courses/CS101 --assignment hw1` 读取课程配置并在课程组织中创建学生仓库。
2.  **提交**: 学生推送到他们的私有仓库。
3.  **触发**: `on: push` 事件触发 Gitea Actions 工作流（在 `.gitea/workflows/` 中定义）。
4.  **执行**:
    *   Runner 检出学生代码。
    *   Runner 从组织中克隆私有测试（使用 `RUNNER_TESTS_TOKEN`）。
    *   Runner 执行测试（pytest）和 LLM 评分。
    *   Runner 将反馈发布到 PR 或提交评论。
5.  **收集**: `collect_grades.py --course courses/CS101 --assignment hw1` 扫描元数据仓库（如果配置）或工件以收集分数。

## 2. 脚本参考

### `scripts/sync_runner_config.sh`
从 `.env` 同步配置到 Runner config.yaml。

**用法**:
```bash
./scripts/sync_runner_config.sh
```

**何时使用**:
*   修改了 `.env` 中的任何 Runner 相关配置
*   初次部署
*   更换 API Key

### `scripts/generate_repos.py`
生成学生仓库。

**必需参数**:
*   `--course`: 课程目录路径 (例如: `courses/CS101`)
*   `--assignment`: 作业 ID (例如: `hw1`)

**可选参数**:
*   `--students`: 覆盖默认学生列表文件
*   `--dry-run`: 试运行模式
*   `--skip-collaborator`: 跳过添加协作者

**示例**:
```bash
python3 scripts/generate_repos.py --course courses/CS101 --assignment hw1
```

### `scripts/collect_grades.py`
从元数据收集成绩。

**必需参数**:
*   `--course`: 课程目录路径
*   `--assignment`: 作业 ID

**可选参数**:
*   `--output`: 输出 CSV 文件 (默认: `grades.csv`)
*   `--metadata-repo`: 覆盖自动推断的元数据仓库
*   `--metadata-branch`: 元数据仓库分支 (默认: `main`)

**示例**:
```bash
python3 scripts/collect_grades.py --course courses/CS101 --assignment hw1 --output grades.csv
```

### `scripts/create_users.py`
批量创建 Gitea 用户。

**必需参数**:
*   `--students`: 学生列表文件路径

**可选参数**:
*   `--password`: 新用户的默认密码 (默认: `12345678`)
*   `--dry-run`: 试运行模式
*   `--skip-existing`: 跳过已存在的用户

**示例**:
```bash
python3 scripts/create_users.py --students courses/CS101/students.txt --password "Welcome2025"
```

### `scripts/delete_repos.py`
批量删除学生仓库（谨慎使用）。

**必需参数**:
*   `--course`: 课程目录路径
*   `--assignment`: 作业 ID

**可选参数**:
*   `--dry-run`: 试运行模式
*   `--force`: 跳过确认提示

**示例**:
```bash
python3 scripts/delete_repos.py --course courses/CS101 --assignment hw1 --dry-run
```

### `scripts/update_workflows_all_branches.py`
更新学生仓库的工作流文件。

**必需参数**:
*   `--course`: 课程目录路径
*   `--assignment`: 作业 ID

**可选参数**:
*   `--repo`: 只更新指定仓库
*   `--branch`: 只更新指定分支

**示例**:
```bash
python3 scripts/update_workflows_all_branches.py --course courses/CS101 --assignment hw1
```

## 3. 目录结构

```text
courses/
├── <COURSE_ID>/
│   ├── course_config.yaml
│   ├── students.txt
│   └── assignments/
│       └── <ASSIGNMENT_ID>/
│           ├── config.yaml
│           ├── template/  (学生起始代码)
│           └── tests/     (私有测试)
```

## 4. 故障排除

### Runner 配置问题

**问题**: Runner 无法克隆私有测试仓库
**诊断**:
```bash
# 检查 runner 容器环境变量
docker-compose exec runner env | grep RUNNER_TESTS

# 检查 config.yaml 中的配置
cat data/runner/config.yaml | grep -A 5 "envs:"
```
**解决**:
```bash
# 确保 .env 中配置正确
vim .env

# 同步配置并重启
./scripts/sync_runner_config.sh
docker-compose restart runner
```

### Workflow 环境变量问题

**问题**: Workflow 提示 "LLM_API_KEY not set" 或 "EXTERNAL_GITEA_HOST" 为空
**原因**: Workflow 文件中使用了 `${{ secrets.XXX }}` 覆盖了 runner 的环境变量
**解决**: 从 workflow 文件的 `env:` 块中移除这些 secrets 引用，让 runner 的环境变量自然传递

### Docker 网络问题

**问题**: Job 容器无法解析 `gitea` 主机名
**诊断**:
```bash
# 检查 runner 网络配置
cat data/runner/config.yaml | grep "network:"
```
**解决**: 确保 `data/runner/config.yaml` 中设置了正确的网络：
```yaml
container:
  network: "gitproject_default"
```

### 磁盘空间问题

**问题**: Workflow 失败，提示 "No space left on device"
**诊断**:
```bash
# 检查 Docker 磁盘使用
docker system df
```
**解决**:
```bash
# 清理 Docker build cache
docker builder prune -af

# 清理未使用的镜像和容器
docker system prune -a
```

### 其他常见问题

*   **工作流失败**: 检查 Gitea 中的 Actions 选项卡以查看详细日志
*   **脚本失败**: 确保已设置 `GITEA_ADMIN_TOKEN` 并具有管理员权限
*   **学生仓库未生成**: 检查课程配置文件格式是否正确（YAML 语法）
*   **成绩收集为空**: 确保 workflow 已成功运行并生成了元数据
