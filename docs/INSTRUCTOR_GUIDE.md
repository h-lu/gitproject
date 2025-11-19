# 🎓 教师指南

本指南介绍如何管理课程、创建作业和评分学生作业。

## 0. 环境准备

在开始管理课程前，请确保已完成系统配置：

### 配置 Gitea Admin Token
1.  登录 Gitea 管理员账户
2.  进入 **用户设置 > 应用 > 生成新令牌**
3.  选择权限：`write:admin`, `write:organization`, `write:repository`, `read:user`
4.  将生成的 Token 保存到 `.env` 文件的 `GITEA_ADMIN_TOKEN` 变量中

### 配置 Runner 环境变量
编辑 `docker-compose.yml` 中的 `runner` 服务：
```yaml
runner:
  environment:
    RUNNER_TESTS_USERNAME: your_username    # 有权访问测试仓库的用户
    RUNNER_TESTS_TOKEN: your_token          # 该用户的访问令牌
    RUNNER_METADATA_REPO: org/repo-name    # （可选）元数据仓库
    RUNNER_METADATA_TOKEN: your_token      # （可选）元数据令牌
```

重启服务：
```bash
docker-compose restart runner
```

## 1. 管理课程

课程组织在 `courses/` 目录中。每个课程都有自己的文件夹（例如 `courses/CS101`）。

### 课程配置
编辑 `courses/<COURSE_ID>/course_config.yaml`：

```yaml
name: "计算机科学导论"
organization: "CS101-2025Fall"  # 此课程的 Gitea 组织名
admins: ["instructor_alice", "ta_bob"]
```

### 学生名单
编辑 `courses/<COURSE_ID>/students.txt`。格式：`学号,用户名`

```text
20250001,student1
20250002,student2
```

### 创建用户账户
如果学生还没有 Gitea 账户，可以批量创建：

```bash
python3 scripts/create_users.py \
  --students courses/CS101/students.txt \
  --password "InitialPassword123"
```

## 2. 创建作业

作业位于 `courses/<COURSE_ID>/assignments/<ASSIGNMENT_ID>`。

### 结构
*   `config.yaml`: 作业元数据。
*   `template/`: 提供给学生的起始代码仓库。
*   `tests/`: 包含隐藏测试和答案的私有仓库。

### 作业配置
编辑 `courses/<COURSE_ID>/assignments/<ASSIGNMENT_ID>/config.yaml`：

```yaml
title: "作业 1"
deadline: "2025-12-01T23:59:59"
language: "python"
grading:
  enable_llm: true
  enable_tests: true
```

### 发布作业
生成学生仓库：

```bash
python3 scripts/generate_repos.py \
  --course courses/CS101 \
  --assignment hw1
```

这将：
1.  创建 `CS101-2025Fall` 组织（如果不存在）。
2.  创建/更新 `hw1-template` 和 `hw1-tests` 仓库。
3.  为每个学生创建私有仓库（例如 `hw1-stu_student1`）。

## 3. 评分与反馈

当学生推送代码时，评分会通过 Gitea Actions 自动进行。

### 查看成绩
将所有成绩收集到 CSV 文件：

```bash
python3 scripts/collect_grades.py \
  --course courses/CS101 \
  --assignment hw1 \
  --output grades.csv
```

### 手动触发
您可以通过进入学生仓库 > **Actions** > 选择工作流 > **运行工作流** 手动触发评分。
