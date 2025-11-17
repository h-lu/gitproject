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

## 🚀 快速开始

### 1. 检查和配置系统

```bash
# 运行配置检查脚本
./check_config.sh
```

### 2. 阅读文档

📚 **所有文档都在 `docs/` 目录下**，推荐从这里开始：

**[👉 docs/ENV_SETUP_GUIDE.md](docs/ENV_SETUP_GUIDE.md)** - 环境配置和使用指南

## 📚 完整文档

| 文档 | 说明 |
|------|------|
| [docs/ENV_SETUP_GUIDE.md](docs/ENV_SETUP_GUIDE.md) | 🔧 **环境配置和快速开始**（推荐从这里开始） |
| [docs/GITEA_ACTIONS_SECRETS.md](docs/GITEA_ACTIONS_SECRETS.md) | 🔐 **批量配置 Actions Secrets**（自动化配置 TESTS_USERNAME / TESTS_TOKEN） |
| [docs/TOKEN_PERMISSIONS_GUIDE.md](docs/TOKEN_PERMISSIONS_GUIDE.md) | 🎫 Gitea API Token 权限配置指南 |
| [docs/COURSE_TEMPLATE_GUIDE.md](docs/COURSE_TEMPLATE_GUIDE.md) | 🎓 创建新课程模板（Java/R/Python） |
| [docs/SCRIPTS_INDEX.md](docs/SCRIPTS_INDEX.md) | 🛠️ 所有脚本的详细说明和使用方法 |
| [docs/GRADING_METADATA_SPEC.md](docs/GRADING_METADATA_SPEC.md) | 📊 成绩 JSON 格式规范 |
| [docs/MULTILANG_SUMMARY.md](docs/MULTILANG_SUMMARY.md) | 🌐 多语言评分系统实现总结 |
| [docs/README.md](docs/README.md) | 📖 详细的系统说明文档 |

## 📂 项目结构

```
GitProject/
├── docs/                       # 📚 所有文档
│   ├── README.md              # 详细系统说明
│   ├── ENV_SETUP_GUIDE.md     # 配置和使用指南 ⭐
│   ├── COURSE_TEMPLATE_GUIDE.md
│   ├── SCRIPTS_INDEX.md
│   ├── GRADING_METADATA_SPEC.md
│   └── MULTILANG_SUMMARY.md
│
├── scripts/                    # 🛠️ 管理脚本
│   ├── create_course_template.py
│   ├── generate_repos.py
│   ├── add_collaborators.sh
│   ├── collect_grades.py
│   ├── quick_collect.sh
│   └── update_workflows_all_branches.py
│
├── hw1-template/              # 📦 作业模板（Python + LLM）
│   ├── .gitea/workflows/      # CI/CD 配置
│   ├── .autograde/            # 评分脚本
│   ├── examples/              # Java 和 R 示例
│   ├── src/                   # Python 源代码
│   └── tests_public/          # 公开测试
│
├── hw1-tests/                 # 🔒 隐藏测试仓库
│   └── python/                # Python 隐藏测试
│
└── check_config.sh            # 配置检查脚本
```

## 🎯 使用流程

1. **配置检查**: 运行 `./check_config.sh`
2. **阅读文档**: 查看 [docs/ENV_SETUP_GUIDE.md](docs/ENV_SETUP_GUIDE.md)
3. **配置环境变量**: 在 shell 中导出 `GITEA_URL`、`GITEA_ADMIN_TOKEN`、`ORGANIZATION` 等变量
4. **推送模板**: 将 `hw1-template` 和 `hw1-tests` 推送到 Gitea
5. **生成仓库**: 运行 `python3 scripts/generate_repos.py`
6. **添加协作者**: 运行 `./scripts/add_collaborators.sh`
7. **学生提交 & 自动评分**: 学生直接 push 到自己的 `hwX-stu_xxx` 仓库，workflow（`on: push`）会自动克隆私有测试并生成评分；教师需要手动重跑时，可使用 workflow dispatch。
8. **收集成绩**: 运行 `./scripts/quick_collect.sh`

> **Runner 环境变量**：由于学生无权读取仓库 Secrets，需要在 `act_runner` 服务（或 docker-compose runner 容器）中配置
> `RUNNER_TESTS_USERNAME` / `RUNNER_TESTS_TOKEN`，以便 workflow 拉取 `hwX-tests`。具体做法见 `docs/WORKFLOW_TOKEN_FIX.md`。

## 🆘 获取帮助

- **配置问题**: 查看 [docs/ENV_SETUP_GUIDE.md](docs/ENV_SETUP_GUIDE.md) 的"常见问题"部分
- **脚本使用**: 查看 [docs/SCRIPTS_INDEX.md](docs/SCRIPTS_INDEX.md)
- **创建新课程**: 查看 [docs/COURSE_TEMPLATE_GUIDE.md](docs/COURSE_TEMPLATE_GUIDE.md)
- **运行检查**: 执行 `./check_config.sh` 自动诊断

## 📊 系统状态

运行配置检查：
```bash
./check_config.sh
```

这会检查：
- ✅ Gitea 服务器连接
- ✅ API Token 有效性
- ✅ `hw1-template` 和 `hw1-tests` 完整性
- ✅ 管理脚本
- ✅ Python 依赖

## 🌟 核心特性详解

### 多语言支持

系统支持为不同编程语言创建课程模板：

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

### 环境变量配置

使用以下环境变量控制脚本行为（可写入 shell profile，或在执行命令前 `export`）：

```bash
export GITEA_URL=http://49.234.193.192:3000
export GITEA_ADMIN_TOKEN=your_token
export ORGANIZATION=course-test
export TEMPLATE_REPO=hw1-template
export PREFIX=hw1-stu_
```

### 自动化工作流

学生提交 PR 后，系统自动：
1. 运行测试（公开 + 隐藏）
2. 计算分数（含迟交扣分）
3. LLM 评分简答题
4. 生成 JSON 元数据
5. 发布评论到 PR

## 📄 许可证

MIT License

## 🙏 致谢

- [Gitea](https://gitea.io/) - 开源 Git 服务
- [Gitea Actions](https://docs.gitea.io/en-us/usage/actions/overview/) - CI/CD 系统
- [act_runner](https://gitea.com/gitea/act_runner) - Actions Runner

---

**开始使用**: 阅读 [docs/ENV_SETUP_GUIDE.md](docs/ENV_SETUP_GUIDE.md) 📖

