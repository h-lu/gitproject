# 🤖 Gitea 自动评分系统

基于 Gitea Actions 的课程作业自动评分系统，支持多种编程语言（Python/Java/R）和 LLM 简答题评分。

## ✨ 特性

- 🌐 **多语言支持**: Python、Java、R 编程作业自动评分
- 🤖 **智能评分**: 单元测试 + LLM 简答题评分
- 🔒 **私有测试**: 隐藏测试用例，防止学生针对性优化
- 📊 **成绩收集**: 一键批量收集所有学生成绩，统一 JSON 格式
- 👥 **批量管理**: 自动化创建用户、仓库、配置权限
- 💬 **自动反馈**: 评分结果自动评论到 Pull Request
- 🎓 **模板系统**: 快速创建不同课程的作业模板

## 📚 文档导航

| 文档 | 说明 |
|------|------|
| [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) | 🔧 环境变量、RUNNER/Token 配置与整体流程 |
| [COURSE_TEMPLATE_GUIDE.md](COURSE_TEMPLATE_GUIDE.md) | 🎓 创建 Java/Batch/... 模板库 |
| [SCRIPTS_INDEX.md](SCRIPTS_INDEX.md) | 🛠️ 所有脚本的用途（包括 collect_grades/quick_collect） |
| [GRADING_METADATA_SPEC.md](GRADING_METADATA_SPEC.md) | 📊 metadata.json 的结构与字段 |
| [MULTILANG_SUMMARY.md](MULTILANG_SUMMARY.md) | 🌐 多语言评分系统实现总结 |

## 🚀 快速开始

### 1. 启动服务

```bash
docker compose up -d
```

访问 Gitea: `http://YOUR_IP:3000`

### 2. 检查和配置系统

```bash
# 运行配置检查脚本
./check_config.sh
```

**推荐阅读**: [ENV_SETUP_GUIDE.md](ENV_SETUP_GUIDE.md) - 包含完整的配置和使用流程

### 4. 创建组织和仓库

在 Gitea 中创建：
- 组织（如 `course-test`）
- 模板仓库（如 `hw1-template`）
- 私有测试仓库（如 `hw1-tests`）

### 5. 配置 Secrets

在组织设置中添加以下 Secrets：
- `TESTS_USERNAME`: 拥有私有测试仓库访问权限的管理员账号
- `TESTS_TOKEN`: 对应账号的访问 Token（具备 read:repository）
- `LLM_API_KEY`: DeepSeek API Key
- `LLM_API_URL`: `https://api.deepseek.com/chat/completions`
- `LLM_MODEL`: `deepseek-chat`

### 6. 批量创建学生账号和仓库

```bash
# 准备学生列表
cat > scripts/students.txt <<EOF
sit001
sit002
sit003
EOF

# 创建用户（密码: 12345678）
python scripts/create_users.py --students scripts/students.txt --skip-existing

# 创建仓库
python scripts/generate_repos.py --students scripts/students.txt --skip-collaborator

# 添加协作者权限
./scripts/add_collaborators.sh
```

## ✅ 自动评分与元数据

- 所有 workflow 通过 `push` 事件触发，`act_runner` 读取 `RUNNER_TESTS_USERNAME`/`RUNNER_TESTS_TOKEN` 拉取私有的 `hw1-tests`。
- `metadata.json` 不再公开；每次运行通过 `upload_metadata.py` 上传到 `course-test/hw1-metadata`（路径 `records/{org}__{repo}/{workflow}_{run_id}_{commit}.json`）。
- 为保证元数据上传，请在 `data/runner/config.yaml` / `docker-compose.yml` 中设置 `RUNNER_METADATA_REPO`/`TOKEN`/`BRANCH`，修改后`docker compose restart runner`；也可运行`./scripts/update_runner_envs.sh`自动写入。
- 教师可通过 `python scripts/collect_grades.py --metadata-repo course-test/hw1-metadata` 或 `./scripts/quick_collect.sh` 汇总成绩；学生无法直接访问 `hw1-metadata`。
- 借助 `scripts/install_submission_limit_hook.sh` + `/data/submission_limits` 可限制学生 push 次数（默认 3 次），管理员账号不受限制。

## 📖 完整流程

### 教师端

```bash
# 1. 创建用户和仓库
python scripts/create_users.py --students scripts/students.txt --skip-existing
python scripts/generate_repos.py --students scripts/students.txt --skip-collaborator
./scripts/add_collaborators.sh

# 2. 等待学生 push 到 main（Workflow 仅在 push 事件触发），元数据保存到 hw1-metadata

# 3. 批量收集元数据产生的成绩
./scripts/quick_collect.sh

# 4. 查看 CSV（或导入更多统计工具）
cat grades_hw1-stu_*.csv
```

### 学生端

```bash
# 1. 克隆仓库
git clone http://YOUR_IP:3000/course-test/hw1-stu_sit001.git
cd hw1-stu_sit001

# 2. 可先在 solution 分支开发
git checkout -b solution

# 3. 解决题目并提交
git add .
git commit -m "完成作业"

# 4. 将最终代码推到 main（或合并 solution → main）
git push origin main
```

