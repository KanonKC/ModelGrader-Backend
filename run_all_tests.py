#!/usr/bin/env python
"""
Comprehensive test runner for all ModelGrader-Backend service unit tests
Usage: python run_all_tests.py [options]

This script runs unit tests for:
- AccountService
- ProblemService  
- AuthService
- CollectionService
- GroupService
- SubmissionService
- TopicService

Options:
  --verbose, -v    : Run with verbose output
  --coverage, -c   : Run with coverage analysis
  --services, -s   : Run specific services (comma-separated)
  --help, -h       : Show this help message

Examples:
  python run_all_tests.py
  python run_all_tests.py --verbose
  python run_all_tests.py --coverage
  python run_all_tests.py --services account,auth,collection
  python run_all_tests.py -v -c
"""

import os
import sys
import argparse
import django
from django.conf import settings
import unittest
from io import StringIO

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Backend.settings')
django.setup()

# Import test classes
from api.services.account.test_account_service import TestAccountService, TestAccountServiceIntegration
from api.services.problem.test_problem_service import TestProblemService, TestProblemServiceIntegration
from api.services.auth.test_auth_service import TestAuthService, TestAuthServiceIntegration, TestAuthServiceModuleFunctions
from api.services.collection.test_collection_service import TestCollectionService
from api.services.group.test_group_service import TestGroupService
from api.services.submission.test_submission_service import TestSubmissionService
from api.services.topic.test_topic_service import TestTopicService


