"""
公开测试：鲁棒性

测试异常输入、边界情况、数值稳定性
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD


class TestRobust:
    """测试鲁棒性"""
    
    def test_single_sample(self):
        """测试单个样本"""
        X = np.array([[1, 2]])
        y = np.array([1])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X, y)
        
        pred = model.predict(X)
        assert pred.shape == (1,)
        assert pred[0] in [0, 1]
    
    def test_single_feature(self):
        """测试单个特征"""
        X = np.array([[1], [2], [3], [10], [11], [12]])
        y = np.array([0, 0, 0, 1, 1, 1])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X, y)
        
        pred = model.predict(X)
        assert pred.shape == (6,)
    
    def test_all_same_class(self):
        """测试所有样本属于同一类"""
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([1, 1, 1])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X, y)
        
        pred = model.predict(X)
        assert np.all(pred == 1)
    
    def test_large_values(self):
        """测试大数值输入"""
        X = np.array([[100, 200], [300, 400], [500, 600]])
        y = np.array([0, 1, 0])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X, y)
        
        # 不应该崩溃
        pred = model.predict(X)
        assert pred.shape == (3,)
        assert np.all(np.isin(pred, [0, 1]))


