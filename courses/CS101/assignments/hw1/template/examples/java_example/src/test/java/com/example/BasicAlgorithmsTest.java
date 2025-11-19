package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import static org.junit.jupiter.api.Assertions.*;

/**
 * BasicAlgorithms 的单元测试
 */
public class BasicAlgorithmsTest {
    
    @Test
    @DisplayName("测试斐波那契数列 - 基本情况")
    public void testFibonacciBasic() {
        assertEquals(0, BasicAlgorithms.fibonacci(0));
        assertEquals(1, BasicAlgorithms.fibonacci(1));
        assertEquals(1, BasicAlgorithms.fibonacci(2));
        assertEquals(2, BasicAlgorithms.fibonacci(3));
        assertEquals(3, BasicAlgorithms.fibonacci(4));
        assertEquals(5, BasicAlgorithms.fibonacci(5));
    }
    
    @Test
    @DisplayName("测试斐波那契数列 - 较大的值")
    public void testFibonacciLarge() {
        assertEquals(55, BasicAlgorithms.fibonacci(10));
        assertEquals(6765, BasicAlgorithms.fibonacci(20));
    }
    
    @Test
    @DisplayName("测试斐波那契数列 - 负数输入")
    public void testFibonacciNegative() {
        assertThrows(IllegalArgumentException.class, () -> {
            BasicAlgorithms.fibonacci(-1);
        });
    }
    
    @Test
    @DisplayName("测试质数判断 - 小质数")
    public void testIsPrimeSmall() {
        assertFalse(BasicAlgorithms.isPrime(0));
        assertFalse(BasicAlgorithms.isPrime(1));
        assertTrue(BasicAlgorithms.isPrime(2));
        assertTrue(BasicAlgorithms.isPrime(3));
        assertFalse(BasicAlgorithms.isPrime(4));
        assertTrue(BasicAlgorithms.isPrime(5));
        assertFalse(BasicAlgorithms.isPrime(6));
        assertTrue(BasicAlgorithms.isPrime(7));
    }
    
    @Test
    @DisplayName("测试质数判断 - 较大的数")
    public void testIsPrimeLarge() {
        assertTrue(BasicAlgorithms.isPrime(97));
        assertTrue(BasicAlgorithms.isPrime(101));
        assertFalse(BasicAlgorithms.isPrime(100));
        assertFalse(BasicAlgorithms.isPrime(99));
    }
    
    @Test
    @DisplayName("测试数组反转 - 基本情况")
    public void testReverseArrayBasic() {
        assertArrayEquals(
            new int[]{5, 4, 3, 2, 1},
            BasicAlgorithms.reverseArray(new int[]{1, 2, 3, 4, 5})
        );
        
        assertArrayEquals(
            new int[]{3, 2, 1},
            BasicAlgorithms.reverseArray(new int[]{1, 2, 3})
        );
    }
    
    @Test
    @DisplayName("测试数组反转 - 边界情况")
    public void testReverseArrayEdgeCases() {
        // 空数组
        assertArrayEquals(
            new int[]{},
            BasicAlgorithms.reverseArray(new int[]{})
        );
        
        // 单元素数组
        assertArrayEquals(
            new int[]{42},
            BasicAlgorithms.reverseArray(new int[]{42})
        );
    }
    
    @Test
    @DisplayName("测试数组反转 - null 输入")
    public void testReverseArrayNull() {
        assertThrows(IllegalArgumentException.class, () -> {
            BasicAlgorithms.reverseArray(null);
        });
    }
    
    @Test
    @DisplayName("测试查找最大值 - 基本情况")
    public void testFindMaxBasic() {
        assertEquals(5, BasicAlgorithms.findMax(new int[]{1, 2, 3, 4, 5}));
        assertEquals(10, BasicAlgorithms.findMax(new int[]{10, 5, 3, 7, 2}));
        assertEquals(100, BasicAlgorithms.findMax(new int[]{100}));
    }
    
    @Test
    @DisplayName("测试查找最大值 - 负数")
    public void testFindMaxNegative() {
        assertEquals(-1, BasicAlgorithms.findMax(new int[]{-5, -3, -1, -10}));
        assertEquals(5, BasicAlgorithms.findMax(new int[]{-5, 0, 5, -10}));
    }
    
    @Test
    @DisplayName("测试查找最大值 - 异常情况")
    public void testFindMaxExceptions() {
        assertThrows(IllegalArgumentException.class, () -> {
            BasicAlgorithms.findMax(null);
        });
        
        assertThrows(IllegalArgumentException.class, () -> {
            BasicAlgorithms.findMax(new int[]{});
        });
    }
}