class TestRunner:
    """Main test runner class for all service tests"""

    def __init__(self, verbose=False, coverage=False, services=None):
        self.verbose = verbose
        self.coverage = coverage
        self.services = services or ['account', 'problem', 'auth', 'collection', 'group', 'submission', 'topic']
        self.results = {}
        self.total_tests = 0
        self.total_failures = 0
        self.total_errors = 0
        self.total_skipped = 0
        
    def get_test_classes(self):
        """Get test classes based on selected services"""
        test_classes = {}
        
        if 'account' in self.services:
            test_classes['AccountService'] = {
                'unit': TestAccountService,
                'integration': TestAccountServiceIntegration
            }
        
        if 'problem' in self.services:
            test_classes['ProblemService'] = {
                'unit': TestProblemService,
                'integration': TestProblemServiceIntegration
            }
        
        if 'auth' in self.services:
            test_classes['AuthService'] = {
                'unit': TestAuthService,
                'integration': TestAuthServiceIntegration,
                'module_functions': TestAuthServiceModuleFunctions
            }
        
        if 'collection' in self.services:
            test_classes['CollectionService'] = {
                'unit': TestCollectionService
            }
        
        if 'group' in self.services:
            test_classes['GroupService'] = {
                'unit': TestGroupService
            }
        
        if 'submission' in self.services:
            test_classes['SubmissionService'] = {
                'unit': TestSubmissionService
            }
        
        if 'topic' in self.services:
            test_classes['TopicService'] = {
                'unit': TestTopicService
            }
        
        return test_classes
    
    def run_coverage_analysis(self):
        """Run tests with coverage analysis"""
        try:
            import coverage
            print("🔍 Running tests with coverage analysis...")
            
            # Start coverage
            cov = coverage.Coverage(source=['api.services'])
            cov.start()
            
            # Run tests
            self.run_tests()
            
            # Stop coverage and generate report
            cov.stop()
            cov.save()
            
            print("\n📊 Coverage Report:")
            print("=" * 50)
            cov.report()
            
            # Generate HTML report
            print("\n📁 Generating HTML coverage report...")
            cov.html_report(directory='htmlcov')
            print("HTML report generated in 'htmlcov' directory")
            
            return True
            
        except ImportError:
            print("❌ Coverage package not installed. Install with: pip install coverage")
            return False
    
    def run_tests(self):
        """Run all selected tests"""
        test_classes = self.get_test_classes()
        
        print("🚀 Starting ModelGrader-Backend Service Tests")
        print("=" * 60)
        
        if self.verbose:
            print(f"📋 Services to test: {', '.join(self.services)}")
            print(f"🔧 Verbose mode: {'ON' if self.verbose else 'OFF'}")
            print(f"📊 Coverage mode: {'ON' if self.coverage else 'OFF'}")
            print()
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add unit tests
        for service_name, classes in test_classes.items():
            print(f"📦 Adding {service_name} tests...")
            
            # Add unit tests
            if 'unit' in classes:
                suite.addTest(unittest.TestLoader().loadTestsFromTestCase(classes['unit']))
                print(f"  ✅ Unit tests added")
            
            # Add module function tests (AuthService only)
            if 'module_functions' in classes:
                suite.addTest(unittest.TestLoader().loadTestsFromTestCase(classes['module_functions']))
                print(f"  ✅ Module function tests added")
            
            # Skip integration tests for now (require database)
            if 'integration' in classes:
                print(f"  ⏭️  Integration tests skipped (require database setup)")
        
        print()
        
        # Configure test runner
        verbosity = 2 if self.verbose else 1
        runner = unittest.TextTestRunner(
            verbosity=verbosity,
            stream=sys.stdout,
            descriptions=True,
            failfast=False
        )
        
        # Run tests
        print("🏃 Running tests...")
        print("-" * 60)
        
        result = runner.run(suite)
        
        # Store results
        self.total_tests = result.testsRun
        self.total_failures = len(result.failures)
        self.total_errors = len(result.errors)
        self.total_skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
        
        # Print summary
        self.print_summary(result)
        
        return result.wasSuccessful()
    
    def print_summary(self, result):
        """Print test execution summary"""
        print("\n" + "=" * 60)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        # Test counts
        print(f"Total Tests Run:    {self.total_tests}")
        print(f"✅ Passed:          {self.total_tests - self.total_failures - self.total_errors}")
        print(f"❌ Failed:          {self.total_failures}")
        print(f"💥 Errors:          {self.total_errors}")
        print(f"⏭️  Skipped:         {self.total_skipped}")
        
        # Success rate
        if self.total_tests > 0:
            success_rate = ((self.total_tests - self.total_failures - self.total_errors) / self.total_tests) * 100
            print(f"📈 Success Rate:    {success_rate:.1f}%")
        
        # Overall result
        print("\n🎯 Overall Result: ", end="")
        if result.wasSuccessful():
            print("✅ ALL TESTS PASSED!")
        else:
            print("❌ SOME TESTS FAILED!")
        
        # Detailed failure/error info
        if result.failures:
            print(f"\n❌ FAILURES ({len(result.failures)}):")
            for test, traceback in result.failures:
                print(f"  • {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0] if 'AssertionError:' in traceback else 'Assertion failed'}")
        
        if result.errors:
            print(f"\n💥 ERRORS ({len(result.errors)}):")
            for test, traceback in result.errors:
                print(f"  • {test}: {traceback.split('\\n')[-2] if traceback.split('\\n') else 'Unknown error'}")
        
        print("=" * 60)
    
    def run(self):
        """Main entry point"""
        if self.coverage:
            return self.run_coverage_analysis()
        else:
            return self.run_tests()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Run all ModelGrader-Backend service unit tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_all_tests.py                    # Run all tests
  python run_all_tests.py --verbose          # Run with verbose output
  python run_all_tests.py --coverage         # Run with coverage analysis
  python run_all_tests.py --services account,auth,collection,group  # Run specific services
  python run_all_tests.py -v -c              # Verbose with coverage
        """
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Run with verbose output'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run with coverage analysis'
    )
    
    parser.add_argument(
        '--services', '-s',
        type=str,
        help='Comma-separated list of services to test (account,problem,auth,collection,group,submission,topic)'
    )
    
    return parser.parse_args()


def main():
    """Main function"""
    args = parse_arguments()
    
    # Parse services
    services = None
    if args.services:
        services = [s.strip().lower() for s in args.services.split(',')]
        valid_services = ['account', 'problem', 'auth', 'collection', 'group', 'submission', 'topic']
        invalid_services = [s for s in services if s not in valid_services]
        if invalid_services:
            print(f"❌ Invalid services: {', '.join(invalid_services)}")
            print(f"Valid services: {', '.join(valid_services)}")
            sys.exit(1)
    
    # Create and run test runner
    runner = TestRunner(
        verbose=args.verbose,
        coverage=args.coverage,
        services=services
    )
    
    try:
        success = runner.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
