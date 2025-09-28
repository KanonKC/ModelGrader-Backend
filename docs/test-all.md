# All Tests Runner Guide

This guide explains how to use the comprehensive test runner for all ModelGrader-Backend service unit tests.

## 🚀 Quick Start

```bash
# Navigate to project directory
cd /Users/kanon.che/Documents/ModelGrader-Backend

# Run all tests (simplest command)
python run_all_tests.py

# Run with verbose output
python run_all_tests.py --verbose

# Run with coverage analysis
python run_all_tests.py --coverage
```

## 📋 Available Options

### Basic Usage
```bash
python run_all_tests.py [options]
```

### Options
- `--verbose, -v` : Run with detailed output showing each test
- `--coverage, -c` : Run with coverage analysis and HTML report
- `--services, -s` : Run specific services (comma-separated)
- `--help, -h` : Show help message

## 🎯 Examples

### Run All Tests
```bash
# Basic run
python run_all_tests.py

# With verbose output
python run_all_tests.py --verbose
```

### Run Specific Services
```bash
# Run only AccountService tests
python run_all_tests.py --services account

# Run AccountService and AuthService tests
python run_all_tests.py --services account,auth

# Run ProblemService and AuthService tests
python run_all_tests.py --services problem,auth
```

### Run with Coverage
```bash
# Run all tests with coverage
python run_all_tests.py --coverage

# Run specific services with coverage
python run_all_tests.py --coverage --services account,auth

# Verbose output with coverage
python run_all_tests.py --verbose --coverage
```

## 📊 What Gets Tested

The test runner executes unit tests for:

### AccountService
- ✅ Account creation, retrieval, and listing
- ✅ Error handling and edge cases
- ✅ Data validation and serialization

### ProblemService  
- ✅ Problem creation and deletion
- ✅ Program validation
- ✅ File import functionality
- ✅ Account-based problem retrieval

### AuthService
- ✅ Token verification and management
- ✅ Login/logout functionality
- ✅ Authorization checks
- ✅ Security scenarios (expired tokens, wrong passwords)

## 📈 Output Examples

### Basic Output
```
🚀 Starting ModelGrader-Backend Service Tests
============================================================
📦 Adding AccountService tests...
  ✅ Unit tests added
📦 Adding ProblemService tests...
  ✅ Unit tests added
📦 Adding AuthService tests...
  ✅ Unit tests added
  ✅ Module function tests added

🏃 Running tests...
------------------------------------------------------------
.....
============================================================
📊 TEST EXECUTION SUMMARY
============================================================
Total Tests Run:    45
✅ Passed:          45
❌ Failed:          0
💥 Errors:          0
⏭️  Skipped:        0
📈 Success Rate:    100.0%

🎯 Overall Result: ✅ ALL TESTS PASSED!
============================================================
```

### Verbose Output
```
🚀 Starting ModelGrader-Backend Service Tests
============================================================
📋 Services to test: account, problem, auth
🔧 Verbose mode: ON
📊 Coverage mode: OFF

📦 Adding AccountService tests...
  ✅ Unit tests added
📦 Adding ProblemService tests...
  ✅ Unit tests added
📦 Adding AuthService tests...
  ✅ Unit tests added
  ✅ Module function tests added

🏃 Running tests...
------------------------------------------------------------
test_create_account_success (api.services.account.test_account_service.TestAccountService) ... ok
test_get_account_success (api.services.account.test_account_service.TestAccountService) ... ok
test_verify_token_success (api.services.auth.test_auth_service.TestAuthService) ... ok
...
```

### Coverage Output
```
🔍 Running tests with coverage analysis...
🚀 Starting ModelGrader-Backend Service Tests
============================================================
...
📊 Coverage Report:
==================================================
Name                                    Stmts   Miss  Cover   Missing
---------------------------------------------------------------------
api/services/account/account_service.py     72      0   100%
api/services/auth/auth_service.py          137      0   100%
api/services/problem/problem_service.py    285      0   100%
---------------------------------------------------------------------
TOTAL                                       494      0   100%

📁 Generating HTML coverage report...
HTML report generated in 'htmlcov' directory
```

## 🛠️ Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Make sure you're in the project directory
cd /Users/kanon.che/Documents/ModelGrader-Backend

# Check Django setup
python manage.py check
```

**Coverage Not Working:**
```bash
# Install coverage package
pip install coverage

# Or use conda
conda install coverage
```

**Permission Errors:**
```bash
# Make script executable
chmod +x run_all_tests.py

# Or run with python explicitly
python run_all_tests.py
```

### Exit Codes
- `0` : All tests passed
- `1` : Some tests failed or error occurred

## 🔧 Advanced Usage

### Custom Test Selection
```bash
# Run only unit tests (skip integration)
python run_all_tests.py --services account

# Run with specific verbosity
python run_all_tests.py --verbose
```

### Integration with CI/CD
```bash
# For continuous integration
python run_all_tests.py --coverage

# Check exit code
if [ $? -eq 0 ]; then
    echo "All tests passed!"
else
    echo "Tests failed!"
    exit 1
fi
```

## 📁 File Structure

```
ModelGrader-Backend/
├── run_all_tests.py              # Main test runner
├── ALL_TESTS_GUIDE.md           # This guide
├── TEST_COMMANDS.md             # Individual service commands
├── api/services/
│   ├── account/
│   │   ├── test_account_service.py
│   │   └── README_TESTS.md
│   ├── problem/
│   │   ├── test_problem_service.py
│   │   └── README_TESTS.md
│   └── auth/
│       ├── test_auth_service.py
│       └── README_TESTS.md
└── htmlcov/                     # Coverage reports (generated)
```

## 🎉 Benefits

- **Single Command**: Run all service tests with one command
- **Flexible**: Choose which services to test
- **Comprehensive**: Includes coverage analysis
- **User-Friendly**: Clear output and error messages
- **CI/CD Ready**: Proper exit codes and structured output
- **Extensible**: Easy to add new services

## 🔄 Regular Usage

For daily development:
```bash
# Quick test run
python run_all_tests.py

# Before committing
python run_all_tests.py --coverage --verbose
```

For debugging:
```bash
# Test specific service
python run_all_tests.py --services account --verbose

# Check coverage
python run_all_tests.py --coverage
```

