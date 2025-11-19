"""
pytest 配置文件

提供共享的 fixtures 和测试配置
"""

import pytest
import numpy as np


@pytest.fixture
def random_seed():
    """设置随机种子 fixture"""
    np.random.seed(42)
    return 42


@pytest.fixture
def simple_binary_data():
    """生成简单的二分类数据"""
    np.random.seed(42)
    X = np.random.randn(100, 2)
    y = (X[:, 0] + X[:, 1] > 0).astype(int)
    return X, y


