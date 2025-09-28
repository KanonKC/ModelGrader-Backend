# GitHub Workflows for ModelGrader-Backend

This document explains the GitHub Actions workflows that automatically run tests when pull requests are made to the `main` and `dev` branches.

## 🚀 Quick Start

The workflows will automatically run when you:
1. Create a pull request to `main` or `dev` branches
2. Push commits to `main` or `dev` branches

## 📁 Available Workflows

### 1. `run-tests.yml` (Recommended)
**Best for**: Most use cases
- ✅ Runs all tests using `run_all_tests.py`
- ✅ Tests individual services
- ✅ Includes coverage analysis
- ✅ Fast execution

### 2. `simple-test.yml` (Minimal)
**Best for**: Quick testing
- ✅ Simple and fast
- ✅ Just runs the basic test suite
- ✅ Minimal dependencies

### 3. `test.yml` (Basic)
**Best for**: Standard testing with coverage
- ✅ Runs tests with verbose output
- ✅ Includes coverage analysis
- ✅ Uploads coverage reports

### 4. `ci.yml` (Comprehensive)
**Best for**: Full CI/CD pipeline
- ✅ Multiple test scenarios
- ✅ Code quality checks
- ✅ Matrix testing
- ✅ Artifact uploads

## 🔧 How It Works

### Automatic Triggers
```yaml
on:
  pull_request:
    branches: [ main, dev ]
  push:
    branches: [ main, dev ]
```

### Test Execution
1. **Checkout**: Gets your code
2. **Setup Python**: Installs Python 3.11
3. **Install Dependencies**: Runs `pip install -r requirements.txt`
4. **Run Tests**: Executes `python run_all_tests.py --verbose`
5. **Report Results**: Shows ✅ pass or ❌ fail

### Example Output
```
🚀 Starting ModelGrader-Backend Service Tests
============================================================
📦 Adding SubmissionService tests...
  ✅ Unit tests added
📦 Adding TopicService tests...
  ✅ Unit tests added

🏃 Running tests...
------------------------------------------------------------
..............................
----------------------------------------------------------------------
Ran 30 tests in 1.874s

OK

============================================================
📊 TEST EXECUTION SUMMARY
============================================================
Total Tests Run:    30
✅ Passed:          30
❌ Failed:          0
💥 Errors:          0
⏭️  Skipped:         0
📈 Success Rate:    100.0%

🎯 Overall Result: ✅ ALL TESTS PASSED!
============================================================
```

## 🛠️ Local Testing

You can run the same tests locally:

```bash
# Run all tests
python run_all_tests.py --verbose

# Run with coverage
python run_all_tests.py --coverage --verbose

# Run specific services
python run_all_tests.py --services account,auth,submission --verbose
```

## 📊 Coverage Reports

Coverage reports are generated and available:
- In GitHub Actions logs
- As HTML reports (artifacts)
- On Codecov (if configured)

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**
   - Check that all test classes exist
   - Verify imports in `run_all_tests.py`

2. **Dependency Issues**
   - Ensure `requirements.txt` is up to date
   - Check for missing packages

3. **Test Failures**
   - Review test output in GitHub Actions logs
   - Run tests locally to debug

### Debugging Steps

1. Go to your repository's "Actions" tab
2. Click on the failed workflow run
3. Review the logs for specific errors
4. Test locally using the same commands

## ⚙️ Customization

### Adding More Services
Edit `run_all_tests.py` to include new test classes:

```python
# Add new service
if 'newservice' in self.services:
    test_classes['NewService'] = {
        'unit': TestNewService
    }
```

### Modifying Workflows
You can customize workflows by:
- Adding more Python versions
- Including additional test scenarios
- Adding code quality checks
- Configuring different triggers

### Example: Adding Python 3.12
```yaml
strategy:
  matrix:
    python-version: [3.11, 3.12]
```

## 📋 Requirements

- Python 3.11+
- All dependencies from `requirements.txt`
- Django project properly configured
- Test files in expected locations

## 🎯 Best Practices

1. **Use `run-tests.yml`** for most cases
2. **Test locally** before pushing
3. **Check the Actions tab** for results
4. **Review coverage reports** regularly
5. **Keep dependencies updated**

## 📞 Support

If you encounter issues:
1. Check the GitHub Actions logs
2. Test locally with the same commands
3. Review this documentation
4. Check the `run_all_tests.py` script

---

**Happy Testing! 🧪✨**
