# AuthService Unit Tests

This directory contains comprehensive unit tests for the `AuthService` class.

## Test Coverage

The test suite covers the following scenarios:

### `verify_token` method:
- ✅ Successful token verification
- ✅ Expired token handling
- ✅ Account not found handling
- ✅ Repository exception handling

### `getAccountByToken` method:
- ✅ Successful account retrieval
- ✅ Expired token handling
- ✅ Account not found handling
- ✅ Repository exception handling

### `login` method:
- ✅ Successful login with token generation
- ✅ Incorrect password handling
- ✅ User not found handling
- ✅ Repository exception handling
- ✅ Token expiration setting

### `authorization` method:
- ✅ Successful authorization
- ✅ Expired token handling
- ✅ Wrong token handling
- ✅ Account not found handling
- ✅ Repository exception handling

### `logout` method:
- ✅ Successful logout
- ✅ Wrong token handling
- ✅ Account not found handling
- ✅ Repository exception handling
- ✅ Token clearing

### Module-level functions:
- ✅ `verify_token` function
- ✅ `getAccountByToken` function

### General:
- ✅ Service initialization
- ✅ Configuration dependency injection
- ✅ Integration test structure (requires database)

## Running the Tests

### Option 1: Using Django's test runner (Recommended)
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python manage.py test api.services.auth.test_auth_service
```

### Option 2: Using the test runner script
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python run_auth_service_tests.py
```

### Option 3: Using unittest directly
```bash
cd /Users/kanon.che/Documents/ModelGrader-Backend
python -m unittest api.services.auth.test_auth_service
```

## Test Structure

### Unit Tests (`TestAuthService`)
- Uses mocked dependencies
- Fast execution
- No database required
- Tests authentication logic in isolation

### Integration Tests (`TestAuthServiceIntegration`)
- Uses real repository implementation
- Requires database setup
- Tests end-to-end authentication flow
- Currently skipped in unit test runs

### Module Function Tests (`TestAuthServiceModuleFunctions`)
- Tests backward compatibility functions
- Verifies service instantiation
- Tests function delegation

## Mocking Strategy

The tests use the following mocking approach:

1. **Repository Mocking**: AccountRepository is mocked
2. **Configuration Mocking**: Configuration object is mocked
3. **Time Mocking**: Time functions are mocked for consistent testing
4. **UUID Mocking**: UUID generation is mocked for predictable tokens
5. **Password Encryption**: Password hashing is mocked
6. **Model Conversion**: model_to_dict is mocked
7. **Request Objects**: Django request objects are mocked

## Test Data

The tests use consistent test data:
- Sample account with valid token
- Expired token scenarios
- Invalid token scenarios
- Various authentication states
- Realistic token lifetimes

## Security Considerations

The tests verify:
- Token expiration handling
- Password verification
- Token uniqueness
- Secure logout (token clearing)
- Authorization checks

## Dependencies

The AuthService has the following dependencies:
- `AccountRepository` - Account data access
- `Configuration` - Token lifetime settings
- `passwordEncryption` - Password hashing
- `uuid4` - Token generation
- `time` - Token expiration
- `model_to_dict` - Model serialization

## Error Handling

The tests verify proper handling of:
- `Account.DoesNotExist` - User not found
- `IncorrectPasswordError` - Wrong password
- `InvalidTokenError` - Invalid/expired token
- `ItemNotFoundError` - Missing resources
- General exceptions - Database errors

## Token Management

The tests verify:
- Token generation on login
- Token expiration calculation
- Token validation
- Token clearing on logout
- Token uniqueness

## Future Enhancements

Consider adding:
- Rate limiting tests
- Concurrent login tests
- Token refresh tests
- Session management tests
- Security vulnerability tests
- Performance tests
- Multi-device login tests
