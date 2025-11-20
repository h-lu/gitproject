# Data Analysis Functions
# 实现数据分析工具集

#' Calculate basic statistics
#' 
#' @param data numeric vector
#' @return list with mean, median, and sd
calculate_statistics <- function(data) {
  # TODO: 实现统计计算
  # 返回 list(mean = ..., median = ..., sd = ...)
  
  stop("Not implemented")
}

#' Filter outliers using IQR method
#' 
#' @param data numeric vector
#' @param method outlier detection method (default: "iqr")
#' @return filtered data without outliers
filter_outliers <- function(data, method = "iqr") {
  # TODO: 使用IQR方法去除异常值
  # Q1 = quantile(data, 0.25)
  # Q3 = quantile(data, 0.75)
  # IQR = Q3 - Q1
  # 保留 [Q1 - 1.5*IQR, Q3 + 1.5*IQR] 范围内的数据
  
  stop("Not implemented")
}

#' Build linear regression model
#' 
#' @param x predictor variable
#' @param y response variable
#' @return lm model object
build_linear_model <- function(x, y) {
  # TODO: 构建线性回归模型
  # 使用 lm(y ~ x)
  
  stop("Not implemented")
}

#' Predict values using model
#' 
#' @param model lm model object
#' @param new_x new predictor values
#' @return predicted values
predict_values <- function(model, new_x) {
  # TODO: 使用模型进行预测
  # 使用 predict() 函数
  
  stop("Not implemented")
}
