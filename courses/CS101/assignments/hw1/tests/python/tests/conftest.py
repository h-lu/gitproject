"""
pytest 配置文件（隐藏测试）

提供共享的 fixtures
"""

import pytest
import numpy as np
import os


@pytest.fixture
def hidden_dataset():
    """加载隐藏数据集"""
    data_path = os.path.join(
        os.path.dirname(__file__), 
        '../data/breast_cancer_hidden.csv'
    )
    
    if not os.path.exists(data_path):
        pytest.skip("Hidden dataset not found")
    
    try:
        import pandas as pd
        df = pd.read_csv(data_path)
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        return X, y
    except ImportError:
        # 如果没有 pandas，使用 csv 模块
        import csv
        with open(data_path, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            data = list(reader)
        
        X = np.array([[float(x) for x in row[:-1]] for row in data])
        y = np.array([int(row[-1]) for row in data])
        return X, y

