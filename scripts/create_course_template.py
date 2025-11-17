#!/usr/bin/env python3
"""
课程模板生成器

用法:
  python3 scripts/create_course_template.py \\
    --name java-programming \\
    --language java \\
    --title "Java 程序设计" \\
    --output java-course-template

功能:
- 复制基础模板结构
- 配置语言特定的文件
- 生成对应的 workflow
- 创建示例问题和测试
"""

import argparse
import shutil
import os
import sys
from pathlib import Path


# 语言配置
LANGUAGE_CONFIGS = {
    "python": {
        "container": "python:3.11",
        "test_framework": "pytest",
        "dependencies_file": "requirements.txt",
        "source_dir": "src",
        "test_dir": "tests_public",
        "example_dir": "examples/python_ml",  # 使用现有的 Python 示例
    },
    "java": {
        "container": "maven:3.9-eclipse-temurin-17",
        "test_framework": "junit5",
        "dependencies_file": "pom.xml",
        "source_dir": "src/main/java",
        "test_dir": "src/test/java",
        "example_dir": "examples/java_example",
    },
    "r": {
        "container": "r-base:4.3",
        "test_framework": "testthat",
        "dependencies_file": "DESCRIPTION",
        "source_dir": "R",
        "test_dir": "tests/testthat",
        "example_dir": "examples/r_example",
    },
}


