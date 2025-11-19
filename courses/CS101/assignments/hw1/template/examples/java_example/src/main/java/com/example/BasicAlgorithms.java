package com.example;

/**
 * 基础算法实现
 * 这是一个简单的 Java 编程练习示例
 */
public class BasicAlgorithms {
    
    /**
     * 计算第 n 个斐波那契数
     * 
     * @param n 序号（从 0 开始）
     * @return 第 n 个斐波那契数
     * @throws IllegalArgumentException 如果 n < 0
     */
    public static int fibonacci(int n) {
        if (n < 0) {
            throw new IllegalArgumentException("n must be non-negative");
        }
        
        if (n == 0) {
            return 0;
        }
        if (n == 1) {
            return 1;
        }
        
        int prev = 0;
        int curr = 1;
        
        for (int i = 2; i <= n; i++) {
            int next = prev + curr;
            prev = curr;
            curr = next;
        }
        
        return curr;
    }
    
    /**
     * 判断一个数是否为质数
     * 
     * @param n 待判断的数
     * @return 如果是质数返回 true，否则返回 false
     */
    public static boolean isPrime(int n) {
        if (n <= 1) {
            return false;
        }
        if (n == 2) {
            return true;
        }
        if (n % 2 == 0) {
            return false;
        }
        
        // 只需检查到 sqrt(n)
        int sqrt = (int) Math.sqrt(n);
        for (int i = 3; i <= sqrt; i += 2) {
            if (n % i == 0) {
                return false;
            }
        }
        
        return true;
    }
    
    /**
     * 反转数组
     * 
     * @param arr 待反转的数组
     * @return 反转后的新数组
     * @throws IllegalArgumentException 如果数组为 null
     */
    public static int[] reverseArray(int[] arr) {
        if (arr == null) {
            throw new IllegalArgumentException("Array cannot be null");
        }
        
        int[] result = new int[arr.length];
        
        for (int i = 0; i < arr.length; i++) {
            result[i] = arr[arr.length - 1 - i];
        }
        
        return result;
    }
    
    /**
     * 计算数组中的最大值
     * 
     * @param arr 数组
     * @return 最大值
     * @throws IllegalArgumentException 如果数组为 null 或空
     */
    public static int findMax(int[] arr) {
        if (arr == null || arr.length == 0) {
            throw new IllegalArgumentException("Array cannot be null or empty");
        }
        
        int max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        
        return max;
    }
}

