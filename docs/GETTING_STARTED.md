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

5.  **获取管理员 Token**:
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
