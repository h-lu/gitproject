# 多语言作业示例

本目录包含不同编程语言的作业示例，展示如何使用通用评分框架创建不同语言的编程作业。

## 目录结构

```
examples/
├── r_example/          # R 语言示例
│   ├── R/             # R 源代码
│   ├── tests/         # testthat 测试
│   ├── DESCRIPTION    # R 包描述文件
│   └── problem.yaml   # 作业配置
├── java_example/       # Java 语言示例
│   ├── src/           # Maven 标准结构
│   ├── pom.xml        # Maven 配置
│   └── problem.yaml   # 作业配置
└── README.md          # 本文件
```

## R 语言示例 (r_example/)

### 作业内容
实现基础统计函数：
- `calculate_mean()` - 计算均值
- `calculate_variance()` - 计算方差
- `standardize()` - 标准化向量

### 测试框架
- **testthat** (>= 3.0.0)
- JUnit XML 报告格式

### 使用方法
1. 复制 `r_example/` 到新的作业目录
2. 修改 `R/basic_stats.R` 中的函数实现
3. 修改 `tests/testthat/test_basic_stats.R` 中的测试用例
4. 使用 `.autograde/workflow_templates/r.yml` 作为 workflow

### 本地测试
```r
# 安装依赖
install.packages("testthat")

# 运行测试
library(testthat)
test_dir("tests/testthat")
```

---

## Java 语言示例 (java_example/)

### 作业内容
实现基础算法：
- `fibonacci()` - 斐波那契数列
- `isPrime()` - 质数判断
- `reverseArray()` - 数组反转
- `findMax()` - 查找最大值

### 测试框架
- **JUnit 5** (jupiter)
- Maven Surefire 插件

### 使用方法
1. 复制 `java_example/` 到新的作业目录
2. 修改 `src/main/java/com/example/BasicAlgorithms.java`
3. 修改 `src/test/java/com/example/BasicAlgorithmsTest.java`
4. 使用 `.autograde/workflow_templates/java.yml` 作为 workflow

### 本地测试
```bash
# 编译和运行测试
mvn test

# 查看测试报告
ls target/surefire-reports/
```

---

## 创建新的语言作业

### 步骤 1：复制示例
```bash
# 复制对应语言的示例
cp -r examples/java_example my-new-assignment
cd my-new-assignment
```

### 步骤 2：修改配置
编辑 `problem.yaml`：
- 修改 `assignment.id` 和 `title`
- 调整评分点配置
- 设置资源限制

### 步骤 3：实现作业内容
- 修改源代码文件
- 更新测试用例
- 更新 README 说明

### 步骤 4：配置 Workflow
```bash
# 复制对应的 workflow 模板
cp ../.autograde/workflow_templates/java.yml .gitea/workflows/grade.yml
```

### 步骤 5：测试
1. 本地运行测试确保通过
2. 提交到 Gitea 触发 CI
3. 查看 Actions 运行结果

---

## 支持的语言

| 语言   | 测试框架 | 容器镜像                      | 状态 |
|--------|----------|-------------------------------|------|
| Python | pytest   | python:3.11                   | ✅   |
| Java   | JUnit 5  | maven:3.9-eclipse-temurin-17  | ✅   |
| R      | testthat | r-base:4.3                    | ✅   |

---

## 通用评分框架

所有语言共享相同的评分流程：

1. **运行测试** → 生成 JUnit XML
2. **解析 XML** → 计算通过率
3. **生成元数据** → 标准 JSON 格式
4. **发布评论** → PR 评论 + JSON 元数据
5. **收集成绩** → CSV 报告

详见 `../.autograde/` 目录中的通用脚本。

---

## 相关文档

- [课程模板创建指南](../../COURSE_TEMPLATE_GUIDE.md)
- [成绩元数据格式](../../GRADING_METADATA_SPEC.md)
- [脚本索引](../../SCRIPTS_INDEX.md)

---

## 常见问题

### Q: 如何添加新的编程语言？
A: 
1. 在 `.autograde/run_tests.py` 中添加语言支持
2. 创建对应的 workflow 模板
3. 在 `examples/` 中添加示例

### Q: 测试框架必须输出 JUnit XML 吗？
A: 是的。通用评分框架依赖 JUnit XML 格式来解析测试结果。大多数测试框架都支持输出 JUnit XML。

### Q: 可以混合多种语言吗？
A: 可以，但不推荐。建议每个作业使用单一语言，为不同课程创建独立的模板。

---

最后更新: 2025-11-13

