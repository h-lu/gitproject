#!/usr/bin/env python3
"""
LLM 简答题评分脚本

调用 LLM API，按评分量表对简答题进行评分，输出 JSON 格式结果
"""

import os
import json
import argparse
import requests
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量（支持从 .env 文件或环境变量读取）
load_dotenv()


def read_file(path):
    """读取文件内容"""
    if os.path.exists(path):
        return open(path, 'r', encoding='utf-8').read()
    return ""


PROMPT_TEMPLATE = """你是严格且一致的助教，按提供的评分量表为学生的简答题评分。

- 只依据量表，不做主观延伸；允许多样表述。
- 不输出任何解释性文本；只输出 JSON，包含:
  {{
    "total": number(0-10, 两位小数),
    "criteria": [
      {{"id":"accuracy","score":0-3,"reason":"要点式一句话"}},
      {{"id":"coverage","score":0-3,"reason":""}},
      {{"id":"clarity","score":0-3,"reason":""}}
    ],
    "flags": [],
    "confidence": number(0-1)
  }}
如果答案与题目无关，total=0，并加 flag "need_review"。

【题目】
<<<{question}>>>

【评分量表】
<<<{rubric}>>>

【学生答案】
<<<{answer}>>>
"""


def call_llm(url, key, model, prompt):
    """
    调用 LLM API
    
    Parameters
    ----------
    url : str
        API 地址
    key : str
        API 密钥
    model : str
        模型名称
    prompt : str
        提示词
    
    Returns
    -------
    dict
        LLM 返回的 JSON 结果
    """
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model,
        "temperature": 0,
        "top_p": 1,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {"type": "json_object"}
    }
    
    try:
        # 设置超时：连接超时 10 秒，读取超时 60 秒
        response = requests.post(
            url, 
            headers=headers, 
            json=data, 
            timeout=(10, 60)
        )
        response.raise_for_status()
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "{}")
        return json.loads(content)
    except requests.exceptions.Timeout as e:
        print(f"LLM API request timeout: {e}", file=sys.stderr)
        raise
    except requests.exceptions.HTTPError as e:
        print(f"LLM API HTTP error: {e} (status: {response.status_code})", file=sys.stderr)
        raise
    except requests.exceptions.RequestException as e:
        print(f"LLM API request failed: {e}", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse LLM response as JSON: {e}", file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description="Grade short answer questions using LLM")
    parser.add_argument("--question", required=True, help="Path to question file")
    parser.add_argument("--answer", required=True, help="Path to answer file")
    parser.add_argument("--rubric", required=True, help="Path to rubric JSON file")
    parser.add_argument("--out", default="grade.json", help="Output JSON file")
    parser.add_argument("--summary", default="summary.md", help="Output summary markdown file")
    parser.add_argument("--model", default=os.getenv("LLM_MODEL", "deepseek-chat"))
    parser.add_argument("--api_url", default=os.getenv("LLM_API_URL", "https://api.deepseek.com/chat/completions"))
    parser.add_argument("--api_key", default=os.getenv("LLM_API_KEY", ""))
    args = parser.parse_args()
    
    # 验证必需的配置
    if not args.api_key:
        print("Warning: LLM_API_KEY not set. LLM grading may fail.", file=sys.stderr)
    
    # 读取文件
    question = read_file(args.question).strip()
    answer = read_file(args.answer).strip()
    rubric_text = read_file(args.rubric).strip()
    
    if not question or not answer:
        print(f"Warning: Empty question or answer file", file=sys.stderr)
        resp = {
            "total": 0,
            "criteria": [],
            "flags": ["need_review", "empty_answer"],
            "confidence": 0.0
        }
    else:
        # 调用 LLM
        try:
            prompt = PROMPT_TEMPLATE.format(
                question=question,
                rubric=rubric_text,
                answer=answer
            )
            resp = call_llm(args.api_url, args.api_key, args.model, prompt)
        except Exception as e:
            print(f"LLM grading failed: {e}", file=sys.stderr)
            resp = {
                "total": 0,
                "criteria": [],
                "flags": ["need_review", "llm_error"],
                "confidence": 0.0
            }
    
    # 边界带自动送审
    try:
        rubric_data = json.loads(rubric_text)
        lo, hi = rubric_data.get("borderline_band", [None, None])
        total = float(resp.get("total", 0))
        flags = set(resp.get("flags", []))
        
        if lo is not None and hi is not None and lo <= total <= hi:
            flags.add("need_review")
        
        # 低置信度送审
        confidence = resp.get("confidence", 1.0)
        if confidence < 0.7:
            flags.add("need_review")
        
        resp["flags"] = sorted(list(flags))
    except Exception:
        pass
    
    # 保存 grade.json
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(resp, f, ensure_ascii=False, indent=2)
    
    # 生成 summary.md
    try:
        rubric_data = json.loads(rubric_text)
        max_score = rubric_data.get("max_score", 10)
    except Exception:
        max_score = 10
    
    lines = [
        f"# 简答题评分",
        f"",
        f"- **总分**：**{resp.get('total', 0):.2f} / {max_score}**",
        f"- **置信度**：{resp.get('confidence', 0):.2f}",
        f"- **标记**：{', '.join(resp.get('flags', [])) or '无'}",
        f"",
        f"## 分项评分"
    ]
    
    for criterion in resp.get("criteria", []):
        criterion_id = criterion.get("id", "")
        score = criterion.get("score", 0)
        reason = criterion.get("reason", "")
        lines.append(f"- **{criterion_id}**: {score} 分")
        if reason:
            lines.append(f"  - {reason}")
    
    with open(args.summary, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"LLM grading complete: {resp.get('total', 0):.2f}/{max_score}")


if __name__ == "__main__":
    main()


