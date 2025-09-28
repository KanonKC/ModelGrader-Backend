# Test Commands Reference

This document provides a quick reference for running tests in the ModelGrader-Backend project.

## 🚀 Quick Start

1. **Navigate to your project directory:**
   ```bash
   cd /Users/kanon.che/Documents/ModelGrader-Backend
   ```

2. **Run all service tests:**
   ```bash
   # AccountService tests
   python manage.py test api.services.account.test_account_service
   
   # ProblemService tests
   python manage.py test api.services.problem.test_problem_service
   
   # AuthService tests
   python manage.py test api.services.auth.test_auth_service
   ```

## Quick Commands for All Services

### 🚀 **Most Common Commands**

```bash
# AccountService tests
python manage.py test api.services.account.test_account_service
python manage.py test api.services.account.test_account_service --verbosity=2
python manage.py test api.services.account.test_account_service.TestAccountService

# ProblemService tests
python manage.py test api.services.problem.test_problem_service
python manage.py test api.services.problem.test_problem_service --verbosity=2
python manage.py test api.services.problem.test_problem_service.TestProblemService

# AuthService tests
python manage.py test api.services.auth.test_auth_service
python manage.py test api.services.auth.test_auth_service --verbosity=2
python manage.py test api.services.auth.test_auth_service.TestAuthService

# Run all service tests at once
python manage.py test api.services.account.test_account_service api.services.problem.test_problem_service api.services.auth.test_auth_service
```

### 📊 **Test Coverage Commands**

```bash
# Run tests with coverage for all services
coverage run --source='.' manage.py test api.services.account.test_account_service api.services.problem.test_problem_service api.services.auth.test_auth_service

# Run coverage for individual services
coverage run --source='.' manage.py test api.services.account.test_account_service
coverage run --source='.' manage.py test api.services.problem.test_problem_service
coverage run --source='.' manage.py test api.services.auth.test_auth_service

# View coverage report
coverage report

# Generate HTML coverage report
coverage html
```

### 🔧 **Alternative Test Runners**

```bash
# Using unittest directly
python -m unittest api.services.account.test_account_service

# Using pytest (if installed)
pytest api/services/account/test_account_service.py -v

# Run all tests in the account service directory
python manage.py test api.services.account
```

### 🎯 **Specific Test Scenarios**

```bash
# Test only create_account functionality
python manage.py test api.services.account.test_account_service.TestAccountService.test_create_account_success

# Test only get_account functionality  
python manage.py test api.services.account.test_account_service.TestAccountService.test_get_account_success

# Test only get_all_accounts functionality
python manage.py test api.services.account.test_account_service.TestAccountService.test_get_all_accounts_without_search

# Test error handling
python manage.py test api.services.account.test_account_service.TestAccountService.test_get_account_not_found
```

### 📝 **Test Output Options**

```bash
# Quiet output (minimal)
python manage.py test api.services.account.test_account_service --verbosity=0

# Normal output (default)
python manage.py test api.services.account.test_account_service --verbosity=1

# Verbose output (detailed)
python manage.py test api.services.account.test_account_service --verbosity=2

# Very verbose output (most detailed)
python manage.py test api.services.account.test_account_service --verbosity=3
```

### 🐛 **Debugging Tests**

```bash
# Run tests with debug output
python manage.py test api.services.account.test_account_service --debug-mode

# Run tests and keep test database
python manage.py test api.services.account.test_account_service --keepdb

# Run tests in parallel (if supported)
python manage.py test api.services.account.test_account_service --parallel
```

### 📁 **Directory Structure**

```
ModelGrader-Backend/
├── api/
│   └── services/
│       └── account/
│           ├── account_service.py
│           ├── test_account_service.py
│           ├── README_TESTS.md
│           └── example_test_run.py
├── manage.py
└── TEST_COMMANDS.md
```

### ⚡ **Quick Start**

1. **Navigate to project directory:**
   ```bash
   cd /Users/kanon.che/Documents/ModelGrader-Backend
   ```

2. **Run all tests:**
   ```bash
   python manage.py test api.services.account.test_account_service --verbosity=2
   ```

3. **Check results:**
   - ✅ All tests should pass
   - 📊 Coverage report available
   - 🐛 Any failures will be clearly shown

### 🔍 **Troubleshooting**

**If tests fail:**
- Check Django settings are correct
- Ensure all dependencies are installed
- Verify database is accessible
- Check for import errors

**If coverage is low:**
- Add more test cases
- Test edge cases
- Test error scenarios
- Test integration points
