"""
逻辑回归分类器（基于梯度下降）

实现要求：
1. 仅使用 numpy，禁止使用 sklearn.linear_model.LogisticRegression
2. sigmoid 函数需数值稳定（处理大幅度输入）
3. 支持截距项（fit_intercept）
4. 支持随机种子（random_state）保证可复现
5. 实现 L2 正则化（reg_lambda）
"""

import numpy as np


class LogisticRegressionGD:
    """
    基于梯度下降的二分类逻辑回归模型
    
    Parameters
    ----------
    lr : float, default=0.1
        学习率
    n_iters : int, default=1000
        最大迭代次数
    reg_lambda : float, default=0.0
        L2 正则化系数
    fit_intercept : bool, default=True
        是否拟合截距项
    random_state : int, optional
        随机种子，用于初始化权重
    """
    
    def __init__(self, lr=0.1, n_iters=1000, reg_lambda=0.0, 
                 fit_intercept=True, random_state=None):
        # TODO: 初始化参数
        self.lr = lr
        self.n_iters = n_iters
        self.reg_lambda = reg_lambda
        self.fit_intercept = fit_intercept
        self.random_state = random_state
        
        # TODO: 初始化权重（在 fit 中完成）
        self.weights = None
        self.bias = None
    
    def _sigmoid(self, z):
        """
        数值稳定的 sigmoid 函数
        
        使用 clip 和 exp 的数值稳定形式避免溢出
        
        Parameters
        ----------
        z : np.ndarray
            输入值
        
        Returns
        -------
        np.ndarray
            sigmoid 输出
        """
        # TODO: 实现数值稳定的 sigmoid
        # 提示：对于 z 很大或很小时，使用 clip 限制范围
        # 或者使用：1 / (1 + np.exp(-np.clip(z, -250, 250)))
        # 这样可以避免 exp 溢出
        pass
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> "LogisticRegressionGD":
        """
        训练模型
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            训练特征
        y : np.ndarray, shape (n_samples,)
            训练标签（0 或 1）
        
        Returns
        -------
        self : LogisticRegressionGD
            返回自身以支持链式调用
        """
        # TODO: 实现训练逻辑
        # 1. 数据预处理（标准化、添加截距项）
        # 2. 初始化权重（使用 random_state）
        # 3. 梯度下降迭代
        # 4. 更新权重（考虑 L2 正则化）
        pass
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        预测概率
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            测试特征
        
        Returns
        -------
        np.ndarray, shape (n_samples,)
            预测为正类的概率
        """
        # TODO: 实现概率预测
        pass
    
    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """
        预测类别
        
        Parameters
        ----------
        X : np.ndarray, shape (n_samples, n_features)
            测试特征
        threshold : float, default=0.5
            分类阈值
        
        Returns
        -------
        np.ndarray, shape (n_samples,)
            预测类别（0 或 1）
        """
        # TODO: 基于 predict_proba 实现类别预测
        pass


