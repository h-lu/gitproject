#!/usr/bin/env python3
"""
通用测试运行器 - 根据语言配置运行测试并生成 JUnit XML

支持的语言:
- python: pytest
- java: maven (mvn test)
- r: testthat (通过 JUnit Reporter)

环境变量:
- LANGUAGE: 编程语言 (python/java/r)
- TEST_DIR: 测试目录路径
- SOURCE_DIR: 源代码目录路径
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path


def run_python_tests(test_dir, output_xml, **kwargs):
    """运行 Python pytest 测试"""
    cmd = [
        "pytest", test_dir,
        f"--junit-xml={output_xml}",
        "-v", "--tb=short"
    ]
    
    # 添加覆盖率选项（如果指定）
    source_dir = kwargs.get('source_dir')
    if source_dir:
        cmd.extend([
            f"--cov={source_dir}",
            "--cov-report=term-missing",
            "--cov-report=json:coverage.json"
        ])
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result


def run_java_tests(test_dir, output_xml, **kwargs):
    """运行 Java Maven 测试"""
    cmd = ["mvn", "test", "-B"]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    
    # Maven 自动生成 XML 在 target/surefire-reports/
    # 需要复制到指定的输出位置
    surefire_dir = Path("target/surefire-reports")
    if surefire_dir.exists():
        # 合并所有 TEST-*.xml 文件
        import xml.etree.ElementTree as ET
        
        xml_files = list(surefire_dir.glob("TEST-*.xml"))
        if xml_files:
            # 简单情况：只复制第一个（或合并）
            import shutil
            if len(xml_files) == 1:
                shutil.copy(xml_files[0], output_xml)
            else:
                # 合并多个 XML 文件（简化版本）
                root = ET.Element("testsuites")
                for xml_file in xml_files:
                    tree = ET.parse(xml_file)
                    root.append(tree.getroot())
                
                tree = ET.ElementTree(root)
                tree.write(output_xml, encoding='utf-8', xml_declaration=True)
    
    return result


def run_r_tests(test_dir, output_xml, **kwargs):
    """运行 R testthat 测试"""
    # R 脚本：使用 testthat 的 JUnitReporter
    # 注意：需要安装 testthat (>= 3.0.0)
    
    r_script = f"""
library(testthat)

# 配置 JUnit reporter
reporter <- JunitReporter$new(file = '{output_xml}')

# 运行测试
test_dir(
  path = '{test_dir}',
  reporter = reporter,
  stop_on_failure = FALSE
)
"""
    
    # 将脚本写入临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.R', delete=False) as f:
        f.write(r_script)
        script_path = f.name
    
    try:
        cmd = ["Rscript", script_path]
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=False)
        return result
    finally:
        # 清理临时文件
        if os.path.exists(script_path):
            os.remove(script_path)


def main():
    parser = argparse.ArgumentParser(
        description="通用测试运行器 - 支持 Python/Java/R"
    )
    parser.add_argument(
        "--language",
        required=True,
        choices=["python", "java", "r"],
        help="编程语言"
    )
    parser.add_argument(
        "--test-dir",
        required=True,
        help="测试目录路径"
    )
    parser.add_argument(
        "--output-xml",
        default="test-results.xml",
        help="JUnit XML 输出文件路径"
    )
    parser.add_argument(
        "--source-dir",
        help="源代码目录（用于覆盖率）"
    )
    
    args = parser.parse_args()
    
    # 语言对应的运行器
    runners = {
        "python": run_python_tests,
        "java": run_java_tests,
        "r": run_r_tests,
    }
    
    if args.language not in runners:
        print(f"❌ Unsupported language: {args.language}", file=sys.stderr)
        sys.exit(1)
    
    # 运行测试
    result = runners[args.language](
        args.test_dir,
        args.output_xml,
        source_dir=args.source_dir
    )
    
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

