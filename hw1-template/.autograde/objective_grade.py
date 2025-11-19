#!/usr/bin/env python3
"""
选择题/判断题评分脚本

读取学生答案和标准答案，生成成绩 JSON 文件
"""

import json
import argparse
import sys
from datetime import datetime
from pathlib import Path


def load_answers(answer_file):
    """
    加载学生答案文件（支持 JSON 和简单文本格式）
    
    JSON 格式示例：
    {
      "MC1": "A",
      "MC2": "B",
      "TF1": true,
      "TF2": false
    }
    
    文本格式示例（每行一个答案）：
    A
    B
    true
    false
    """
    try:
        with open(answer_file, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 尝试作为 JSON 加载
        if content.startswith('{'):
            return json.loads(content)
        
        # 否则按行加载，忽略空行和注释
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        # 转换为字典格式：{"MC1": answer, "MC2": answer, ...}
        answers = {}
        for i, line in enumerate(lines, 1):
            # 尝试识别题型
            if line.lower() in ('true', 'false', 't', 'f'):
                question_id = f"TF{len([k for k in answers if k.startswith('TF')])+1}"
                answers[question_id] = line.lower() in ('true', 't')
            else:
                question_id = f"MC{len([k for k in answers if k.startswith('MC')])+1}"
                answers[question_id] = line.upper()
        
        return answers
    except Exception as e:
        print(f"Error loading answers: {e}", file=sys.stderr)
        return {}


def load_standard_answers(std_file):
    """加载标准答案文件（JSON 格式）"""
    try:
        with open(std_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading standard answers: {e}", file=sys.stderr)
        return {}


def grade_multiple_choice(student_answers, standard_answers, question_texts=None):
    """
    评选择题
    
    Parameters
    ----------
    student_answers : dict
        学生答案，格式 {"MC1": "A", "MC2": "B", ...}
    standard_answers : dict
        标准答案，格式 {"MC1": "A", "MC2": "B", ...}
    question_texts : dict, optional
        题目文本，格式 {"MC1": "题目文本", ...}
    
    Returns
    -------
    dict
        成绩数据
    """
    questions = []
    correct_count = 0
    
    for question_id, std_answer in standard_answers.items():
        if not question_id.startswith('MC'):
            continue
        
        student_answer = student_answers.get(question_id, "")
        is_correct = str(student_answer).upper() == str(std_answer).upper()
        
        if is_correct:
            correct_count += 1
            score = 1
        else:
            score = 0
        
        questions.append({
            "question_id": question_id,
            "question_text": question_texts.get(question_id, "") if question_texts else "",
            "correct_answer": str(std_answer).upper(),
            "student_answer": str(student_answer).upper(),
            "correct": is_correct,
            "score": score,
            "max_score": 1
        })
    
    total_count = len(questions)
    
    return {
        "type": "multiple_choice",
        "score": correct_count,
        "max_score": total_count,
        "details": {
            "correct": correct_count,
            "total": total_count,
            "questions": questions
        }
    }


def grade_true_false(student_answers, standard_answers, question_texts=None):
    """
    评判断题
    
    Parameters
    ----------
    student_answers : dict
        学生答案，格式 {"TF1": true, "TF2": false, ...}
    standard_answers : dict
        标准答案，格式 {"TF1": true, "TF2": false, ...}
    question_texts : dict, optional
        题目文本
    
    Returns
    -------
    dict
        成绩数据
    """
    questions = []
    correct_count = 0
    
    for question_id, std_answer in standard_answers.items():
        if not question_id.startswith('TF'):
            continue
        
        student_answer = student_answers.get(question_id, None)
        
        # 规范化布尔值
        if isinstance(student_answer, str):
            student_answer = student_answer.lower() in ('true', 't', '1', 'yes')
        
        is_correct = bool(student_answer) == bool(std_answer)
        
        if is_correct:
            correct_count += 1
            score = 1
        else:
            score = 0
        
        questions.append({
            "question_id": question_id,
            "question_text": question_texts.get(question_id, "") if question_texts else "",
            "correct_answer": bool(std_answer),
            "student_answer": bool(student_answer) if student_answer is not None else None,
            "correct": is_correct,
            "score": score,
            "max_score": 1
        })
    
    total_count = len(questions)
    
    return {
        "type": "true_false",
        "score": correct_count,
        "max_score": total_count,
        "details": {
            "correct": correct_count,
            "total": total_count,
            "questions": questions
        }
    }


def grade_multiple_select(student_answers, standard_answers, question_texts=None):
    """
    评多选题
    
    Parameters
    ----------
    student_answers : dict
        学生答案，格式 {"MS1": ["A", "B"], "MS2": ["C"], ...}
    standard_answers : dict
        标准答案，格式 {"MS1": ["A", "B"], "MS2": ["C"], ...}
    question_texts : dict, optional
        题目文本
    
    Returns
    -------
    dict
        成绩数据
    """
    questions = []
    correct_count = 0
    
    for question_id, std_answer in standard_answers.items():
        if not question_id.startswith('MS'):
            continue
        
        student_answer = student_answers.get(question_id, [])
        
        # 规范化答案（转为大写并排序）
        if isinstance(student_answer, str):
            student_answer = [student_answer]
        if not isinstance(student_answer, list):
            student_answer = []
        
        std_set = set([str(a).upper() for a in std_answer])
        stu_set = set([str(a).upper() for a in student_answer])
        
        is_correct = std_set == stu_set
        
        if is_correct:
            correct_count += 1
            score = 1
        else:
            score = 0
        
        questions.append({
            "question_id": question_id,
            "question_text": question_texts.get(question_id, "") if question_texts else "",
            "correct_answer": sorted(list(std_set)),
            "student_answer": sorted(list(stu_set)) if stu_set else [],
            "correct": is_correct,
            "score": score,
            "max_score": 1
        })
    
    total_count = len(questions)
    
    return {
        "type": "multiple_select",
        "score": correct_count,
        "max_score": total_count,
        "details": {
            "correct": correct_count,
            "total": total_count,
            "questions": questions
        }
    }


def grade_fill_blank(student_answers, standard_answers, question_texts=None):
    """
    评填空题
    
    Parameters
    ----------
    student_answers : dict
        学生答案，格式 {"FB1": "答案", "FB2": ["答案1", "答案2"], ...}
    standard_answers : dict
        标准答案，格式同上
    question_texts : dict, optional
        题目文本
    
    Returns
    -------
    dict
        成绩数据
    """
    questions = []
    correct_count = 0
    
    def normalize_answer(ans):
        """规范化答案：去除空格、转小写"""
        if isinstance(ans, str):
            return ans.strip().lower()
        elif isinstance(ans, list):
            return [a.strip().lower() for a in ans]
        return ans
    
    def compare_answers(student, standard):
        """比较答案是否相等"""
        student_norm = normalize_answer(student)
        standard_norm = normalize_answer(standard)
        
        if isinstance(standard_norm, list) and isinstance(student_norm, list):
            return student_norm == standard_norm
        elif isinstance(standard_norm, str) and isinstance(student_norm, str):
            return student_norm == standard_norm
        return False
    
    for question_id, std_answer in standard_answers.items():
        if not question_id.startswith('FB'):
            continue
        
        student_answer = student_answers.get(question_id, "")
        
        is_correct = compare_answers(student_answer, std_answer)
        
        if is_correct:
            correct_count += 1
            score = 1
        else:
            score = 0
        
        questions.append({
            "question_id": question_id,
            "question_text": question_texts.get(question_id, "") if question_texts else "",
            "correct_answer": std_answer,
            "student_answer": student_answer,
            "correct": is_correct,
            "score": score,
            "max_score": 1
        })
    
    total_count = len(questions)
    
    return {
        "type": "fill_blank",
        "score": correct_count,
        "max_score": total_count,
        "details": {
            "correct": correct_count,
            "total": total_count,
            "questions": questions
        }
    }


def main():
    parser = argparse.ArgumentParser(description="Grade objective questions")
    parser.add_argument("--answers", required=True, help="Student answers file (JSON or text)")
    parser.add_argument("--standard", required=True, help="Standard answers file (JSON)")
    parser.add_argument("--questions", help="Question texts file (JSON, optional)")
    parser.add_argument("--out", default="grade.json", help="Output grade JSON file")
    parser.add_argument("--summary", default="summary.md", help="Output summary markdown file")
    parser.add_argument("--type", choices=['mc', 'tf', 'ms', 'fb', 'all'], default='all',
                        help="Question type to grade")
    
    args = parser.parse_args()
    
    # 加载文件
    student_answers = load_answers(args.answers)
    standard_answers = load_standard_answers(args.standard)
    question_texts = None
    
    if args.questions:
        try:
            with open(args.questions, 'r', encoding='utf-8') as f:
                question_texts = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load question texts: {e}", file=sys.stderr)
    
    if not student_answers or not standard_answers:
        print("Error: Could not load answers", file=sys.stderr)
        sys.exit(1)
    
    # 评分
    components = []
    total_score = 0
    total_max_score = 0
    
    if args.type in ('mc', 'all'):
        mc_grade = grade_multiple_choice(student_answers, standard_answers, question_texts)
        if mc_grade['details']['total'] > 0:
            components.append(mc_grade)
            total_score += mc_grade['score']
            total_max_score += mc_grade['max_score']
    
    if args.type in ('tf', 'all'):
        tf_grade = grade_true_false(student_answers, standard_answers, question_texts)
        if tf_grade['details']['total'] > 0:
            components.append(tf_grade)
            total_score += tf_grade['score']
            total_max_score += tf_grade['max_score']
    
    if args.type in ('ms', 'all'):
        ms_grade = grade_multiple_select(student_answers, standard_answers, question_texts)
        if ms_grade['details']['total'] > 0:
            components.append(ms_grade)
            total_score += ms_grade['score']
            total_max_score += ms_grade['max_score']
    
    if args.type in ('fb', 'all'):
        fb_grade = grade_fill_blank(student_answers, standard_answers, question_texts)
        if fb_grade['details']['total'] > 0:
            components.append(fb_grade)
            total_score += fb_grade['score']
            total_max_score += fb_grade['max_score']
    
    # 生成 grade.json
    grade_data = {
        "score": total_score,
        "max_score": total_max_score,
        "components": components,
        "timestamp": int(__import__('time').time())
    }
    
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(grade_data, f, ensure_ascii=False, indent=2)
    
    # 生成 summary.md
    summary_lines = [
        "# 客观题评分\n",
        f"- **总分**：{total_score} / {total_max_score}\n",
        f"- **组件数**：{len(components)}\n",
        ""
    ]
    
    for comp in components:
        comp_type = comp['type']
        correct = comp['details']['correct']
        total = comp['details']['total']
        
        type_names = {
            'multiple_choice': '选择题',
            'true_false': '判断题',
            'multiple_select': '多选题',
            'fill_blank': '填空题'
        }
        
        type_name = type_names.get(comp_type, comp_type)
        summary_lines.append(f"## {type_name}\n")
        summary_lines.append(f"- **正确**：{correct} / {total}\n")
        summary_lines.append("")
    
    with open(args.summary, 'w', encoding='utf-8') as f:
        f.write("\n".join(summary_lines))
    
    print(f"Grading complete: {total_score}/{total_max_score}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

