# 隐藏测试仓库

此仓库包含 HW1 的隐藏测试用例，仅教师和 CI 系统可访问。

## 目录结构

```
hw1-tests/
├── python/
│   ├── tests/
│   │   ├── test_logreg_basic.py      # 隐藏的 API 测试
│   │   ├── test_logreg_grad.py       # 隐藏的梯度测试
│   │   ├── test_logreg_train.py      # 隐藏的性能测试
│   │   └── test_logreg_robust.py      # 隐藏的鲁棒性测试
│   └── data/
│       └── breast_cancer_hidden.csv   # 隐藏数据集
```

## 注意事项

- 此仓库应设置为**私有**
- 仅教师和 CI Runner 有读取权限
- 学生不应能够访问此仓库的内容


