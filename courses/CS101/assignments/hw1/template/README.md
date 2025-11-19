# HW1: 机器学习基础

## 作业说明

本次作业旨在帮助你掌握：
- 二分类逻辑回归的基本原理与梯度下降优化
- 数据标准化与正则化的作用
- 机器学习基础概念：偏差-方差权衡、正则化、评价指标

## 成绩构成（100 分）

### 编程题 Q1：逻辑回归实现（60 分）

你需要实现一个基于梯度下降的逻辑回归分类器，具体要求如下：

- **API/前向与梯度正确性**（15 分）
- **训练收敛与稳定性**（15 分）
- **数据集上的性能**（20 分）：Accuracy ≥ 0.9 或按区间给分
- **鲁棒性与可复现**（10 分）：随机种子、数值稳定性

### 客观题（20 分）

- **选择题**（10 分）：5 道选择题，每题 2 分
- **判断题**（10 分）：5 道判断题，每题 2 分

### 简答题（20 分）

- **SA1：偏差-方差权衡**（7 分）
- **SA2：L1 vs L2 正则化**（7 分）
- **SA3：Precision/Recall/F1 与适用场景**（6 分）

## 提交规范

1. **编程题提交**：在 `src/models/logistic_regression.py` 中实现 `LogisticRegressionGD` 类
2. **客观题提交**：在 `objective_answers/my_answers.json` 中填写选择题和判断题答案
3. **简答题提交**：在 `answers/` 目录下填写 `sa1.md`、`sa2.md`、`sa3.md`
4. **提交方式**：完成后，执行以下命令提交：

```bash
git add .
git commit -m "完成 HW1"
git push
```

5. **截止时间**：请查看课程公告或仓库 Secrets 中的 `DEADLINE`

## 实现要求

### 编程题约束

- **仅使用 numpy**：禁止使用 `sklearn.linear_model.LogisticRegression` 等直接模型类
- **数值稳定**：`sigmoid` 函数需对大幅度正/负输入稳定
- **支持截距项**：通过 `fit_intercept` 参数控制
- **可复现性**：若设定 `random_state`，结果应稳定
- **数据预处理**：训练前对特征进行标准化（可放在 `src/utils/preprocess.py`）

### API 规范

```python
class LogisticRegressionGD:
    def __init__(self, lr=0.1, n_iters=1000, reg_lambda=0.0, 
                 fit_intercept=True, random_state=None):
        """
        lr: 学习率
        n_iters: 最大迭代次数
        reg_lambda: 正则化系数（L2）
        fit_intercept: 是否拟合截距项
        random_state: 随机种子
        """
        pass
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegressionGD":
        """训练模型"""
        pass
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """返回预测概率，shape (n_samples,)"""
        pass
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """返回预测类别（0/1），shape (n_samples,)"""
        pass
```

## 题目说明

### 编程题

- **公开测试**：`tests_public/` 目录下的测试用例可以本地运行，用于自测
- **隐藏测试**：提交后会自动运行隐藏测试用例，用于最终评分
- **本地测试**：运行 `pytest tests_public/ -v` 进行本地测试

### 客观题

- **题目位置**：`objective_questions/` 目录
  - `mc_questions.md`：选择题题目
  - `tf_questions.md`：判断题题目
- **答题位置**：`objective_answers/my_answers.json`
- **答题格式**：详见 `objective_answers/README.md`

### 简答题

- **题目位置**：`questions/` 目录（`sa1.md`, `sa2.md`, `sa3.md`）
- **答题位置**：`answers/` 目录（对应文件名）
- **评分方式**：LLM 自动评分 + 人工复核（边界样本）

## 数据集

- **公开数据集**：`data/breast_cancer_small.csv`（小样本，用于开发与调试）
- **隐藏数据集**：用于最终性能评估（包含更完整的数据与边界情况）

## 评分与反馈

- 每次 `git push` 后会自动触发批改流程
- 批改结果会在 Pull Request 中显示评论，包含：
  - **编程题**：单元测试通过情况、分数、错误详情
  - **客观题**：正确/错误题目、得分统计
  - **简答题**：LLM 评分、分项得分、置信度
  - **JSON 元数据**：完整的机器可读成绩数据
- 简答题由 LLM 助教评分，边界样本会自动标记为 `need_review` 供人工复核
- 如对成绩有疑问，可在 PR 中回复评论与助教沟通

## 注意事项

1. **禁止作弊**：不得直接使用 sklearn 的模型类，不得抄袭他人代码
2. **代码质量**：注意代码可读性与注释
3. **及时提交**：迟交会按规则扣分（详见 `summary.md`）
4. **查看反馈**：提交后及时查看 Actions 结果，如有问题及时修正

## 参考资料

- 逻辑回归原理与梯度下降算法
- NumPy 文档：https://numpy.org/doc/stable/
- 数据标准化方法

祝学习顺利！


 
 
 
 
 
 
 
