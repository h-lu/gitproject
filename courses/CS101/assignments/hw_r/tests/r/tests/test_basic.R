# Test basic statistics function
library(testthat)

# Load the source file
source("src/data_analysis.R")

test_that("calculate_statistics works correctly", {
  data <- c(1, 2, 3, 4, 5)
  result <- calculate_statistics(data)
  
  expect_equal(result$mean, 3)
  expect_equal(result$median, 3)
  expect_equal(round(result$sd, 2), 1.58)
})

test_that("filter_outliers removes outliers", {
  # Data with outliers
  data <- c(1, 2, 3, 4, 5, 100)
  filtered <- filter_outliers(data)
  
  expect_true(length(filtered) < length(data))
  expect_false(100 %in% filtered)
})

test_that("build_linear_model creates model", {
  x <- c(1, 2, 3, 4, 5)
  y <- c(2, 4, 6, 8, 10)
  model <- build_linear_model(x, y)
  
  expect_s3_class(model, "lm")
})

test_that("predict_values makes correct predictions", {
  x <- c(1, 2, 3, 4, 5)
  y <- c(2, 4, 6, 8, 10)
  model <- build_linear_model(x, y)
  
  predictions <- predict_values(model, c(6, 7))
  expect_length(predictions, 2)
  expect_equal(round(predictions[1]), 12)
})