def create_template(name, language, title, output_dir, base_template="hw1-template"):
    """创建新的课程模板"""
    
    if language not in LANGUAGE_CONFIGS:
        print(f"❌ 不支持的语言: {language}")
        print(f"   支持的语言: {', '.join(LANGUAGE_CONFIGS.keys())}")
        sys.exit(1)
    
    config = LANGUAGE_CONFIGS[language]
    base_path = Path(__file__).parent.parent / base_template
    output_path = Path(output_dir)
    
    if not base_path.exists():
        print(f"❌ 基础模板不存在: {base_path}")
        sys.exit(1)
    
    if output_path.exists():
        print(f"⚠️  目标目录已存在: {output_path}")
        response = input("是否覆盖? (y/N): ")
        if response.lower() != 'y':
            print("❌ 操作已取消")
            sys.exit(1)
        shutil.rmtree(output_path)
    
    print(f"📦 创建课程模板: {name}")
    print(f"   语言: {language}")
    print(f"   标题: {title}")
    print(f"   输出: {output_path}")
    print()
    
    # 步骤 1: 复制基础结构
    print("1️⃣  复制基础结构...")
    output_path.mkdir(parents=True)
    
    # 复制 .autograde 目录
    shutil.copytree(
        base_path / ".autograde",
        output_path / ".autograde"
    )
    print("   ✓ .autograde/ 已复制")
    
    # 创建 .gitea/workflows 目录
    (output_path / ".gitea" / "workflows").mkdir(parents=True)
    
    # 步骤 2: 复制语言特定的示例
    print(f"2️⃣  复制 {language} 示例...")
    example_path = base_path / config["example_dir"]
    
    if language == "python":
        # Python 使用现有的结构
        for item in ["src", "tests_public", "data", "questions", "answers"]:
            src = base_path / item
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, output_path / item)
                else:
                    shutil.copy2(src, output_path / item)
        
        # 复制依赖文件
        for file in ["requirements.txt", "pytest.ini"]:
            src = base_path / file
            if src.exists():
                shutil.copy2(src, output_path / file)
        
        print("   ✓ Python 源代码和测试已复制")
    
    elif example_path.exists():
        # R 和 Java 从示例目录复制
        for item in example_path.iterdir():
            if item.name not in [".git", "__pycache__", "problem.yaml"]:
                if item.is_dir():
                    shutil.copytree(item, output_path / item.name)
                else:
                    shutil.copy2(item, output_path / item.name)
        print(f"   ✓ {language.upper()} 示例已复制")
    else:
        print(f"   ⚠️  示例目录不存在，需要手动创建源代码")
    
    # 步骤 3: 生成 workflow 文件
    print("3️⃣  生成 workflow...")
    workflow_template = base_path / ".autograde" / "workflow_templates" / f"{language}.yml"
    if workflow_template.exists():
        shutil.copy2(
            workflow_template,
            output_path / ".gitea" / "workflows" / "grade.yml"
        )
        print(f"   ✓ 使用 {language}.yml 模板")
    else:
        print(f"   ⚠️  workflow 模板不存在，需要手动创建")
    
    # 步骤 4: 生成 problem.yaml
    print("4️⃣  生成 problem.yaml...")
    problem_yaml = f"""# {title} - 作业配置

assignment:
  id: {name}
  title: {title}
  language: {language}
  type: programming

description: |
  {title}课程作业。
  
  请在此填写作业的详细说明。

language_config:
  test_framework: {config['test_framework']}
  dependencies_file: {config['dependencies_file']}
  source_dir: {config['source_dir']}
  test_dir: {config['test_dir']}

grading:
  max_score: 100
  components:
    - name: programming
      weight: 100
      type: auto
      language: {language}

constraints:
  - 请在此列出作业的约束条件

resources:
  timeout: 120
  mem: 512m

# 如需添加简答题，取消注释以下部分：
# additional_components:
#   - name: llm_essay
#     weight: 30
#     type: llm
#     questions: [q1, q2, q3]
"""
    
    with open(output_path / "problem.yaml", "w", encoding="utf-8") as f:
        f.write(problem_yaml)
    print("   ✓ problem.yaml 已生成")
    
    # 步骤 5: 生成 README.md
    print("5️⃣  生成 README.md...")
    readme_content = f"""# {title}

## 作业说明

本次作业旨在帮助你掌握 {language.upper()} 编程的基本技能。

## 成绩构成

- **编程题**：100 分

## 提交规范

1. **代码提交**：在 `{config['source_dir']}/` 目录中实现所需功能
2. **提交方式**：完成代码后，执行以下命令提交：

```bash
git add .
git commit -m "完成作业"
git push
```

## 测试说明

- **公开测试**：`{config['test_dir']}/` 目录下的测试用例可以本地运行
- **隐藏测试**：提交后会自动运行隐藏测试用例

## 本地测试

### {language.upper()} 环境

"""
    
    if language == "python":
        readme_content += """```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests_public/ -v
```
"""
    elif language == "java":
        readme_content += """```bash
# 编译和运行测试
mvn clean test

# 查看测试报告
ls target/surefire-reports/
```
"""
    elif language == "r":
        readme_content += """```r
# 安装依赖
install.packages(c("testthat", "devtools"))

# 运行测试
library(testthat)
test_dir("tests/testthat")
```
"""
    
    readme_content += """
## 评分与反馈

- 每次 `git push` 后会自动触发批改流程
- 批改结果会在 Actions 中显示
- 评分结果会以评论形式发布在 Pull Request 中

## 注意事项

1. **禁止作弊**：不得抄袭他人代码
2. **代码质量**：注意代码可读性与注释
3. **及时提交**：迟交会按规则扣分

祝学习顺利！
"""
    
    with open(output_path / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("   ✓ README.md 已生成")
    
    # 步骤 6: 创建 .gitignore
    print("6️⃣  生成 .gitignore...")
    gitignore_common = """# 编译产物
*.pyc
__pycache__/
*.class
*.o
*.so

# IDE
.idea/
.vscode/
*.swp
*.swo
*~

# 系统文件
.DS_Store
Thumbs.db

# 日志
*.log

# 临时文件
*.tmp
tmp/
temp/
"""
    
    gitignore_lang = {
        "python": """
# Python 特定
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
venv/
env/
""",
        "java": """
# Java/Maven 特定
target/
.classpath
.project
.settings/
*.jar
!**/src/**/*.jar
""",
        "r": """
# R 特定
.Rhistory
.RData
.Rproj.user
*.Rproj
"""
    }
    
    gitignore_content = gitignore_common + gitignore_lang.get(language, "")
    
    with open(output_path / ".gitignore", "w", encoding="utf-8") as f:
        f.write(gitignore_content)
    print("   ✓ .gitignore 已生成")
    
    # 完成
    print()
    print("✅ 课程模板创建完成！")
    print()
    print("📝 下一步:")
    print(f"   1. cd {output_path}")
    print("   2. 修改源代码和测试用例")
    print("   3. 编辑 problem.yaml 配置评分点")
    print("   4. 编辑 README.md 补充作业说明")
    print("   5. 初始化 Git 仓库并推送到 Gitea")
    print()
    print(f"📚 参考文档:")
    print(f"   - workflow 模板: {output_path}/.autograde/workflow_templates/")
    print(f"   - 语言示例: {base_path}/examples/{language}_example/")
    print(f"   - 完整指南: COURSE_TEMPLATE_GUIDE.md")


def main():
    parser = argparse.ArgumentParser(
        description="课程模板生成器 - 快速创建不同编程语言的作业模板",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 创建 Java 课程模板
  python3 scripts/create_course_template.py \\
    --name java-ds-hw1 \\
    --language java \\
    --title "数据结构（Java）" \\
    --output java-ds-hw1-template
  
  # 创建 R 统计课程模板
  python3 scripts/create_course_template.py \\
    --name stats-r-hw1 \\
    --language r \\
    --title "统计学与R语言" \\
    --output stats-r-hw1-template
"""
    )
    
    parser.add_argument(
        "--name",
        required=True,
        help="作业名称（用作 assignment ID，如 java-ds-hw1）"
    )
    parser.add_argument(
        "--language",
        required=True,
        choices=["python", "java", "r"],
        help="编程语言"
    )
    parser.add_argument(
        "--title",
        required=True,
        help="作业标题（如 \"数据结构（Java）\"）"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="输出目录路径"
    )
    parser.add_argument(
        "--base-template",
        default="hw1-template",
        help="基础模板目录（默认: hw1-template）"
    )
    
    args = parser.parse_args()
    
    create_template(
        args.name,
        args.language,
        args.title,
        args.output,
        args.base_template
    )


if __name__ == "__main__":
    main()

