"""
隐藏测试：逻辑回归基本 API 测试（更严格）

包含比公开测试更严格的验证
"""

import pytest
import numpy as np
from src.models.logistic_regression import LogisticRegressionGD


class TestAPI:
    """测试 API 正确性（隐藏测试）"""
    
    def test_init_with_reg(self):
        """测试带正则化的初始化"""
        model = LogisticRegressionGD(lr=0.01, n_iters=2000, reg_lambda=0.1, random_state=42)
        assert model.reg_lambda == 0.1
        assert model.fit_intercept is True
    
    def test_fit_intercept_false(self):
        """测试不拟合截距项"""
        X = np.array([[1, 2], [3, 4], [5, 6]])
        y = np.array([0, 1, 0])
        model = LogisticRegressionGD(fit_intercept=False, random_state=42)
        model.fit(X, y)
        assert model.bias is None or model.bias == 0
    
    def test_predict_proba_values(self):
        """测试 predict_proba 返回合理的概率值"""
        X_train = np.array([[1, 2], [3, 4], [5, 6], [10, 11], [12, 13]])
        y_train = np.array([0, 0, 0, 1, 1])
        X_test = np.array([[2, 3], [11, 12]])
        
        model = LogisticRegressionGD(lr=0.1, n_iters=1000, random_state=42)
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)
        
        # 第一个样本应该更接近 0，第二个更接近 1
        assert proba[0] < 0.5
        assert proba[1] > 0.5
        assert np.all((proba >= 0) & (proba <= 1))
    
    def test_predict_consistency(self):
        """测试 predict 与 predict_proba 的一致性"""
        X_train = np.array([[1, 2], [3, 4], [5, 6]])
        y_train = np.array([0, 1, 0])
        X_test = np.array([[2, 3], [4, 5]])
        
        model = LogisticRegressionGD(random_state=42)
        model.fit(X_train, y_train)
        
        proba = model.predict_proba(X_test)
        pred_default = model.predict(X_test)
        pred_custom = model.predict(X_test, threshold=0.5)
        
        # 默认阈值应该与 0.5 阈值一致
        assert np.array_equal(pred_default, pred_custom)
        
        # predict 应该与 proba > threshold 一致
        expected = (proba > 0.5).astype(int)
        assert np.array_equal(pred_default, expected)

