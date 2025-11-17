# 通用成绩元数据格式规范

## 概述

本规范定义了 Gitea 自动批改系统的通用成绩元数据格式，支持多语言编程题、LLM 评分、选择题和判断题的混合作业。

## 顶层结构

```json
{
  "version": "1.0",
  "assignment": "hw1",
  "student_id": "sit001",
  "components": [
    { "type": "programming_python", ... },
    { "type": "llm_essay", ... },
    { "type": "multiple_choice", ... },
    { "type": "true_false", ... }
  ],
  "total_score": 124.5,
  "total_max_score": 145,
  "timestamp": "2025-11-13T21:29:47.726257",
  "generator": "gitea-autograde"
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| version | string | 是 | 格式版本，当前为 "1.0" |
| assignment | string | 是 | 作业 ID，如 "hw1", "hw2" |
| student_id | string | 否 | 学生 ID，从仓库名或环境变量提取 |
| components | array | 是 | 成绩组件列表，至少 1 个 |
| total_score | number | 是 | 所有组件的累加分数 |
| total_max_score | number | 是 | 所有组件的最大分数总和 |
| timestamp | string | 是 | ISO 8601 时间戳 |
| generator | string | 是 | 生成工具，固定为 "gitea-autograde" |

---

## Component Types

### 1. Programming (编程题)

支持 Python、Java、R 等语言。

#### 类型标识
- `programming_python`
- `programming_java`
- `programming_r`

#### 完整示例

```json
{
  "type": "programming_python",
  "language": "python",
  "score": 85.5,
  "max_score": 100,
  "details": {
    "passed": 12,
    "total": 15,
    "base_score": 85.5,
    "penalty": 0.0,
    "coverage": 0.85,
    "failed_tests": [
      "tests.test_module.test_func1",
      "tests.test_module.test_func2"
    ],
    "test_framework": "pytest"
  }
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | `programming_python` \| `programming_java` \| `programming_r` |
| language | string | 是 | 编程语言 |
| score | number | 是 | 最终得分 |
| max_score | number | 是 | 最大分数 |
| details.passed | integer | 是 | 通过的测试用例数 |
| details.total | integer | 是 | 总测试用例数 |
| details.base_score | number | 是 | 未扣分的基础分数 |
| details.penalty | number | 是 | 扣分（如迟交扣分） |
| details.coverage | number | 否 | 代码覆盖率（0-1） |
| details.failed_tests | array | 是 | 未通过的测试名称列表 |
| details.test_framework | string | 是 | 测试框架（pytest, junit, testthat 等） |

---

### 2. LLM Essay (LLM 简答题)

#### 类型标识
- `llm_essay`

#### 完整示例

```json
{
  "type": "llm_essay",
  "score": 25.5,
  "max_score": 30,
  "details": {
    "questions": 3,
    "need_review": true,
    "question_details": [
      {
        "question_id": "SA1",
        "question_name": "偏差-方差权衡",
        "score": 8.5,
        "max_score": 10,
        "confidence": 0.9,
        "need_review": false,
        "flags": [],
        "criteria": [
          {
            "id": "accuracy",
            "score": 3,
            "reason": "定义准确，理解完整"
          },
          {
            "id": "coverage",
            "score": 3,
            "reason": "覆盖表现与实践方法"
          },
          {
            "id": "clarity",
            "score": 2.5,
            "reason": "表达基本清晰"
          }
        ]
      },
      {
        "question_id": "SA2",
        "question_name": "L1 vs L2 正则化",
        "score": 0.0,
        "max_score": 10,
        "confidence": 1.0,
        "need_review": true,
        "flags": ["need_review"],
        "criteria": [
          {
            "id": "accuracy",
            "score": 0.0,
            "reason": "答案缺失"
          },
          {
            "id": "coverage",
            "score": 0.0,
            "reason": "未覆盖任何要点"
          },
          {
            "id": "clarity",
            "score": 0.0,
            "reason": "无内容"
          }
        ]
      },
      {
        "question_id": "SA3",
        "question_name": "Precision/Recall/F1",
        "score": 17.0,
        "max_score": 10,
        "confidence": 0.85,
        "need_review": false,
        "flags": [],
        "criteria": [...]
      }
    ]
  }
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | `llm_essay` |
| score | number | 是 | 总分 |
| max_score | number | 是 | 最大分 |
| details.questions | integer | 是 | 题目数量 |
| details.need_review | boolean | 是 | 是否需要人工审核 |
| details.question_details | array | 是 | 各题详情（见下表） |

**question_details 字段说明**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| question_id | string | 是 | 题目 ID，如 "SA1" |
| question_name | string | 是 | 题目名称 |
| score | number | 是 | 该题得分 |
| max_score | number | 是 | 该题最大分 |
| confidence | number | 是 | LLM 评分置信度（0-1） |
| need_review | boolean | 是 | 该题是否需要人工审核 |
| flags | array | 是 | 标记列表（如 "need_review"、"llm_error"） |
| criteria | array | 是 | 分项评分（见下表） |

**criteria 字段说明**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| id | string | 是 | 标准 ID（如 "accuracy", "coverage", "clarity"） |
| score | number | 是 | 该维度得分 |
| reason | string | 是 | 评分理由 |

---

### 3. Multiple Choice (选择题)

#### 类型标识
- `multiple_choice`

#### 完整示例

```json
{
  "type": "multiple_choice",
  "score": 8,
  "max_score": 10,
  "details": {
    "correct": 8,
    "total": 10,
    "questions": [
      {
        "question_id": "MC1",
        "question_text": "什么是机器学习？",
        "correct_answer": "A",
        "student_answer": "A",
        "correct": true,
        "score": 1,
        "max_score": 1
      },
      {
        "question_id": "MC2",
        "question_text": "下列哪个是监督学习？",
        "correct_answer": "B",
        "student_answer": "C",
        "correct": false,
        "score": 0,
        "max_score": 1
      }
    ]
  }
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | `multiple_choice` |
| score | number | 是 | 总分 |
| max_score | number | 是 | 最大分 |
| details.correct | integer | 是 | 正确数量 |
| details.total | integer | 是 | 总题数 |
| details.questions | array | 是 | 各题详情（见下表） |

**questions 字段说明**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| question_id | string | 是 | 题目 ID，如 "MC1" |
| question_text | string | 否 | 题目文本 |
| correct_answer | string | 是 | 标准答案（如 "A"、"B"） |
| student_answer | string | 是 | 学生答案 |
| correct | boolean | 是 | 是否正确 |
| score | number | 是 | 该题得分 |
| max_score | number | 是 | 该题最大分 |

---

### 4. True/False (判断题)

#### 类型标识
- `true_false`

#### 完整示例

```json
{
  "type": "true_false",
  "score": 5,
  "max_score": 5,
  "details": {
    "correct": 5,
    "total": 5,
    "questions": [
      {
        "question_id": "TF1",
        "question_text": "所有机器学习模型都需要大数据才能工作。",
        "correct_answer": false,
        "student_answer": false,
        "correct": true,
        "score": 1,
        "max_score": 1
      },
      {
        "question_id": "TF2",
        "question_text": "过拟合是机器学习中的常见问题。",
        "correct_answer": true,
        "student_answer": true,
        "correct": true,
        "score": 1,
        "max_score": 1
      }
    ]
  }
}
```

#### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | string | 是 | `true_false` |
| score | number | 是 | 总分 |
| max_score | number | 是 | 最大分 |
| details.correct | integer | 是 | 正确数量 |
| details.total | integer | 是 | 总题数 |
| details.questions | array | 是 | 各题详情（见下表） |

**questions 字段说明**

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| question_id | string | 是 | 题目 ID，如 "TF1" |
| question_text | string | 否 | 题目文本 |
| correct_answer | boolean | 是 | 标准答案 |
| student_answer | boolean | 是 | 学生答案 |
| correct | boolean | 是 | 是否正确 |
| score | number | 是 | 该题得分 |
| max_score | number | 是 | 该题最大分 |

---

## 混合作业示例

一个包含编程题、LLM 简答题、选择题和判断题的作业：

```json
{
  "version": "1.0",
  "assignment": "hw1",
  "student_id": "sit001",
  "components": [
    {
      "type": "programming_python",
      "language": "python",
      "score": 70,
      "max_score": 100,
      "details": {
        "passed": 12,
        "total": 15,
        "base_score": 80,
        "penalty": 10,
        "failed_tests": [...],
        "test_framework": "pytest"
      }
    },
    {
      "type": "llm_essay",
      "score": 27,
      "max_score": 30,
      "details": {
        "questions": 3,
        "need_review": false,
        "question_details": [...]
      }
    },
    {
      "type": "multiple_choice",
      "score": 9,
      "max_score": 10,
      "details": {
        "correct": 9,
        "total": 10,
        "questions": [...]
      }
    },
    {
      "type": "true_false",
      "score": 4,
      "max_score": 5,
      "details": {
        "correct": 4,
        "total": 5,
        "questions": [...]
      }
    }
  ],
  "total_score": 110,
  "total_max_score": 145,
  "timestamp": "2025-11-13T21:29:47.726257",
  "generator": "gitea-autograde"
}
```

---

## 环境变量

在生成元数据时，可通过以下环境变量配置：

| 环境变量 | 说明 | 示例 |
|---------|------|------|
| ASSIGNMENT_ID | 作业 ID | hw1 |
| STUDENT_ID | 学生 ID（优先级高） | sit001 |
| REPO | Git 仓库名（用于提取 student_id） | course-test/hw1-stu_sit001 |
| GRADE_TYPE | 题型类型 | programming \| llm \| mc \| tf |
| LANGUAGE | 编程语言（若涉及编程题） | python \| java \| r |

---

## 注意事项

1. **student_id 提取规则**
   - 优先从 `STUDENT_ID` 环境变量获取
   - 若未设置，从 `REPO` 中通过正则 `hw\d+-stu[_-]?([^/]+)` 提取
   - 若无法提取，使用 `null`

2. **分数舍入**
   - 所有分数字段保留 2 位小数
   - 使用 Python `round()` 函数或等价实现

3. **时间戳**
   - 使用 ISO 8601 格式：`2025-11-13T21:29:47.726257`
   - 使用 UTC 时间或本地时间（保持一致）

4. **字段验证**
   - `score` ≤ `max_score`
   - `total_score` = 所有组件 `score` 之和
   - `total_max_score` = 所有组件 `max_score` 之和

5. **容错处理**
   - 若某个组件数据缺失，仍生成其他组件的元数据
   - 若所有组件都缺失，生成空的 `components: []`

---

## 多语言支持

### 语言特定的 Component Type

系统自动根据 `LANGUAGE` 环境变量生成语言特定的 type：

| 语言   | Component Type      | 示例 |
|--------|---------------------|------|
| Python | `programming_python` | `{"type": "programming_python", "language": "python"}` |
| Java   | `programming_java`   | `{"type": "programming_java", "language": "java"}` |
| R      | `programming_r`      | `{"type": "programming_r", "language": "r"}` |

### 语言配置

在 workflow 中设置 `LANGUAGE` 环境变量：

```yaml
- name: Create grade metadata
  env:
    ASSIGNMENT_ID: hw1
    REPO: ${{ github.repository }}
    LANGUAGE: java  # 设置语言
  run: |
    export GRADE_TYPE=programming
    python3 ./.autograde/create_minimal_metadata.py > metadata.json
```

### 成绩收集中的归一化

`collect_grades.py` 会自动将所有 `programming_*` 类型归一化为 `programming`，避免重复计数：

```python
def normalize_component_type(comp_type):
    """将 programming_python/java/r 统一为 programming"""
    if comp_type and comp_type.startswith("programming"):
        return "programming"
    return comp_type
```

这样在 CSV 报告中，无论是 Python、Java 还是 R 作业，都会显示为一个统一的 programming 分数。

---

## 工具和文档

- **课程模板生成器**: `scripts/create_course_template.py` - 快速创建不同语言的课程模板
- **Workflow 模板**: `hw1-template/.autograde/workflow_templates/` - Python/Java/R 模板
- **示例**: `hw1-template/examples/` - 各语言的完整示例
- **详细指南**: `COURSE_TEMPLATE_GUIDE.md` - 创建多语言课程的完整指南

---

## 版本历史

- **1.0** (2025-11-13): 初始版本，支持编程、LLM、选择题、判断题
- **1.1** (2025-11-13): 添加多语言支持说明（Python/Java/R）

