"""
公开测试：逻辑回归基本 API 测试

测试函数签名、输入输出形状、基本功能
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD


class TestAPI:
    """测试 API 正确性"""
    
    def test_init(self):
        """测试初始化"""
        model = LogisticRegressionGD(lr=0.1, n_iters=100, random_state=42)
        assert model.lr == 0.1
        assert model.n_iters == 100
        assert model.reg_lambda == 0.0
        assert model.fit_intercept is True
    
    def test_fit_returns_self(self):
        """测试 fit 返回自身（支持链式调用）"""
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([0, 1, 0])
        model = LogisticRegressionGD(random_state=42)
        result = model.fit(X, y)
        assert result is model
    
    def test_predict_proba_shape(self):
        """测试 predict_proba 输出形状"""
        X_train = np.array([[1, 2], [3, 4], [5, 6]])
        y_train = np.array([0, 1, 0])
        X_test = np.array([[2, 3], [4, 5]])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)
        
        assert proba.shape == (2,)
        assert np.all((proba >= 0) & (proba <= 1))
    
    def test_predict_shape(self):
        """测试 predict 输出形状和值域"""
        X_train = np.array([[1, 2], [3, 4], [5, 6]])
        y_train = np.array([0, 1, 0])
        X_test = np.array([[2, 3], [4, 5]])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X_train, y_train)
        pred = model.predict(X_test)
        
        assert pred.shape == (2,)
        assert np.all(np.isin(pred, [0, 1]))
    
    def test_predict_threshold(self):
        """测试 predict 的阈值参数"""
        X_train = np.array([[1, 2], [3, 4], [5, 6]])
        y_train = np.array([0, 1, 0])
        X_test = np.array([[2, 3]])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X_train, y_train)
        
        # 使用不同阈值
        pred_low = model.predict(X_test, threshold=0.3)
        pred_high = model.predict(X_test, threshold=0.7)
        
        assert pred_low.shape == (1,)
        assert pred_high.shape == (1,)


