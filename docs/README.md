# 📚 Gitea 自动评分系统文档

欢迎使用 Gitea 自动评分系统文档。本系统旨在管理多个课程的编程作业，通过单元测试和 LLM 提供自动评分功能。

## 🚀 快速链接

| 指南 | 说明 |
|------|------|
| **[快速开始](GETTING_STARTED.md)** | 🔧 配置系统并运行您的第一个课程 |
| **[教师指南](INSTRUCTOR_GUIDE.md)** | 🎓 如何管理课程、作业和成绩 |
| **[学生指南](STUDENT_GUIDE.md)** | 📖 学生提交作业指南 |
| **[开发者指南](DEVELOPER_GUIDE.md)** | 🛠️ 脚本和架构技术细节 |

## 📂 系统概览

系统使用层级结构来组织课程和作业：

```text
courses/
├── CS101/                      # 课程 ID
│   ├── course_config.yaml      # 课程元数据
│   ├── students.txt            # 学生名单
│   └── assignments/
│       ├── hw1/                # 作业 ID
│       │   ├── config.yaml     # 作业元数据
│       │   ├── template/       # 起始代码
│       │   └── tests/          # 私有测试
│       └── ...
```

## 🆘 需要帮助？

如果您遇到问题，请查看 **[开发者指南](DEVELOPER_GUIDE.md)** 获取故障排除提示，或联系系统管理员。
