#!/usr/bin/env python3
"""
聚合多个 LLM 评分结果
"""
import json
import argparse
from pathlib import Path


def load_grade(filepath):
    """加载单个评分文件"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filepath} not found")
        return None
    except json.JSONDecodeError as e:
        print(f"Error parsing {filepath}: {e}")
        return None


def aggregate_grades(input_files, output_file, summary_file):
    """聚合多个评分文件"""
    grades = []
    total_score = 0
    max_score = 0
    need_review_count = 0
    
    for input_file in input_files:
        grade = load_grade(input_file)
        if grade:
            grades.append(grade)
            # 支持两种格式：'total' (llm_grade.py) 或 'score' (旧格式)
            score = grade.get('total', grade.get('score', 0))
            total_score += score
            # 默认每题 10 分
            max_score += grade.get('max_score', 10)
            # 检查是否需要审核
            if 'need_review' in grade.get('flags', []) or grade.get('need_review', False):
                need_review_count += 1
    
    # 计算总分
    final_score = total_score if max_score > 0 else 0
    final_max_score = max_score
    
    # 生成汇总结果
    result = {
        'total_score': final_score,
        'max_score': final_max_score,
        'questions': len(grades),
        'need_review': need_review_count > 0,
        'details': grades
    }
    
    # 保存 JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    # 生成 Markdown 摘要
    summary_lines = [
        '# LLM 简答题评分汇总',
        '',
        f'**总分**: {final_score:.1f} / {final_max_score:.1f}',
        f'**题目数**: {len(grades)}',
        f'**需要人工审核**: {"是" if result["need_review"] else "否"}',
        '',
        '## 各题详情',
        ''
    ]
    
    for i, grade in enumerate(grades, 1):
        q_name = grade.get('question', f'Q{i}')
        # 支持两种格式：'total' (llm_grade.py) 或 'score' (旧格式)
        score = grade.get('total', grade.get('score', 0))
        max_q_score = grade.get('max_score', 10)
        # 检查是否需要审核
        need_review = 'need_review' in grade.get('flags', []) or grade.get('need_review', False)
        confidence = grade.get('confidence', 1.0)
        
        summary_lines.append(f'### SA{i}')
        summary_lines.append(f'- **得分**: {score:.2f} / {max_q_score:.1f}')
        summary_lines.append(f'- **置信度**: {confidence:.2f}')
        if need_review:
            summary_lines.append('- ⚠️ **需要人工审核**')
        
        # 显示分项评分
        if 'criteria' in grade:
            summary_lines.append('- **分项**:')
            for criterion in grade['criteria']:
                crit_id = criterion.get('id', '')
                crit_score = criterion.get('score', 0)
                crit_reason = criterion.get('reason', '')
                summary_lines.append(f'  - {crit_id}: {crit_score:.1f} - {crit_reason}')
        
        summary_lines.append('')
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_lines))
    
    print(f"✅ Aggregated {len(grades)} grades")
    print(f"   Total: {final_score:.1f} / {final_max_score:.1f}")
    print(f"   Output: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Aggregate LLM grading results')
    parser.add_argument('--inputs', nargs='+', required=True,
                       help='Input grade JSON files')
    parser.add_argument('--out', required=True,
                       help='Output aggregated JSON file')
    parser.add_argument('--summary', required=True,
                       help='Output summary Markdown file')
    
    args = parser.parse_args()
    
    aggregate_grades(args.inputs, args.out, args.summary)


if __name__ == '__main__':
    main()
