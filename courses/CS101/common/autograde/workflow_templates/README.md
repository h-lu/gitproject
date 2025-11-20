# Workflow 模板

本目录包含不同编程语言的 Gitea Actions workflow 模板。

## 可用模板

| 文件 | 语言 | 容器 | 测试框架 |
|------|------|------|----------|
| `python.yml` | Python | python:3.11 | pytest |
| `java.yml` | Java | maven:3.9-eclipse-temurin-17 | JUnit 5 |
| `r.yml` | R | r-base:4.3 | testthat |

## 使用方法

### 1. 选择模板

根据你的编程语言选择对应的模板：

```bash
# 对于 Python 作业
cp .autograde/workflow_templates/python.yml .gitea/workflows/grade.yml

# 对于 Java 作业
cp .autograde/workflow_templates/java.yml .gitea/workflows/grade.yml

# 对于 R 作业
cp .autograde/workflow_templates/r.yml .gitea/workflows/grade.yml
```

### 2. 自定义配置

编辑 `.gitea/workflows/grade.yml` 根据需要修改：

- **容器版本**：修改 `container:` 字段
- **超时时间**：修改 `timeout-minutes:`
- **依赖安装**：修改 "Install dependencies" 步骤
- **测试命令**：修改测试运行步骤

### 3. 配置 Secrets

确保在 Gitea 仓库设置中配置了以下 Secrets：

- `TESTS_TOKEN`：用于访问隐藏测试仓库的 token（可选）
- `EXTERNAL_GITEA_HOST`：外部访问的 Gitea 地址（可选）

## Python 模板 (python.yml)

### 特点
- 使用 `python:3.11` 容器
- 自动安装 `requirements.txt` 中的依赖
- 使用 `run_tests.py` 运行 pytest
- 支持代码覆盖率

### 自定义选项
```yaml
# 修改 Python 版本
container: python:3.10  # 或 python:3.9

# 添加额外的依赖
- name: Install dependencies
  run: |
    pip install -r requirements.txt
    pip install numpy pandas  # 额外的包
```

## Java 模板 (java.yml)

### 特点
- 使用 `maven:3.9-eclipse-temurin-17` 容器
- Maven 自动管理依赖（通过 `pom.xml`）
- JUnit 5 测试框架
- 自动提取 Surefire 报告

### 自定义选项
```yaml
# 修改 JDK 版本
container: maven:3.9-eclipse-temurin-11  # Java 11
container: maven:3.9-eclipse-temurin-21  # Java 21

# 自定义 Maven 命令
run: |
  mvn clean test -B -DskipTests=false
```

### Maven 配置提示

确保 `pom.xml` 中配置了 Surefire 插件：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <version>3.2.2</version>
    <configuration>
        <reportsDirectory>${project.build.directory}/surefire-reports</reportsDirectory>
    </configuration>
</plugin>
```

## R 模板 (r.yml)

### 特点
- 使用 `r-base:4.3` 容器
- 自动从 `DESCRIPTION` 安装依赖
- testthat 测试框架
- JUnitReporter 输出 XML

### 自定义选项
```yaml
# 修改 R 版本
container: r-base:4.2  # 或其他版本

# 修改 CRAN 镜像
run: |
  Rscript -e "install.packages('testthat', repos='https://cran.r-project.org/')"
```

### R 项目结构要求

```
project/
├── DESCRIPTION         # 包依赖定义
├── R/                  # R 源代码
└── tests/
    └── testthat/       # testthat 测试
```

## 通用 Workflow 流程

所有模板都遵循相同的流程：

1. **安装系统依赖**（git, rsync 等）
2. **检出代码** - 克隆学生仓库
3. **安装语言依赖** - 根据语言安装包
4. **获取隐藏测试**（可选）- 从私有仓库获取
5. **运行测试** - 生成 JUnit XML
6. **评分** - 解析 XML，计算分数
7. **生成元数据** - 创建 JSON metadata
8. **发布评论** - 在 PR 中发布结果

## 高级配置

### 添加代码质量检查

```yaml
- name: Run linter
  run: |
    # Python: pylint, flake8
    pip install pylint
    pylint src/
    
    # Java: checkstyle
    mvn checkstyle:check
    
    # R: lintr
    Rscript -e "lintr::lint_package()"
```

### 自定义评分规则

修改 `grade.py` 的调用参数：

```yaml
- name: Grade
  run: |
    python3 ./.autograde/grade.py \
      --junit junit.xml \
      --out grade.json \
      --summary summary.md \
      --bonus bonus.json  # 可选的加分项
```

### 多个测试套件

```yaml
- name: Run public tests
  run: |
    pytest tests_public/ --junit-xml=public.xml

- name: Run hidden tests
  run: |
    pytest tests_hidden/ --junit-xml=hidden.xml

- name: Merge test results
  run: |
    python3 ./.autograde/merge_junit.py public.xml hidden.xml -o junit.xml
```

## 故障排查

### 测试无法运行
- 检查测试目录路径是否正确
- 确认依赖是否正确安装
- 查看 Actions 日志中的错误信息

### JUnit XML 未生成
- Python: 确保 pytest 命令包含 `--junit-xml`
- Java: 检查 Surefire 插件配置
- R: 确认 testthat >= 3.0.0

### 元数据为空
- 检查 `grade.json` 是否生成
- 确认 `LANGUAGE` 环境变量设置正确
- 查看 `create_minimal_metadata.py` 的输出

## 相关文档

- [运行测试脚本](../run_tests.py) - 通用测试运行器
- [评分脚本](../grade.py) - JUnit XML 解析和评分
- [元数据生成](../create_minimal_metadata.py) - JSON 元数据
- [示例](../../examples/) - 各语言的完整示例

---

最后更新: 2025-11-13

