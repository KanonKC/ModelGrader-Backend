# ModelGrader Backend Project Rules

## Virtual Environment
- ALWAYS activate the virtual environment before running any Python scripts
- Use `source env/bin/activate` to activate the environment
- All Python commands should be run with the activated environment

## Python Scripts
- When running Django management commands, ensure the environment is activated first
- For testing: `source env/bin/activate && python manage.py test [test_path]`
- For running the server: `source env/bin/activate && python manage.py runserver`
- For migrations: `source env/bin/activate && python manage.py migrate`

## Test Execution
- Always activate environment before running tests
- Use the project's test runner: `source env/bin/activate && python run_all_tests.py`
- Individual test files: `source env/bin/activate && python manage.py test [test_path]`

## Project Structure
- This is a Django REST Framework project
- Main application is in the `api/` directory
- Services are in `api/services/`
- Tests are in `api/services/*/test_*.py`
- Configuration files: `manage.py`, `requirements.txt`, `Dockerfile`

## Dependencies
- Django REST Framework
- PostgreSQL (production)
- SQLite (development/testing)
- Various Python packages listed in `requirements.txt`
