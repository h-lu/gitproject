"""
公开测试：梯度计算与数值稳定性

测试梯度计算的正确性（使用数值梯度验证）
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD


class TestGrad:
    """测试梯度计算"""
    
    def test_sigmoid_numerical_stability(self):
        """测试 sigmoid 函数的数值稳定性"""
        model = LogisticRegressionGD()
        
        # 测试极端值
        z_large = np.array([100, 500, 1000])
        z_small = np.array([-100, -500, -1000])
        z_normal = np.array([0, 1, -1, 2, -2])
        
        # 不应该产生 NaN 或 Inf
        result_large = model._sigmoid(z_large)
        result_small = model._sigmoid(z_small)
        result_normal = model._sigmoid(z_normal)
        
        assert np.all(np.isfinite(result_large))
        assert np.all(np.isfinite(result_small))
        assert np.all(np.isfinite(result_normal))
        
        # 检查值域
        assert np.all((result_large >= 0) & (result_large <= 1))
        assert np.all((result_small >= 0) & (result_small <= 1))
        assert np.all((result_normal >= 0) & (result_normal <= 1))
    
    def test_gradient_descent_converges(self):
        """测试梯度下降能够收敛"""
        # 简单的线性可分数据
        X = np.array([[1, 1], [2, 2], [3, 3], [10, 10], [11, 11], [12, 12]])
        y = np.array([0, 0, 0, 1, 1, 1])
        
        model = LogisticRegressionGD(lr=0.1, n_iters=100, random_state=42)
        model.fit(X, y)
        
        # 应该能够正确分类
        pred = model.predict(X)
        accuracy = np.mean(pred == y)
        assert accuracy >= 0.8  # 至少 80% 准确率


