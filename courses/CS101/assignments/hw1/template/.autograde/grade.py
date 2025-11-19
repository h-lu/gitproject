#!/usr/bin/env python3
"""
编程题评分脚本

解析 JUnit XML 报告，计算分数，考虑迟交扣分，生成 grade.json 和 summary.md
"""

import argparse
import xml.etree.ElementTree as ET
import json
import subprocess
import os
import time
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量（支持从 .env 文件或环境变量读取）
load_dotenv()


def commit_ts():
    """获取最后一次提交的时间戳（Unix 时间戳）"""
    try:
        out = subprocess.check_output(
            ["git", "log", "-1", "--format=%ct"], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return int(out)
    except Exception:
        return int(time.time())


def parse_junit(junit_path):
    """
    解析 JUnit XML 报告
    
    Returns
    -------
    passed : int
        通过的测试数
    total : int
        总测试数
    fails : list
        失败的测试名称列表
    """
    if not os.path.exists(junit_path):
        return (0, 0, [])
    
    try:
        root = ET.parse(junit_path).getroot()
        total = 0
        passed = 0
        fails = []
        
        for testsuite in root.iter("testsuite"):
            for testcase in testsuite.iter("testcase"):
                total += 1
                # 检查是否有 failure、error 或 skipped 子元素
                if list(testcase):
                    classname = testcase.get("classname", "")
                    name = testcase.get("name", "")
                    full_name = f"{classname}.{name}" if classname else name
                    fails.append(full_name)
                else:
                    passed += 1
        
        return (passed, total, fails)
    except Exception as e:
        print(f"Error parsing JUnit XML: {e}", file=sys.stderr)
        return (0, 0, [])


def calculate_late_penalty(deadline_str):
    """
    计算迟交扣分
    
    Parameters
    ----------
    deadline_str : str
        ISO 格式的截止时间（如 "2025-03-15T23:59:59+08:00"）
    
    Returns
    -------
    penalty : float
        扣分数（0-30）
    """
    if not deadline_str:
        return 0.0
    
    try:
        # 解析截止时间（支持多种格式）
        deadline_str = deadline_str.strip()
        # 移除时区信息（简化处理）
        if '+' in deadline_str:
            deadline_str = deadline_str.split('+')[0]
        elif 'Z' in deadline_str:
            deadline_str = deadline_str.replace('Z', '')
        
        # 解析时间
        if 'T' in deadline_str:
            dl = time.mktime(time.strptime(deadline_str[:19], "%Y-%m-%dT%H:%M:%S"))
        else:
            dl = time.mktime(time.strptime(deadline_str[:19], "%Y-%m-%d %H:%M:%S"))
        
        commit_time = commit_ts()
        late_sec = max(0, commit_time - dl)
        days = late_sec / 86400
        
        # 扣分规则：第一天 10 分，之后每天 5 分，最多 30 分
        if days > 0:
            penalty = min(30.0, 10.0 + 5.0 * days)
        else:
            penalty = 0.0
        
        return round(penalty, 2)
    except Exception as e:
        print(f"Error calculating late penalty: {e}", file=sys.stderr)
        return 0.0


def main():
    parser = argparse.ArgumentParser(description="Grade programming assignments from JUnit XML")
    parser.add_argument("--junit", required=True, help="Path to JUnit XML file")
    parser.add_argument("--out", default="grade.json", help="Output JSON file")
    parser.add_argument("--summary", default="summary.md", help="Output summary markdown file")
    parser.add_argument("--bonus", default=None, help="Optional bonus file (e.g., lintr.rds)")
    args = parser.parse_args()
    
    # 解析 JUnit XML
    passed, total, fails = parse_junit(args.junit)
    
    # 计算基础分数
    if total > 0:
        base_score = 100.0 * (passed / total)
    else:
        base_score = 0.0
    
    # 计算迟交扣分
    deadline = os.getenv("DEADLINE", "")
    penalty = calculate_late_penalty(deadline)
    
    # 最终分数
    final_score = max(0.0, round(base_score - penalty, 2))
    
    # 生成 grade.json
    grade_data = {
        "score": final_score,
        "base_score": round(base_score, 2),
        "penalty": penalty,
        "passed": passed,
        "total": total,
        "fails": fails,
        "timestamp": int(time.time())
    }
    
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(grade_data, f, ensure_ascii=False, indent=2)
    
    # 生成 summary.md
    with open(args.summary, "w", encoding="utf-8") as f:
        f.write("# 成绩报告\n\n")
        f.write(f"- **通过用例**：{passed}/{total}\n")
        f.write(f"- **原始分**：{base_score:.2f}/100\n")
        if penalty > 0:
            f.write(f"- **迟交扣分**：-{penalty:.2f}\n")
        f.write(f"- **最终分**：**{final_score:.2f}/100**\n\n")
        
        if fails:
            f.write("## 未通过的测试\n\n")
            for fail in fails:
                f.write(f"- {fail}\n")
            f.write("\n")
        
        if deadline:
            f.write(f"## 截止时间\n\n")
            f.write(f"- 截止时间：{deadline}\n")
            commit_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(commit_ts()))
            f.write(f"- 提交时间：{commit_time_str}\n")
    
    print(f"Grading complete: {final_score:.2f}/100 ({passed}/{total} tests passed)")


if __name__ == "__main__":
    main()


