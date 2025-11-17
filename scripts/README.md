# 运维脚本

## generate_repos.py

批量生成学生作业仓库。

### 使用方法

1. 准备学生列表文件（参考 `students.txt.example`）：
```bash
20250001,student1
20250002,student2
```

2. 运行脚本：
```bash
# 仅创建仓库，不添加协作者（推荐）
python scripts/generate_repos.py --students scripts/students.txt --skip-collaborator

# 或：创建仓库并添加协作者（需要学生已注册 Gitea）
python scripts/generate_repos.py --students scripts/students.txt
```

3. 添加协作者（在学生注册 Gitea 后）：
```bash
./scripts/add_collaborators.sh
```

4. 可选参数：
- `--prefix`: 仓库名前缀（默认：`hw1-stu`）
- `--skip-collaborator`: 跳过添加协作者
- `--dry-run`: 试运行模式，不实际创建仓库

### 环境变量

- `GITEA_URL`: Gitea 服务器地址
- `GITEA_ADMIN_TOKEN`: Gitea 管理员 Token
- `ORGANIZATION`: 组织名称
- `TEMPLATE_REPO`: 模板仓库名称

## create_users.py

批量创建 Gitea 用户账号。

### 使用方法

⚠️ **重要**: 需要包含 `write:admin` 权限的管理员 Token！

```bash
# 试运行（查看将要创建的用户）
python scripts/create_users.py --students scripts/students.txt --dry-run

# 创建用户（默认密码 12345678）
python scripts/create_users.py --students scripts/students.txt --skip-existing

# 指定密码
python scripts/create_users.py --students scripts/students.txt --password mypass123
```

### 文件格式

`students.txt` 支持三种格式：

```txt
# 格式 1: 只有用户名
sit001
sit002

# 格式 2: 用户名,邮箱
sit001,sit001@school.edu

# 格式 3: 用户名,邮箱,全名
sit001,sit001@school.edu,张三
```

### 输出文件

脚本会生成 `user_accounts.txt`，包含所有账号信息。

📚 详细文档: [USER_CREATION_GUIDE.md](../USER_CREATION_GUIDE.md)

## update_workflows.py

批量更新学生仓库的 workflow 文件（从模板仓库同步）。

### 使用方法

```bash
# 从模板仓库更新所有学生仓库的 workflow
python scripts/update_workflows.py \
  --template-dir /path/to/hw1-template \
  --prefix hw1-stu

# 试运行（查看将要更新的仓库）
python scripts/update_workflows.py \
  --template-dir /path/to/hw1-template \
  --prefix hw1-stu \
  --dry-run

# 只更新文件，不推送（用于测试）
python scripts/update_workflows.py \
  --template-dir /path/to/hw1-template \
  --prefix hw1-stu \
  --skip-push
```

### 功能说明

- 自动查找所有匹配前缀的仓库
- 从模板仓库同步 `.gitea/workflows/` 目录下的所有文件
- 自动提交并推送到 `main` 分支
- 保留学生的提交历史（不会丢失数据）

### 使用场景

当模板仓库的 workflow 更新后（例如添加了 JSON 元数据生成），可以使用此脚本批量更新所有学生仓库，无需重新创建仓库。

### 自动评分触发方式

- 所有 workflow 统一使用 `on: push`（学生 push 即刻触发评分）
- 额外提供 `workflow_dispatch`，方便教师在 Web UI 手动重跑
- 学生若创建 PR，仅用于代码 review；评分结果以 push 为准
- 由于学生无权读取仓库 Secrets，需要在 act_runner 服务中设置
  `RUNNER_TESTS_USERNAME` / `RUNNER_TESTS_TOKEN` 环境变量，workflow 直接使用这组凭据拉取私有测试

## test_private_repo_access.py

快速验证当前环境变量 `GITEA_TESTS_USERNAME` / `GITEA_TESTS_TOKEN` 是否能成功访问 `hw1-tests`。

```bash
python3 scripts/test_private_repo_access.py
```

脚本会：
- 自动读取环境变量
- 对 `hw1-tests` 执行 `git ls-remote`
- 输出成功/失败结果，方便在部署前排查凭据问题

## delete_repos.py

批量删除学生作业仓库（用于清理测试仓库）。

### 使用方法

```bash
# 试运行（不实际删除）
python scripts/delete_repos.py --prefix hw1-stu --dry-run

# 删除仓库
python scripts/delete_repos.py --prefix hw1-stu

# 强制删除（跳过确认）
python scripts/delete_repos.py --prefix hw1-stu --force
```

### 安全特性

- 默认需要输入 `DELETE` 确认
- 支持 `--dry-run` 试运行模式
- 显示将被删除的仓库列表

⚠️ **警告**: 删除操作不可逆！请谨慎使用。

## collect_grades.py

收集所有学生作业的成绩。

### 使用方法

```bash
python scripts/collect_grades.py --output grades.csv
```

### 输出格式

CSV 文件包含以下列：
- `student_id`: 学号
- `repo`: 仓库名称
- `status`: 工作流状态
- `score`: 成绩（需要从 artifact 中提取）
- `timestamp`: 提交时间

## install_submission_limit_hook.sh

为所有学生仓库安装 **push 次数限制** 的 pre-receive 钩子，用于控制自动评分次数。

```bash
# 安装/更新钩子（推荐）
env -i PATH=$PATH HOME=$HOME /bin/bash ./scripts/install_submission_limit_hook.sh

# 只对某几个仓库生效
env -i PATH=$PATH HOME=$HOME /bin/bash ./scripts/install_submission_limit_hook.sh hw1-stu_sit001.git
```

钩子安装后：

- 默认最多允许 **3 次** push 到 `main`（可通过 `MAX_SUBMISSIONS` 环境变量调整）。
- 计数保存在 `/data/submission_limits/*.count`（宿主机路径：`./data/gitea/submission_limits`）。
- 管理员账号（`hblu` / `course-test`）的推送不会计入次数。

## reset_submission_attempts.sh

重置指定仓库（或全部仓库）的提交次数：

```bash
# 重置所有仓库
env -i PATH=$PATH HOME=$HOME /bin/bash ./scripts/reset_submission_attempts.sh

# 仅重置部分仓库
env -i PATH=$PATH HOME=$HOME /bin/bash ./scripts/reset_submission_attempts.sh hw1-stu_sit004 hw1-stu_sit005
```

执行后会删除对应的 `*.count` 文件，学生随即可再次 push。

## 注意事项

1. 确保已导出必要的环境变量
2. `GITEA_ADMIN_TOKEN` 需要管理员权限
3. 学生列表文件使用 UTF-8 编码