评分工作流只在 `push` 事件触发，运行结果记录在私有的 `hw1-metadata` 仓库中（学生无权读），教师通过 `collect_grades.py`/`quick_collect.sh` 统一收集。PR 仍可用于代码 review，但元数据不会公开到 PR 评论。

## 🛠️ 管理工具

### 用户管理

```bash
# 批量创建用户
python scripts/create_users.py --students scripts/students.txt

# 支持格式
# sit001                          # 用户名（邮箱自动生成）
# sit001,sit001@school.edu       # 用户名,邮箱
# sit001,sit001@school.edu,张三  # 用户名,邮箱,全名
```

### 仓库管理

```bash
# 生成学生仓库
python scripts/generate_repos.py --students scripts/students.txt --skip-collaborator

# 添加协作者
./scripts/add_collaborators.sh

# 删除仓库
python scripts/delete_repos.py --prefix hw1-stu --dry-run  # 试运行
python scripts/delete_repos.py --prefix hw1-stu --force    # 执行删除
```

### 成绩收集

```bash
# 快速收集（带统计）
./scripts/quick_collect.sh

# 详细收集
python scripts/collect_grades.py --output grades.csv
```

## 📁 项目结构

```
GitProject/
├── docker-compose.yml          # 服务编排
├── hw1-template/              # 作业模板（.gitea/workflows + .autograde）
├── hw1-tests/                # 私有测试仓库
├── scripts/                  # 运维脚本（create_users/generate_repos/collect_grades/quick_collect）
└── docs/                     # 详细文档与指南
```

## 📚 文档索引

- [ENV_SETUP_GUIDE.md](./ENV_SETUP_GUIDE.md) | 环境变量与 Runner/Token 设置
- [COURSE_TEMPLATE_GUIDE.md](./COURSE_TEMPLATE_GUIDE.md) | 多语言课程模板开发
- [SCRIPTS_INDEX.md](./SCRIPTS_INDEX.md) | 脚本用途与调用示例
- [GRADING_METADATA_SPEC.md](./GRADING_METADATA_SPEC.md) | metadata.json 规范
- [MULTILANG_SUMMARY.md](./MULTILANG_SUMMARY.md) | 多语言评分系统概况

## 🔧 系统要求

- Docker & Docker Compose
- Python 3.11+（用于运维脚本）
- 至少 2GB RAM
- 10GB 可用磁盘空间

## ⚙️ 核心组件

- **Gitea 1.22+**: Git 服务器
- **PostgreSQL 16**: 数据库
- **Act Runner**: Actions 执行器
- **DeepSeek API**: LLM 评分

## 🐛 故障排查

### Actions 未运行

```bash
# 检查 Runner 状态
docker compose logs runner

# 重启 Runner
docker compose restart runner
```

### 协作者权限问题

```bash
# 重新添加
./scripts/add_collaborators.sh
```

### Token 权限不足

参考 [ENV_SETUP_GUIDE.md](./ENV_SETUP_GUIDE.md) 重新生成包含所需权限的 Token：
- `write:admin` - 创建用户
- `write:repository` - 创建仓库
- `write:organization` - 管理组织
- `delete:repository` - 删除仓库（可选）

### 文件格式问题

**重要**: `students.txt` 必须以换行符结尾！

```bash
# 检查文件格式
cat -A scripts/students.txt
# 每行应该显示 $ 符号

# 修复文件
echo "" >> scripts/students.txt
```

## 📊 评分系统

### Python 测试评分

- 运行公开测试 + 私有测试
- 支持 pytest 框架
- 自动计算通过率和分数

### LLM 简答题评分

- 使用 DeepSeek API
- 基于参考答案和评分标准
- 包含置信度评估
- 支持人工复核标记

## 🔐 安全建议

1. ✅ 使用强密码并定期更换
2. ✅ Token 设置合理的过期时间
3. ✅ 不要将包含访问凭据的文件（如 `user_accounts.txt`）提交到 Git
4. ✅ 私有测试仓库设为 Private
5. ✅ 定期备份数据库

## 📝 开发者

如需自定义评分逻辑：

- **Python 测试**: 修改 `hw1-template/.autograde/grade.py`
- **LLM 评分**: 修改 `hw1-template/.autograde/llm_grade.py`
- **工作流**: 修改 `hw1-template/.gitea/workflows/*.yml`

## 📄 许可证

MIT License

## 🙏 致谢

- [Gitea](https://gitea.io/) - 自托管 Git 服务
- [Act Runner](https://gitea.com/gitea/act_runner) - Actions 执行器
- [DeepSeek](https://www.deepseek.com/) - LLM API

---

**提示**: 首次使用请按顺序阅读 `ENV_SETUP_GUIDE.md` → `SCRIPTS_INDEX.md` → `COURSE_TEMPLATE_GUIDE.md`

有问题？查阅 [ENV_SETUP_GUIDE.md](./ENV_SETUP_GUIDE.md) 和 [WORKFLOW_TOKEN_FIX.md](./WORKFLOW_TOKEN_FIX.md) 的故障排查章节。
