"""
隐藏测试：鲁棒性（更严格）

测试异常输入、边界情况、数值稳定性
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD


class TestRobust:
    """测试鲁棒性（隐藏测试）"""
    
    def test_high_dimensional_data(self):
        """测试高维数据"""
        np.random.seed(42)
        X = np.random.randn(50, 50)  # 50 个特征
        y = np.random.randint(0, 2, 50)
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X, y)
        
        pred = model.predict(X)
        assert pred.shape == (50,)
        assert np.all(np.isin(pred, [0, 1]))
    
    def test_imbalanced_classes(self):
        """测试类别不平衡"""
        # 严重不平衡：90% 正类，10% 负类
        np.random.seed(42)
        X = np.random.randn(100, 3)
        y = np.concatenate([np.ones(90), np.zeros(10)])
        np.random.shuffle(y)
        
        X_scaled, _, _ = standardize(X)
        model = LogisticRegressionGD(random_state=42)
        model.fit(X_scaled, y)
        
        # 应该能够处理不平衡数据
        pred = model.predict(X_scaled)
        assert pred.shape == (100,)
    
    def test_near_zero_features(self):
        """测试接近零的特征（数值稳定性）"""
        X = np.array([
            [1e-10, 2e-10],
            [3e-10, 4e-10],
            [5e-10, 6e-10]
        ])
        y = np.array([0, 1, 0])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X, y)
        
        # 不应该崩溃
        pred = model.predict(X)
        assert np.all(np.isfinite(pred))
    
    def test_constant_features(self):
        """测试常数特征（标准差为 0）"""
        X = np.array([
            [1, 5],  # 第一列变化，第二列常数
            [2, 5],
            [3, 5]
        ])
        y = np.array([0, 1, 0])
        
        from src.utils.preprocess import standardize
        X_scaled, mean, std = standardize(X)
        
        # 标准化应该处理常数特征
        model = LogisticRegressionGD(random_state=42)
        model.fit(X_scaled, y)
        
        pred = model.predict(X_scaled)
        assert pred.shape == (3,)
    
    def test_many_samples_few_features(self):
        """测试样本多但特征少的情况"""
        np.random.seed(42)
        X = np.random.randn(1000, 2)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        
        X_scaled, _, _ = standardize(X)
        model = LogisticRegressionGD(lr=0.1, n_iters=500, random_state=42)
        model.fit(X_scaled, y)
        
        pred = model.predict(X_scaled)
        accuracy = np.mean(pred == y)
        # 大数据集应该达到高准确率
        assert accuracy >= 0.95

