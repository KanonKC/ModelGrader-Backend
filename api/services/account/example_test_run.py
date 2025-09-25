#!/usr/bin/env python
"""
Example of running specific AccountService tests
This demonstrates how to run individual test methods
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

import unittest
from api.services.account.test_account_service import TestAccountService

def run_specific_tests():
    """Run specific test methods"""
    
    # Create test suite for specific tests
    suite = unittest.TestSuite()
    
    # Add specific test methods
    suite.addTest(TestAccountService('test_create_account_success'))
    suite.addTest(TestAccountService('test_get_account_success'))
    suite.addTest(TestAccountService('test_get_all_accounts_without_search'))
    
    # Run the specific tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print(f"\nTests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return 0 if result.wasSuccessful() else 1

def run_test_class():
    """Run all tests in a specific test class"""
    
    # Create test suite for entire class
    suite = unittest.TestLoader().loadTestsFromTestCase(TestAccountService)
    
    # Run all tests in the class
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    print("Running specific AccountService tests...")
    exit_code = run_specific_tests()
    
    print("\n" + "="*50)
    print("Running all AccountService tests...")
    exit_code = run_test_class()
    
    sys.exit(exit_code)
