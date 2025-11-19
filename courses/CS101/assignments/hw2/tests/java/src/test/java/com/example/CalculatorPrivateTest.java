package com.example;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Private test cases for Calculator class (hw2-tests repository)
 * These tests are not visible to students but will be run during grading
 */
public class CalculatorPrivateTest {

    private Calculator calculator;

    @BeforeEach
    public void setUp() {
        calculator = new Calculator();
    }

    @Test
    public void testAddNegativeNumbers() {
        assertEquals(-5, calculator.add(-2, -3), "Adding two negative numbers should work correctly");
    }

    @Test
    public void testAddZero() {
        assertEquals(5, calculator.add(5, 0), "Adding zero should return the original number");
        assertEquals(0, calculator.add(0, 0), "Adding zero to zero should return zero");
    }

    @Test
    public void testSubtractNegativeResult() {
        assertEquals(-5, calculator.subtract(3, 8), "Subtraction resulting in negative should work");
    }

    @Test
    public void testSubtractZero() {
        assertEquals(10, calculator.subtract(10, 0), "Subtracting zero should return original");
    }

    @Test
    public void testMultiplyByZero() {
        assertEquals(0, calculator.multiply(100, 0), "Multiplying by zero should return zero");
        assertEquals(0, calculator.multiply(0, 50), "Zero times any number should be zero");
    }

    @Test
    public void testMultiplyNegativeNumbers() {
        assertEquals(6, calculator.multiply(-2, -3), "Negative times negative should be positive");
        assertEquals(-6, calculator.multiply(2, -3), "Positive times negative should be negative");
    }

    @Test
    public void testDivideNegativeNumbers() {
        assertEquals(-2.0, calculator.divide(-6, 3), 0.001, "Dividing negative by positive");
        assertEquals(2.0, calculator.divide(-6, -3), 0.001, "Dividing negative by negative");
    }

    @Test
    public void testDivideWithRemainder() {
        assertEquals(3.333333, calculator.divide(10, 3), 0.001, "Division with remainder should be accurate");
    }

    @Test
    public void testDivideByZeroThrowsException() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            calculator.divide(10, 0);
        });
        assertTrue(exception.getMessage().contains("zero") || exception.getMessage().contains("0"),
                "Exception message should mention division by zero");
    }

    @Test
    public void testLargeNumbers() {
        assertEquals(2000000, calculator.add(1000000, 1000000), "Should handle large numbers");
        assertEquals(1000000000, calculator.multiply(1000, 1000000), "Should handle large multiplication");
    }
}
