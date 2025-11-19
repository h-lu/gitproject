# Homework 2: Java Programming

**Course:** CS101  
**Due Date:** 2025-11-30 23:59:59  
**Total Points:** 100

## Overview

This assignment introduces you to Java programming and the Gradle build system. You will:
- Answer objective questions (multiple choice, true/false)
- Write short answers about Java concepts
- Implement a simple Calculator class

## Getting Started

1. Clone this repository
2. Review the questions in `objective_questions/` and `questions/`
3. Implement the `Calculator` class in `src/main/java/com/example/Calculator.java`
4. Run tests locally:
   ```bash
   gradle test
   ```

## Project Structure

```
.
├── src/
│   ├── main/java/com/example/
│   │   └── Calculator.java          # Your implementation here
│   └── test/java/com/example/
│       └── CalculatorTest.java      # Unit tests
├── objective_questions/             # Objective questions
├── objective_answers/               # Your objective answers
├── questions/                       # Short answer questions
├── answers/                         # Your short answers
├── build.gradle                     # Gradle build configuration
└── settings.gradle                  # Gradle settings
```

## Tasks

### 1. Objective Questions (30 points)
Answer the questions in:`objective_questions/`

Create your answers in `objective_answers/my_answers.json`:
```json
{
  "mc_questions": {
    "1": "A",
    "2": "C"
  },
  "tf_questions": {
    "1": true,
    "2": false
  }
}
```

### 2. Short Answer Questions (30 points)
Answer the questions in `questions/sa1.md`, `questions/sa2.md`, and `questions/sa3.md`

Write your answers in `answers/sa1.md`, `answers/sa2.md`, and `answers/sa3.md`

### 3. Programming Task (40 points)
Implement the `Calculator` class with the following methods:
- `int add(int a, int b)` - Returns the sum of a and b
- `int subtract(int a, int b)` - Returns a minus b
- `int multiply(int a, int b)` - Returns the product of a and b
- `double divide(int a, int b)` - Returns a divided by b (throw `IllegalArgumentException` if b is 0)

## Testing

Run all tests:
```bash
gradle test
```

View test results:
```bash
cat build/test-results/test/*.xml
```

## Submission

Push your changes to the `main` branch. The autograding workflow will:
1. Run your unit tests
2. Grade your objective questions
3. Evaluate your short answers using LLM
4. Calculate your final score

## Grading Breakdown

| Component | Points |
|-----------|--------|
| Objective Questions | 30 |
| Short Answers | 30 |
| Programming | 40 |
| **Total** | **100** |

## Resources

- [Java Documentation](https://docs.oracle.com/en/java/)
- [Gradle User Guide](https://docs.gradle.org/current/userguide/userguide.html)
- [JUnit 5 Documentation](https://junit.org/junit5/docs/current/user-guide/)

## Help

If you encounter issues:
1. Check the workflow logs in Gitea Actions
2. Ensure your code compiles: `gradle build`
3. Verify test coverage: `gradle test`

Good luck!
