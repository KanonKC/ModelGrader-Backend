# AccountService Unit Tests

This directory contains comprehensive unit tests for the `AccountService` class.

## Test Coverage

The test suite covers the following scenarios:

### `create_account` method:
- ✅ Successful account creation with password encryption
- ✅ Repository exception handling
- ✅ Data mutation prevention
- ✅ Minimal data handling

### `get_account` method:
- ✅ Successful account retrieval
- ✅ Account not found (DoesNotExist exception)
- ✅ Repository exception handling
- ✅ Different ID format handling

### `get_all_accounts` method:
- ✅ Retrieval without search query
- ✅ Retrieval with search query
- ✅ Empty result handling
- ✅ Repository exception handling
- ✅ Missing/empty search parameter handling

### General:
- ✅ Service initialization
- ✅ Error handling consistency
- ✅ Integration test structure (requires database)

## Running the Tests

### Option 1: Using Django's test runner (Recommended)
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python manage.py test api.services.account.test_account_service
```

### Option 2: Using Django's test runner with specific test class
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python manage.py test api.services.account.test_account_service.TestAccountService
```

### Option 3: Using Django's test runner with specific test method
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python manage.py test api.services.account.test_account_service.TestAccountService.test_create_account_success
```

### Option 4: Using Django's test runner with verbose output
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python manage.py test api.services.account.test_account_service --verbosity=2
```

### Option 5: Using Django's test runner with coverage
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
coverage run --source='.' manage.py test api.services.account.test_account_service
coverage report
coverage html
```

### Option 6: Using unittest directly (requires Django setup)
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python -m unittest api.services.account.test_account_service
```

### Option 7: Using pytest (if installed)
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
pytest api/services/account/test_account_service.py -v
```

## Test Structure

### Unit Tests (`TestAccountService`)
- Uses mocked dependencies
- Fast execution
- No database required
- Tests business logic in isolation

### Integration Tests (`TestAccountServiceIntegration`)
- Uses real repository implementation
- Requires database setup
- Tests end-to-end functionality
- Currently skipped in unit test runs

## Mocking Strategy

The tests use the following mocking approach:

1. **Repository Mocking**: `AccountRepository` is mocked to isolate the service layer
2. **External Dependencies**: `passwordEncryption` function is mocked
3. **Request Objects**: Django request objects are mocked
4. **Model Objects**: Account model instances are mocked

## Test Data

The tests use consistent test data:
- Sample account data with realistic fields
- Various account ID formats
- Different search scenarios
- Edge cases (empty data, missing fields)

## Assertions

Each test verifies:
- Correct method calls to dependencies
- Proper parameter passing
- Expected return value structure
- Exception handling
- Data integrity

## Future Enhancements

Consider adding:
- Performance tests
- Security tests (password handling)
- Concurrent access tests
- Memory usage tests
- More edge case scenarios
