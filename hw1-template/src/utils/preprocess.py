"""
数据预处理工具函数
"""

import numpy as np


def standardize(X: np.ndarray, mean=None, std=None):
    """
    标准化特征（Z-score normalization）
    
    使用数值稳定的方法计算均值和标准差，避免除零错误
    
    Parameters
    ----------
    X : np.ndarray, shape (n_samples, n_features)
        输入特征
    mean : np.ndarray, optional
        均值（用于测试集，需使用训练集的均值）
    std : np.ndarray, optional
        标准差（用于测试集，需使用训练集的标准差）
    
    Returns
    -------
    X_scaled : np.ndarray
        标准化后的特征
    mean : np.ndarray
        均值
    std : np.ndarray
        标准差
    """
    if mean is None or std is None:
        # 使用 ddof=0 计算总体标准差（与 sklearn 默认一致）
        mean = np.mean(X, axis=0, dtype=np.float64)
        std = np.std(X, axis=0, dtype=np.float64, ddof=0)
        # 避免除零：如果标准差为 0，设为 1（该特征为常数）
        std = np.where(std == 0, 1.0, std)
    
    # 数值稳定的标准化
    X_scaled = (X - mean) / std
    return X_scaled, mean, std


def train_test_split(X, y, test_size=0.2, random_state=None):
    """
    简单的训练/测试集划分
    
    Parameters
    ----------
    X : np.ndarray
        特征
    y : np.ndarray
        标签
    test_size : float
        测试集比例
    random_state : int, optional
        随机种子
    
    Returns
    -------
    X_train, X_test, y_train, y_test
    """
    if random_state is not None:
        np.random.seed(random_state)
    
    n_samples = X.shape[0]
    n_test = int(n_samples * test_size)
    indices = np.random.permutation(n_samples)
    
    test_indices = indices[:n_test]
    train_indices = indices[n_test:]
    
    return X[train_indices], X[test_indices], y[train_indices], y[test_indices]


