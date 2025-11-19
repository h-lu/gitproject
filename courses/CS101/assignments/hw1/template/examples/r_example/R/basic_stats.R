# 基础统计函数
# 这是一个简单的 R 编程练习示例

#' 计算向量的均值
#'
#' @param x 数值向量
#' @return 均值
#' @export
#' @examples
#' calculate_mean(c(1, 2, 3, 4, 5))
calculate_mean <- function(x) {
  if (!is.numeric(x)) {
    stop("Input must be numeric")
  }
  if (length(x) == 0) {
    return(NA_real_)
  }
  return(sum(x) / length(x))
}

#' 计算向量的方差
#'
#' @param x 数值向量
#' @param sample 是否使用样本方差 (n-1)，默认为 TRUE
#' @return 方差
#' @export
#' @examples
#' calculate_variance(c(1, 2, 3, 4, 5))
calculate_variance <- function(x, sample = TRUE) {
  if (!is.numeric(x)) {
    stop("Input must be numeric")
  }
  if (length(x) == 0) {
    return(NA_real_)
  }
  if (length(x) == 1 && sample) {
    return(NA_real_)
  }
  
  mean_x <- calculate_mean(x)
  squared_diff <- (x - mean_x)^2
  
  if (sample) {
    return(sum(squared_diff) / (length(x) - 1))
  } else {
    return(sum(squared_diff) / length(x))
  }
}

#' 标准化向量
#'
#' 将向量标准化为均值为 0，标准差为 1
#'
#' @param x 数值向量
#' @return 标准化后的向量
#' @export
#' @examples
#' standardize(c(1, 2, 3, 4, 5))
standardize <- function(x) {
  if (!is.numeric(x)) {
    stop("Input must be numeric")
  }
  if (length(x) == 0) {
    return(numeric(0))
  }
  if (length(x) == 1) {
    return(0)
  }
  
  mean_x <- calculate_mean(x)
  sd_x <- sqrt(calculate_variance(x, sample = TRUE))
  
  if (sd_x == 0) {
    return(rep(0, length(x)))
  }
  
  return((x - mean_x) / sd_x)
}

