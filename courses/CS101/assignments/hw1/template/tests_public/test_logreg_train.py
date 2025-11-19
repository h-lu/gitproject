"""
公开测试：训练性能

测试在数据集上的训练效果
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD
from src.utils.preprocess import standardize, train_test_split


class TestPerf:
    """测试训练性能"""
    
    def test_train_on_simple_data(self):
        """在简单数据集上测试训练"""
        # 生成简单的线性可分数据
        np.random.seed(42)
        n_samples = 100
        X = np.random.randn(n_samples, 2)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        
        # 标准化
        X_scaled, _, _ = standardize(X)
        
        model = LogisticRegressionGD(lr=0.1, n_iters=500, random_state=42)
        model.fit(X_scaled, y)
        
        # 预测
        pred = model.predict(X_scaled)
        accuracy = np.mean(pred == y)
        
        # 应该能达到较高的准确率
        assert accuracy >= 0.9
    
    def test_reproducibility(self):
        """测试可复现性（相同 random_state 应产生相同结果）"""
        np.random.seed(42)
        X = np.random.randn(50, 3)
        y = np.random.randint(0, 2, 50)
        X_scaled, _, _ = standardize(X)
        
        # 训练两次，使用相同的 random_state
        model1 = LogisticRegressionGD(random_state=42)
        model1.fit(X_scaled, y)
        pred1 = model1.predict(X_scaled)
        
        model2 = LogisticRegressionGD(random_state=42)
        model2.fit(X_scaled, y)
        pred2 = model2.predict(X_scaled)
        
        # 结果应该完全一致
        assert np.array_equal(pred1, pred2)


