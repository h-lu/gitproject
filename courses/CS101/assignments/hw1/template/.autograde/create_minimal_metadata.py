#!/usr/bin/env python3
"""
创建完整的成绩元数据文件

从 grade.json 或 llm_grade.json 生成 metadata.json
包含所有详细信息：未通过的测试、各题详情等
"""

import json
import os
import sys
import re
from datetime import datetime


def extract_student_id():
    """从环境变量或仓库名中提取学生 ID"""
    # 优先从环境变量获取
    student_id = os.getenv("STUDENT_ID")
    if student_id:
        return student_id
    
    # 从仓库名提取（格式：hw1-stu_sit001）
    repo = os.getenv("REPO", "")
    if repo:
        # 匹配 hw1-stu_xxxxx 格式
        match = re.search(r'hw\d+-stu[_-]?([^/]+)', repo)
        if match:
            return match.group(1)
    
    return None


if __name__ == "__main__":
    main()


def extract_assignment_id():

def create_grade_metadata(grade_file='grade.json'):
    """从 grade.json 创建元数据，包含所有详细信息"""
    try:
        with open(grade_file, 'r') as f:
            grade_data = json.load(f)
        
        assignment_id = extract_assignment_id()
        student_id = extract_student_id()
        language = os.getenv("LANGUAGE", "python")
        
        # 提取所有相关信息
        final_score = grade_data.get("final_score", grade_data.get("score", 0))
        base_score = grade_data.get("base_score", final_score)
        penalty = grade_data.get("penalty", 0)
        passed = grade_data.get("passed", 0)
        total = grade_data.get("total", 0)
        fails = grade_data.get("fails", [])
        max_score = grade_data.get("max_score", 100)
        test_framework = grade_data.get("test_framework", "pytest")
        coverage = grade_data.get("coverage")
        raw_score = grade_data.get("raw_score")
        
        # 动态生成 type 字段
        type_map = {
            "python": "programming_python",
            "java": "programming_java",
            "r": "programming_r"
        }
        component_type = type_map.get(language, f"programming_{language}")
        
        component = {
            "type": component_type,
            "language": language,
            "score": round(final_score, 2),
            "max_score": max_score,
            "details": {
                "passed": passed,
                "total": total,
                "base_score": round(base_score, 2),
                "penalty": round(penalty, 2),
                "coverage": round(coverage, 2) if coverage else None,
                "raw_score": round(raw_score, 2) if raw_score else None,
                "failed_tests": fails,
                "test_framework": test_framework
            }
        }
        
        metadata = {
            "version": "1.0",
            "assignment": assignment_id,
            "student_id": student_id,
            "components": [component],
            "total_score": round(final_score, 2),
            "total_max_score": max_score,
            "timestamp": datetime.now().isoformat(),
            "generator": "gitea-autograde"
        }
        
        return metadata
    except Exception as e:
        print(f"Error creating grade metadata: {e}", file=sys.stderr)
        return {}


