# GitHub Workflows

This directory contains GitHub Actions workflows for the ModelGrader-Backend project.

## Available Workflows

### 1. `run-tests.yml` (Recommended)
**Purpose**: Simple and focused test runner for pull requests
**Triggers**: Pull requests and pushes to `main` and `dev` branches
**Features**:
- Runs all tests using `run_all_tests.py`
- Tests individual services
- Includes coverage analysis
- Fast execution

### 2. `test.yml`
**Purpose**: Basic test runner with coverage
**Triggers**: Pull requests and pushes to `main` and `dev` branches
**Features**:
- Runs tests with verbose output
- Includes coverage analysis
- Uploads coverage reports to Codecov

### 3. `ci.yml`
**Purpose**: Comprehensive CI/CD pipeline
**Triggers**: Pull requests and pushes to `main` and `dev` branches
**Features**:
- Multiple test scenarios (all, unit-only, integration-only)
- Code quality checks (flake8, black, isort)
- Matrix testing with different Python versions
- Artifact uploads

## Usage

### For Pull Requests
When you create a pull request to `main` or `dev` branches, the workflows will automatically:
1. Check out your code
2. Set up Python 3.11
3. Install dependencies from `requirements.txt`
4. Run all tests using `run_all_tests.py`
5. Generate coverage reports
6. Report pass/fail status

### Manual Testing
You can also run the same tests locally:

```bash
# Run all tests
python run_all_tests.py --verbose

# Run with coverage
python run_all_tests.py --coverage --verbose

# Run specific services
python run_all_tests.py --services account,auth,submission --verbose
```

## Workflow Status

The workflows will show:
- ✅ **Green checkmark**: All tests passed
- ❌ **Red X**: Some tests failed
- ⚠️ **Yellow circle**: Tests are running

## Coverage Reports

Coverage reports are generated and can be viewed:
- In the GitHub Actions logs
- As HTML reports (uploaded as artifacts)
- On Codecov (if configured)

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all test classes exist and are properly imported
2. **Dependency Issues**: Check that `requirements.txt` includes all necessary packages
3. **Test Failures**: Review the test output in the GitHub Actions logs

### Debugging

To debug workflow issues:
1. Check the "Actions" tab in your GitHub repository
2. Click on the failed workflow run
3. Review the logs for specific error messages
4. Test locally using the same commands

## Customization

You can modify the workflows to:
- Add more Python versions to test against
- Include additional test scenarios
- Add more code quality checks
- Configure different triggers

## Requirements

- Python 3.11
- All dependencies from `requirements.txt`
- Django project properly configured
- Test files in the expected locations
