#!/usr/bin/env python
"""
Test runner for AuthService unit tests
Usage: python run_auth_service_tests.py
"""

import os
import sys
import django
from django.conf import settings

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

import unittest
from api.services.auth.test_auth_service import TestAuthService, TestAuthServiceIntegration, TestAuthServiceModuleFunctions

def run_tests():
    """Run all AuthService tests"""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAuthService))
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAuthServiceModuleFunctions))
    
    # Add integration tests (optional - requires database)
    # suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestAuthServiceIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    exit_code = run_tests()
    sys.exit(exit_code)
