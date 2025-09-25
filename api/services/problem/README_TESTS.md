# ProblemService Unit Tests

This directory contains comprehensive unit tests for the `ProblemService` class.

## Test Coverage

The test suite covers the following scenarios:

### `create_problem` method:
- ✅ Successful problem creation with grader integration
- ✅ Grader exception handling
- ✅ Account not found handling
- ✅ Repository integration

### `delete_problem` method:
- ✅ Successful problem deletion
- ✅ Repository method verification

### `validate_program` method:
- ✅ Successful program validation
- ✅ Invalid language handling
- ✅ Grader integration

### `import_elabsheet_problem` method:
- ✅ Successful PDF import
- ✅ No file provided handling

### `get_all_problems_by_account` method:
- ✅ Retrieval with query parameters
- ✅ Default parameter handling
- ✅ Empty results handling
- ✅ Repository exception handling
- ✅ Group and permission integration

### General:
- ✅ Service initialization
- ✅ Repository dependency injection
- ✅ Integration test structure (requires database)

## Running the Tests

### Option 1: Using Django's test runner (Recommended)
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python manage.py test api.services.problem.test_problem_service
```

### Option 2: Using the test runner script
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python run_problem_service_tests.py
```

### Option 3: Using unittest directly
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python -m unittest api.services.problem.test_problem_service
```

## Test Structure

### Unit Tests (`TestProblemService`)
- Uses mocked dependencies
- Fast execution
- No database required
- Tests business logic in isolation

### Integration Tests (`TestProblemServiceIntegration`)
- Uses real repository implementation
- Requires database setup
- Tests end-to-end functionality
- Currently skipped in unit test runs

## Mocking Strategy

The tests use the following mocking approach:

1. **Repository Mocking**: All repositories are mocked to isolate the service layer
2. **External Dependencies**: Grader classes are mocked
3. **Request Objects**: Django request objects are mocked
4. **Model Objects**: Problem, Account, and Testcase model instances are mocked
5. **Serializers**: Django REST Framework serializers are mocked

## Test Data

The tests use consistent test data:
- Sample problem data with realistic fields
- Various programming languages
- Different testcase scenarios
- Edge cases (empty data, missing fields)

## Assertions

Each test verifies:
- Correct method calls to dependencies
- Proper parameter passing
- Expected return value structure
- Exception handling
- Data integrity

## Dependencies

The ProblemService has the following dependencies:
- `ProblemRepository` - Core problem operations
- `AccountRepository` - Account management
- `PermissionRepository` - Permission handling
- `GroupRepository` - Group operations
- `TopicRepository` - Topic management
- `PythonGrader` - Code execution
- `Grader` - Language-specific graders

## Future Enhancements

Consider adding:
- Performance tests
- Security tests (code execution)
- Concurrent access tests
- Memory usage tests
- More edge case scenarios
- Integration with real graders
