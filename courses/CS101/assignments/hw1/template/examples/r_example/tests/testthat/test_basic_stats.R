# 测试基础统计函数

library(testthat)

# 加载源文件
source("../../R/basic_stats.R")

test_that("calculate_mean works correctly", {
  # 测试正常情况
  expect_equal(calculate_mean(c(1, 2, 3, 4, 5)), 3)
  expect_equal(calculate_mean(c(10, 20, 30)), 20)
  
  # 测试边界情况
  expect_equal(calculate_mean(c(5)), 5)
  expect_true(is.na(calculate_mean(c())))
  
  # 测试负数
  expect_equal(calculate_mean(c(-1, -2, -3)), -2)
  
  # 测试错误输入
  expect_error(calculate_mean("not numeric"), "Input must be numeric")
})

test_that("calculate_variance works correctly", {
  # 测试样本方差
  x <- c(1, 2, 3, 4, 5)
  expected_var <- 2.5  # 手算：sum((x-3)^2) / 4 = (4+1+0+1+4)/4 = 2.5
  expect_equal(calculate_variance(x, sample = TRUE), expected_var)
  
  # 测试总体方差
  expected_pop_var <- 2.0  # sum((x-3)^2) / 5 = 10/5 = 2.0
  expect_equal(calculate_variance(x, sample = FALSE), expected_pop_var)
  
  # 测试边界情况
  expect_true(is.na(calculate_variance(c())))
  expect_true(is.na(calculate_variance(c(5), sample = TRUE)))
  expect_equal(calculate_variance(c(5), sample = FALSE), 0)
  
  # 测试错误输入
  expect_error(calculate_variance("not numeric"), "Input must be numeric")
})

test_that("standardize works correctly", {
  # 测试正常情况
  x <- c(1, 2, 3, 4, 5)
  standardized <- standardize(x)
  
  # 标准化后均值应接近 0
  expect_equal(mean(standardized), 0, tolerance = 1e-10)
  
  # 标准化后标准差应接近 1
  expect_equal(sd(standardized), 1, tolerance = 1e-10)
  
  # 测试边界情况
  expect_equal(length(standardize(c())), 0)
  expect_equal(standardize(c(5)), 0)
  
  # 测试相同值
  expect_equal(standardize(c(3, 3, 3)), c(0, 0, 0))
  
  # 测试错误输入
  expect_error(standardize("not numeric"), "Input must be numeric")
})

test_that("functions handle NA values", {
  # 注意：当前实现不处理 NA，这里只是示例
  # 实际作业中可以要求学生处理 NA
  x_with_na <- c(1, 2, NA, 4, 5)
  
  # 这些测试会失败，除非学生实现了 NA 处理
  # expect_equal(calculate_mean(x_with_na), mean(x_with_na, na.rm = TRUE))
})