def create_llm_metadata(llm_grade_file='artifacts/llm_grade.json'):
    """从 llm_grade.json 创建元数据，包含所有详细信息"""
    try:
        with open(llm_grade_file, 'r') as f:
            llm_data = json.load(f)
        
        assignment_id = extract_assignment_id()
        student_id = extract_student_id()
        
        # 提取聚合后的信息
        total_score = llm_data.get("total_score", llm_data.get("total", 0))
        max_score = llm_data.get("max_score", 30)
        need_review = llm_data.get("need_review", False)
        questions_data = llm_data.get("details", llm_data.get("questions", []))
        
        # 构建各题详情
        question_details = []
        for i, q_data in enumerate(questions_data, 1):
            q_score = q_data.get("total", q_data.get("score", 0))
            q_max = q_data.get("max_score", 10)
            q_confidence = q_data.get("confidence", 1.0)
            q_flags = q_data.get("flags", [])
            q_need_review = "need_review" in q_flags or q_data.get("need_review", False)
            q_criteria = q_data.get("criteria", [])
            
            # 规范化 criteria 格式
            formatted_criteria = []
            for crit in q_criteria:
                formatted_criteria.append({
                    "id": crit.get("id", ""),
                    "score": round(float(crit.get("score", 0)), 2),
                    "reason": crit.get("reason", "")
                })
            
            question_detail = {
                "question_id": f"SA{i}",
                "question_name": q_data.get("question", f"SA{i}"),
                "score": round(float(q_score), 2),
                "max_score": q_max,
                "confidence": round(float(q_confidence), 2),
                "need_review": q_need_review,
                "flags": q_flags,
                "criteria": formatted_criteria
            }
            question_details.append(question_detail)
        
        component = {
            "type": "llm_essay",
            "score": round(float(total_score), 2),
            "max_score": max_score,
            "details": {
                "questions": len(question_details),
                "need_review": need_review,
                "question_details": question_details
            }
        }
        
        metadata = {
            "version": "1.0",
            "assignment": assignment_id,
            "student_id": student_id,
            "components": [component],
            "total_score": round(float(total_score), 2),
            "total_max_score": max_score,
            "timestamp": datetime.now().isoformat(),
            "generator": "gitea-autograde"
        }
        
        return metadata
    except Exception as e:
        print(f"Error creating LLM metadata: {e}", file=sys.stderr)
        return {}


def create_objective_metadata(objective_file='objective_grade.json'):
    """从 objective_grade.json 创建元数据"""
    try:
        with open(objective_file, 'r', encoding='utf-8') as f:
            objective_data = json.load(f)

        assignment_id = extract_assignment_id()
        student_id = extract_student_id()

        total_score = objective_data.get("score", 0)
        max_score = objective_data.get("max_score", 0)
        components = objective_data.get("components", [])

        formatted_components = []
        for comp in components:
            comp_type = comp.get("type", "objective")
            formatted_components.append({
                "type": f"objective_{comp_type}",
                "score": comp.get("score", 0),
                "max_score": comp.get("max_score", 0),
                "details": comp.get("details", {})
            })

        if not formatted_components:
            formatted_components.append({
                "type": "objective_total",
                "score": total_score,
                "max_score": max_score,
                "details": {}
            })

        metadata = {
            "version": "1.0",
            "assignment": assignment_id,
            "student_id": student_id,
            "components": formatted_components,
            "total_score": total_score,
            "total_max_score": max_score,
            "timestamp": datetime.now().isoformat(),
            "generator": "gitea-autograde"
        }

        return metadata
    except Exception as e:
        print(f"Error creating objective metadata: {e}", file=sys.stderr)
        return {}


def main():
    """主函数"""
    # 检查命令行参数或环境变量
    grade_type = os.getenv("GRADE_TYPE", "programming").lower()
    grade_file_override = os.getenv("GRADE_FILE")
    
    if grade_type == "llm":
        # LLM 成绩
        llm_file = grade_file_override or "artifacts/llm_grade.json"
        if os.path.exists(llm_file):
            metadata = create_llm_metadata(llm_file)
        elif os.path.exists("llm_grade.json"):
            metadata = create_llm_metadata("llm_grade.json")
        else:
            print(f"Error: {llm_file} not found", file=sys.stderr)
            metadata = {}
    elif grade_type == "objective":
        objective_file = grade_file_override or "objective_grade.json"
        if os.path.exists(objective_file):
            metadata = create_objective_metadata(objective_file)
        else:
            print(f"Error: {objective_file} not found", file=sys.stderr)
            metadata = {}
    else:
        # 编程成绩
        grade_file = grade_file_override or "grade.json"
        if os.path.exists(grade_file):
            metadata = create_grade_metadata(grade_file)
        else:
            print(f"Error: {grade_file} not found", file=sys.stderr)
            metadata = {}
    
    # 输出到 stdout
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


