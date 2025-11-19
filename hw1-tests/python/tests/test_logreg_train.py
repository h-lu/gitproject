"""
隐藏测试：训练性能（更严格）

测试在真实数据集上的性能要求
"""

import pytest
import numpy as np
import pandas as pd
from src.models.logistic_regression import LogisticRegressionGD
from src.utils.preprocess import standardize, train_test_split
import os


class TestPerf:
    """测试训练性能（隐藏测试）"""
    
    def test_train_on_hidden_dataset(self):
        """在隐藏数据集上测试训练性能"""
        # 检查是否有隐藏数据集
        data_path = os.path.join(os.path.dirname(__file__), '../data/breast_cancer_hidden.csv')
        
        if not os.path.exists(data_path):
            pytest.skip("Hidden dataset not found")
        
        # 加载数据
        df = pd.read_csv(data_path)
        X = df.iloc[:, :-1].values
        y = df.iloc[:, -1].values
        
        # 标准化
        X_scaled, _, _ = standardize(X)
        
        # 划分训练测试集
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # 训练模型
        model = LogisticRegressionGD(lr=0.1, n_iters=1000, random_state=42)
        model.fit(X_train, y_train)
        
        # 测试集性能
        pred = model.predict(X_test)
        accuracy = np.mean(pred == y_test)
        
        # 隐藏测试要求更高的准确率
        assert accuracy >= 0.9, f"Accuracy {accuracy:.3f} is below 0.9"
    
    def test_train_with_regularization(self):
        """测试带正则化的训练"""
        np.random.seed(42)
        n_samples = 200
        n_features = 20
        X = np.random.randn(n_samples, n_features)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        
        X_scaled, _, _ = standardize(X)
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42
        )
        
        # 带正则化训练
        model = LogisticRegressionGD(
            lr=0.1, 
            n_iters=1000, 
            reg_lambda=0.1, 
            random_state=42
        )
        model.fit(X_train, y_train)
        
        # 应该仍能达到较高准确率
        pred = model.predict(X_test)
        accuracy = np.mean(pred == y_test)
        assert accuracy >= 0.85
    
    def test_convergence_speed(self):
        """测试收敛速度（确保不会太慢）"""
        np.random.seed(42)
        X = np.random.randn(100, 3)
        y = (X[:, 0] + X[:, 1] > 0).astype(int)
        X_scaled, _, _ = standardize(X)
        
        # 使用较少的迭代次数，应该仍能收敛
        model = LogisticRegressionGD(lr=0.1, n_iters=200, random_state=42)
        model.fit(X_scaled, y)
        
        pred = model.predict(X_scaled)
        accuracy = np.mean(pred == y)
        # 即使迭代次数较少，也应该达到合理准确率
        assert accuracy >= 0.8

