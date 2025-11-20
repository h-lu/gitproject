# 🔧 快速开始

本指南将帮助您配置 Gitea 自动评分系统并运行第一个课程。

## 1. 前置要求

-   **Docker & Docker Compose**: 确保服务器上已安装这两个工具。
-   **Python 3.10+**: 用于运行管理脚本。
-   **Git**: 用于版本控制。

## 2. 环境配置

1.  **克隆仓库**:
    ```bash
    git clone <your-repo-url>
    cd GitProject
    ```

2.  **配置 `.env`**:
    复制示例环境文件并编辑：
    ```bash
    cp .env.example .env
    vim .env
    ```
    *   设置 `GITEA_URL` 为您服务器的地址（例如 `http://192.168.1.100:3000`）。
    *   设置 `GITEA_ADMIN_TOKEN` 为管理员令牌（下一步获取）。
    *   设置 `EXTERNAL_GITEA_HOST` 为外部可访问的地址（例如 `192.168.1.100:3000`）。

3.  **启动服务**:
    ```bash
    docker-compose up -d
    ```
    这将启动 Gitea、PostgreSQL 和 Actions Runner。

4.  **初始化 Gitea**:
    *   访问 `http://<your-ip>:3000`。
    *   完成安装（数据库设置应从 docker-compose.yml 预填）。
    *   创建第一个管理员账户（例如 `gitea_admin`）。

## 3. Runner 配置

**重要**：Runner 需要访问私有的 `tests` 仓库和元数据仓库，必须配置环境变量。

### 方法：使用同步脚本（推荐）

1. **创建 Runner Token**（在 Gitea 中获取）:
   - 权限：`read:repository`（访问私有测试）
   
2. **创建 Metadata Token**（在 Gitea 中获取）:
   - 权限：`write:repository`（上传成绩元数据）

3. **在 `.env` 中配置**:
   ```bash
   RUNNER_TESTS_USERNAME=hblu
   RUNNER_TESTS_TOKEN=your_tests_token_here
   RUNNER_METADATA_REPO=CS101-2025Fall/course-metadata
   RUNNER_METADATA_TOKEN=your_metadata_token_here
   RUNNER_METADATA_BRANCH=main
   ```

4. **同步到 Runner**:
   ```bash
   ./scripts/sync_runner_config.sh
   docker-compose restart runner
   ```

此脚本会将 `.env` 中的 `RUNNER_*` 变量同步到 Runner 容器的 `.runner` 文件。

## 4. 创建第一个课程

### 4.1 课程结构

```bash
courses/CS101/
├── course_config.yaml    # 课程配置
├── students.txt          # 学生列表
└── assignments/
    ├── hw_python/       # Python 作业
    │   ├── config.yaml
    │   ├── template/    # 学生仓库模板
    │   └── tests/       # 私有测试
    ├── hw_java/         # Java 作业
    └── hw_r/            # R 作业
```

### 4.2 创建课程配置

创建 `courses/CS101/course_config.yaml`:

```yaml
organization: "CS101-2025Fall"
admin_users:
  - "gitea_admin"
metadata_repo: "course-metadata"  # 可选，默认为 course-metadata
```

### 4.3 添加学生

创建 `courses/CS101/students.txt`:

```
20250001,alice
20250002,bob
```

格式：`学号,Gitea用户名`

## 6. 收集成绩

学生提交作业后，使用以下命令收集成绩：

### 使用快速收集脚本

```bash
./scripts/quick_collect.sh -c courses/CS101 -a hw_python
```

### 使用 Python 脚本

```bash
python3 scripts/collect_grades.py \
  --course courses/CS101 \
  --assignment hw_python \
  --output grades_hw_python.csv
```

成绩将保存到 CSV 文件，包含每个学生的编程题、LLM 和客观题分数。

## 7. 同步评分脚本（可选）

如果你修改了 `scripts/autograde/` 中的评分脚本，可以使用以下命令同步到所有作业：

```bash
# 同步到所有课程
python3 scripts/sync_autograde.py

# 仅同步指定课程
python3 scripts/sync_autograde.py --course courses/CS101
```

这会将 `scripts/autograde/` 的内容复制到每个作业的 `template/.autograde/` 目录。

