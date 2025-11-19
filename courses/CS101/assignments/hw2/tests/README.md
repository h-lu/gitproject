# HW2 Private Tests Repository

This repository contains private test cases and grading materials for **CS101 HW2 (Java/Gradle)**.

## Repository Structure

```
hw2-tests/
├── README.md                           # This file
├── llm/
│   └── rubric.json                     # LLM grading rubric for short answers
├── objective/
│   └── standard_answers.json          # Correct answers for objective questions
└── java/
    └── src/test/java/com/example/
        └── CalculatorPrivateTest.java  # Private JUnit tests
```

## Contents

### 1. Java Tests (`java/`)

Private JUnit 5 test cases for the Calculator class that students don't see until after grading.

**Test Coverage:**
- Edge cases (negative numbers, zero, large numbers)
- Error handling (division by zero)
- Floating point precision
- Boundary conditions

**Usage in Workflow:**
The `grade.yml` workflow will:
1. Clone this repository
2. Copy `java/src/test/` to the student's repository
3. Run all tests (public + private) using Gradle
4. Generate grade from JUnit XML results

### 2. LLM Rubric (`llm/rubric.json`)

Grading criteria for the three short answer questions:
- **SA1**: Java vs Python (10 points)
- **SA2**: Gradle build system (10 points)
- **SA3**: OOP Encapsulation (10 points)

**Criteria:**
- Accuracy (50%): Factual correctness
- Completeness (30%): Addresses all parts
- Clarity (20%): Well-organized and clear

### 3. Objective Answers (`objective/standard_answers.json`)

Correct answers for objective questions:

**Multiple Choice (20 points):**
- Q1: B (Bytecode)
- Q2: C (private)

**True/False (10 points):**
- Q1: false (`.java`, not `.class`)
- Q2: true (Strings are immutable)

## Grading Workflow

### Programming (40 points)
```bash
# Clone student repo
# Clone hw2-tests
# Copy private tests
rsync -a hw2-tests/java/src/test/ student-repo/src/test/

# Run all tests
gradle test --no-daemon

# Parse JUnit XML → grade.json
python .autograde/grade.py --junit build/test-results/test/TEST-*.xml
```

### Objective Questions (30 points)
```bash
# Fetch standard answers
# Compare with student answers
python .autograde/objective_grade.py \
  --answers objective_answers/my_answers.json \
  --standard hw2-tests/objective/standard_answers.json
```

### LLM Short Answers (30 points)
```bash
# Fetch rubric
# Grade each answer with LLM API
python .autograde/llm_grade.py \
  --question questions/sa1.md \
  --answer answers/sa1.md \
  --rubric hw2-tests/llm/rubric.json
```

## Maintenance

### Adding New Test Cases
1. Edit `java/src/test/java/com/example/CalculatorPrivateTest.java`
2. Ensure tests follow JUnit 5 conventions
3. Test locally before committing:
   ```bash
   # In a test environment
   gradle test
   ```

### Updating Rubric
1. Edit `llm/rubric.json`
2. Adjust weights or criteria as needed
3. Ensure `max_score` matches total points (30)

### Updating Objective Answers
1. Edit `objective/standard_answers.json`
2. Update `max_scores` if question distribution changes
3. Verify JSON format is correct

## Security

**⚠️ IMPORTANT:**
- This repository should be **PRIVATE**
- Only accessible to instructors/graders
- Students should NOT have read access
- Use `RUNNER_TESTS_TOKEN` with minimal permissions (read-only)

## Integration

This repository is referenced in three workflow files:
- `.gitea/workflows/grade.yml` - For Java tests
- `.gitea/workflows/llm_autograde.yml` - For LLM rubric
- `.gitea/workflows/objective_grade.yml` - For objective answers

All workflows use `${ORG}/hw2-tests` repository naming pattern.
