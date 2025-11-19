# 🤖 Gitea Automated Grading System

基于 Gitea Actions 的多课程自动评分系统，支持 Python、Java、R 和 LLM 评分。

> **📌 重要提示**: 本系统已重构为多课程/多作业模式。每个课程和作业都通过 `courses/` 目录下的 YAML 配置文件管理。

## ✨ 主要特性

- 🎓 **多课程支持**: 每个课程独立管理，拥有独立的 Gitea 组织
- 📝 **多作业管理**: 每个课程可以有多个作业，配置独立
- 🤖 **自动评分**: 基于 Gitea Actions 的 CI/CD 评分流水线
- 🧪 **多语言支持**: Python、Java、R
- 💬 **LLM 评分**: 支持使用大语言模型评分简答题
- 📊 **成绩收集**: 自动收集所有学生成绩到 CSV

## 📚 文档

完整文档位于 `docs/` 目录：

-   **[👉 快速开始](docs/GETTING_STARTED.md)**: 系统配置和运行第一个课程
-   **[🎓 教师指南](docs/INSTRUCTOR_GUIDE.md)**: 管理课程和作业
-   **[📖 学生指南](docs/STUDENT_GUIDE.md)**: 学生提交作业流程

## 🚀 快速开始 (多课程示例)

```bash
# 1. 启动服务
docker-compose up -d

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 设置 GITEA_URL、GITEA_ADMIN_TOKEN 等

# 2.5 同步 Runner 配置
./scripts/sync_runner_config.sh
docker-compose restart runner

# 3. 创建课程
mkdir -p courses/CS101
# 创建课程配置和学生列表（参考文档）

# 4. 生成学生仓库
python3 scripts/generate_repos.py --course courses/CS101 --assignment hw1

# 5. 收集成绩
python3 scripts/collect_grades.py --course courses/CS101 --assignment hw1 --output grades.csv
```

详细步骤请参考 [快速开始指南](docs/GETTING_STARTED.md)。

## 📁 项目结构

```
GitProject/
├── courses/                    # 课程目录
│   └── CS101/                 # 课程 ID
│       ├── course_config.yaml # 课程配置
│       ├── students.txt       # 学生名单
│       └── assignments/       # 作业目录
│           └── hw1/           # 作业 ID
│               ├── config.yaml    # 作业配置
│               ├── template/      # 学生起始代码
│               └── tests/         # 私有测试
├── scripts/                   # 管理脚本
│   ├── generate_repos.py     # 生成学生仓库
│   ├── collect_grades.py     # 收集成绩
│   ├── create_users.py       # 批量创建用户
│   ├── delete_repos.py       # 删除仓库
│   ├── sync_runner_config.sh # 同步 .env 到 Runner 配置
│   └── ...                   # 其他工具脚本
├── docs/                      # 文档
├── docker-compose.yml         # Docker 配置
└── .env.example              # 环境变量模板
```

## 🔑 核心概念

### 多课程架构

- **课程 (Course)**: 每个课程有独立的 Gitea 组织（如 `CS101-2025Fall`）
- **作业 (Assignment)**: 每个作业有独立的模板仓库、测试仓库和学生仓库
- **配置文件**: 使用 YAML 文件管理课程和作业元数据
- **自动命名**: 仓库名自动根据作业 ID 生成（如 `hw1-template`, `hw1-tests`, `hw1-stu_student1`）

### 工作流程

1. **教师**: 创建课程和作业配置 → 运行生成脚本 → 学生仓库自动创建
2. **学生**: 克隆仓库 → 完成作业 → 推送代码 → 自动评分
3. **教师**: 运行收集脚本 → 获取所有学生成绩

## 🛠️ 技术栈

- **Gitea**: Git 仓库托管和 Gitea Actions CI/CD
- **Docker**: 容器化部署
- **Python**: 管理脚本和评分逻辑
- **PostgreSQL**: Gitea 数据库

## 📖 更多信息

- [教师指南](docs/INSTRUCTOR_GUIDE.md) - 如何管理课程和作业
- [学生指南](docs/STUDENT_GUIDE.md) - 如何提交作业
- [开发者指南](docs/DEVELOPER_GUIDE.md) - 系统架构和故障排除
- [脚本文档](scripts/README.md) - 所有脚本的详细使用说明

## 📄 License

MIT License