---

**恭喜！** 🎉 您已成功配置 Gitea 自动评分系统。

**下一步**：
- 📖 阅读 [教师指南](INSTRUCTOR_GUIDE.md) 了解如何管理作业
- 🔧 阅读 [开发者指南](DEVELOPER_GUIDE.md) 了解系统架构
- 👨‍🎓 分享 [学生指南](STUDENT_GUIDE.md) 给学生学生仓库

## 5. 生成学生仓库

### 5.1 生成 Python 作业仓库

```bash
python3 scripts/generate_repos.py \
  --course courses/CS101 \
  --assignment hw_python
```

这会：
1. 创建组织 `CS101-2025Fall`（如果不存在）
2. 创建模板仓库 `hw_python-template`
3. 创建私有测试仓库 `hw_python-tests`
4. 为每个学生生成仓库 `hw_python-stu_20250001`, `hw_python-stu_20250002` 等
5. **自动复制** `scripts/autograde/` 到模板的 `.autograde/` 目录

### 5.2 生成 Java 作业仓库

```bash
python3 scripts/generate_repos.py \
  --course courses/CS101 \
  --assignment hw_java
```

### 5.3 生成 R 作业仓库

```bash
python3 scripts/generate_repos.py \
  --course courses/CS101 \
  --assignment hw_r
```
    *   登录 Gitea，进入 **用户设置 > 应用 > 生成新令牌**。
    *   令牌名称：`admin-script-token`
    *   选择以下权限：
        *   `write:admin` - 管理用户和组织
        *   `write:organization` - 管理组织
        *   `write:repository` - 管理仓库
        *   `read:user` - 读取用户信息
    *   复制生成的令牌，更新 `.env` 文件中的 `GITEA_ADMIN_TOKEN`。

6.  **配置 Runner 注册令牌**:
    *   在 Gitea 管理面板中: **站点管理 → Actions → Runners**
    *   点击"创建新令牌"，复制令牌
    *   更新 `.env` 文件中的 `RUNNER_REGISTRATION_TOKEN`

7.  **配置 Runner 环境变量**:
    所有 Runner 相关配置统一在 `.env` 文件中管理：
    ```bash
    # Runner 访问私有仓库的凭据
    RUNNER_TESTS_USERNAME=your_gitea_username
    RUNNER_TESTS_TOKEN=your_tests_token
    
    # LLM 评分配置（可选，如需简答题评分）
    LLM_API_KEY=your_deepseek_api_key
    LLM_API_URL=https://api.deepseek.com/v1/chat/completions
    LLM_MODEL=deepseek-chat
    ```
    
    **同步配置到 Runner**:
    ```bash
    # 运行同步脚本
    ./scripts/sync_runner_config.sh
    
    # 重启 Runner 使配置生效
    docker-compose restart runner
    ```
    
    > ⚠️ **重要**: 每次修改 `.env` 中的 Runner 相关配置后，都需要运行同步脚本并重启 Runner。

## 3. 初始化第一个课程

1.  **创建课程目录**:
    ```bash
    mkdir -p courses/CS101
    ```

2.  **创建课程配置**:
    创建 `courses/CS101/course_config.yaml`：
    ```yaml
    name: "计算机科学导论"
    organization: "CS101-2025Fall"
    admins: ["your_gitea_username"]
    ```

3.  **添加学生**:
    创建 `courses/CS101/students.txt`：
    ```text
    20250001,student1
    20250002,student2
    ```

4.  **创建作业**:
    创建 `courses/CS101/assignments/hw1/config.yaml`：
    ```yaml
    title: "作业 1"
    deadline: "2025-12-01T23:59:59"
    language: "python"
    ```
    *   将模板代码放在 `courses/CS101/assignments/hw1/template/`。
    *   将测试放在 `courses/CS101/assignments/hw1/tests/`。

## 4. 生成仓库

运行生成脚本以在 Gitea 中创建组织和仓库：

```bash
export GITEA_ADMIN_TOKEN=your_token
python3 scripts/generate_repos.py --course courses/CS101 --assignment hw1
```

🎉 **成功！** 您现在拥有一个运行中的课程和学生仓库。
