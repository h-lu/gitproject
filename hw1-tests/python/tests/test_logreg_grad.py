"""
隐藏测试：梯度计算与数值稳定性（更严格）

测试梯度计算的正确性和数值稳定性
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD


class TestGrad:
    """测试梯度计算（隐藏测试）"""
    
    def test_sigmoid_extreme_values(self):
        """测试 sigmoid 在极端值下的数值稳定性"""
        model = LogisticRegressionGD()
        
        # 测试非常大的值
        z_very_large = np.array([500, 1000, 2000])
        result = model._sigmoid(z_very_large)
        
        # 应该接近 1，但不应该是 inf 或 nan
        assert np.all(np.isfinite(result))
        assert np.all(result > 0.99)
        assert np.all(result <= 1.0)
        
        # 测试非常小的值
        z_very_small = np.array([-500, -1000, -2000])
        result = model._sigmoid(z_very_small)
        
        # 应该接近 0，但不应该是 inf 或 nan
        assert np.all(np.isfinite(result))
        assert np.all(result < 0.01)
        assert np.all(result >= 0.0)
    
    def test_gradient_descent_converges_large_data(self):
        """测试在大数据集上的收敛性"""
        # 生成更大的数据集
        np.random.seed(42)
        n_samples = 500
        X = np.random.randn(n_samples, 5)
        y = (X[:, 0] + X[:, 1] - X[:, 2] > 0).astype(int)
        
        # 标准化
        from src.utils.preprocess import standardize
        X_scaled, _, _ = standardize(X)
        
        model = LogisticRegressionGD(lr=0.1, n_iters=1000, random_state=42)
        model.fit(X_scaled, y)
        
        # 应该能够正确分类
        pred = model.predict(X_scaled)
        accuracy = np.mean(pred == y)
        assert accuracy >= 0.85  # 在大数据集上要求稍低但仍需较高准确率
    
    def test_regularization_effect(self):
        """测试正则化的效果"""
        np.random.seed(42)
        X = np.random.randn(100, 10)
        y = np.random.randint(0, 2, 100)
        
        from src.utils.preprocess import standardize
        X_scaled, _, _ = standardize(X)
        
        # 无正则化
        model_no_reg = LogisticRegressionGD(reg_lambda=0.0, random_state=42)
        model_no_reg.fit(X_scaled, y)
        
        # 有正则化
        model_reg = LogisticRegressionGD(reg_lambda=1.0, random_state=42)
        model_reg.fit(X_scaled, y)
        
        # 正则化应该使权重更小（L2 正则化）
        if model_no_reg.weights is not None and model_reg.weights is not None:
            norm_no_reg = np.linalg.norm(model_no_reg.weights)
            norm_reg = np.linalg.norm(model_reg.weights)
            # 正则化后的权重范数应该更小
            assert norm_reg <= norm_no_reg * 1.1  # 允许一些误差

