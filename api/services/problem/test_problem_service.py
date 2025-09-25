import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.services.problem.problem_service import ProblemService
from api.repositories.problem_repository import ProblemRepository
from api.repositories.account_repository import AccountRepository
from api.repositories.permission_repository import PermissionRepository
from api.repositories.group_repository import GroupRepository
from api.repositories.topic_repository import TopicRepository
from api.models import Account, Problem, Testcase
from api.errors.common import *


class TestProblemService(TestCase):
    """Unit tests for ProblemService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_problem_repo = Mock(spec=ProblemRepository)
        self.mock_account_repo = Mock(spec=AccountRepository)
        self.mock_permission_repo = Mock(spec=PermissionRepository)
        self.mock_group_repo = Mock(spec=GroupRepository)
        self.mock_topic_repo = Mock(spec=TopicRepository)
        
        self.problem_service = ProblemService(
            problem_repo=self.mock_problem_repo,
            account_repo=self.mock_account_repo,
            permission_repo=self.mock_permission_repo,
            group_repo=self.mock_group_repo,
            topic_repo=self.mock_topic_repo
        )
        
        # Sample account data
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        self.sample_account.email = 'test@example.com'
        
        # Sample problem data
        self.sample_problem_data = {
            'language': 'python',
            'title': 'Test Problem',
            'description': 'A test problem',
            'solution': 'print("Hello World")',
            'time_limit': 1.0,
            'allowed_languages': ['python'],
            'testcases': [
                {'input': 'test1', 'output': 'Hello World'},
                {'input': 'test2', 'output': 'Hello World'}
            ]
        }
        
        # Sample problem object
        self.sample_problem = Mock(spec=Problem)
        self.sample_problem.problem_id = 'prob_123'
        self.sample_problem.title = 'Test Problem'
        self.sample_problem.description = 'A test problem'
        self.sample_problem.language = 'python'
        self.sample_problem.creator = self.sample_account
        
        # Sample testcase object
        self.sample_testcase = Mock(spec=Testcase)
        self.sample_testcase.testcase_id = 'test_123'
        self.sample_testcase.input = 'test1'
        self.sample_testcase.output = 'Hello World'
        self.sample_testcase.runtime_status = 'success'

    @patch('api.services.problem.problem_service.PythonGrader')
    @patch('api.services.problem.problem_service.ProblemSerializer')
    @patch('api.services.problem.problem_service.TestcaseSerializer')
    def test_create_problem_success(self, mock_testcase_serializer_class, mock_problem_serializer_class, mock_grader_class):
        """Test successful problem creation"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_problem_data.copy()
        
        # Mock account repository
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Mock grader
        mock_grader_instance = Mock()
        mock_runtime_result = Mock()
        mock_runtime_result.data = [
            Mock(input='test1', output='Hello World', runtime_status='success'),
            Mock(input='test2', output='Hello World', runtime_status='success')
        ]
        mock_grader_instance.generate_output.return_value = mock_runtime_result
        mock_grader_class.return_value = mock_grader_instance
        
        # Mock problem repository
        self.mock_problem_repo.create.return_value = self.sample_problem
        self.mock_problem_repo.bulk_create_testcases.return_value = [self.sample_testcase]
        
        # Mock serializers
        mock_problem_serializer_instance = Mock()
        mock_problem_serializer_instance.data = {
            'problem_id': 'prob_123',
            'title': 'Test Problem',
            'description': 'A test problem'
        }
        mock_problem_serializer_class.return_value = mock_problem_serializer_instance
        
        mock_testcase_serializer_instance = Mock()
        mock_testcase_serializer_instance.data = [
            {'testcase_id': 'test_123', 'input': 'test1', 'output': 'Hello World'}
        ]
        mock_testcase_serializer_class.return_value = mock_testcase_serializer_instance
        
        # Act
        result = self.problem_service.create_problem(account_id, mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        mock_grader_class.assert_called_once_with(
            self.sample_problem_data['solution'],
            self.sample_problem_data['testcases'],
            1,
            1.5
        )
        self.mock_problem_repo.create.assert_called_once()
        self.mock_problem_repo.bulk_create_testcases.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('problem_id', result)
        self.assertIn('testcases', result)

    def test_delete_problem_success(self):
        """Test successful problem deletion"""
        # Arrange
        problem_id = 'prob_123'
        
        # Act
        result = self.problem_service.delete_problem(problem_id)
        
        # Assert
        self.mock_problem_repo.delete.assert_called_once_with(problem_id)
        self.assertIsNone(result)

    @patch('api.services.problem.problem_service.Grader')
    def test_validate_program_success(self, mock_grader_class):
        """Test successful program validation"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'language': 'python',
            'source_code': 'print("Hello")',
            'testcases': ['test1', 'test2'],
            'time_limited': 1.0
        }
        
        # Mock grader
        mock_grader_instance = Mock()
        mock_runtime_result = Mock()
        mock_runtime_result.runnable = True
        mock_runtime_result.has_error = False
        mock_runtime_result.has_timeout = False
        mock_runtime_result.getResult.return_value = ['result1', 'result2']
        mock_grader_instance.generate_output.return_value = mock_runtime_result
        mock_grader_class.__getitem__.return_value = mock_grader_instance
        
        # Act
        result = self.problem_service.validate_program(mock_request)
        
        # Assert
        mock_grader_class.__getitem__.assert_called_once_with('python')
        mock_grader_instance.assert_called_once_with(
            'print("Hello")',
            ['test1', 'test2'],
            1,
            1.0
        )
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('runnable', result)
        self.assertIn('has_error', result)
        self.assertIn('has_timeout', result)
        self.assertIn('runtime_results', result)
        self.assertTrue(result['runnable'])
        self.assertFalse(result['has_error'])
        self.assertFalse(result['has_timeout'])

    def test_import_elabsheet_problem_success(self):
        """Test successful elabsheet problem import"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.data = {'file': 'test_file.pdf'}
        
        # Act
        result = self.problem_service.import_elabsheet_problem(mock_request, problem_id)
        
        # Assert
        self.mock_problem_repo.update.assert_called_once_with(problem_id, {'pdf_url': 'test_file.pdf'})
        self.assertIsNone(result)

    @patch('api.services.problem.problem_service.ProblemPopulatePartialTestcaseSerializer')
    def test_get_all_problems_by_account_success(self, mock_serializer_class):
        """Test successful retrieval of all problems by account"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {
            'start': '0',
            'end': '10',
            'query': 'test'
        }
        
        # Mock repositories
        personal_problems = [self.sample_problem]
        manageable_problems = [self.sample_problem]
        self.mock_problem_repo.get_personal.return_value = personal_problems
        self.mock_problem_repo.get_manageable_by_account.return_value = manageable_problems
        self.mock_problem_repo.get_testcases.return_value = [self.sample_testcase]
        self.mock_group_repo.get_ids_by_account.return_value = ['group_123']
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [
            {'problem_id': 'prob_123', 'title': 'Test Problem'}
        ]
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        result = self.problem_service.get_all_problems_by_account(account_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get_personal.assert_called_once_with(account_id, 'test', 0, 10)
        self.mock_group_repo.get_ids_by_account.assert_called_once_with(account_id)
        self.mock_problem_repo.get_manageable_by_account.assert_called_once_with(['group_123'], 'test', 0, 10)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('problems', result)
        self.assertIn('manageable_problems', result)
        self.assertIn('max_personal', result)
        self.assertIn('max_manageable', result)

    @patch('api.services.problem.problem_service.ProblemPopulatePartialTestcaseSerializer')
    def test_get_all_problems_by_account_with_default_params(self, mock_serializer_class):
        """Test retrieval with default parameters"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {}  # No query params
        
        # Mock repositories
        personal_problems = [self.sample_problem]
        manageable_problems = [self.sample_problem]
        self.mock_problem_repo.get_personal.return_value = personal_problems
        self.mock_problem_repo.get_manageable_by_account.return_value = manageable_problems
        self.mock_problem_repo.get_testcases.return_value = [self.sample_testcase]
        self.mock_group_repo.get_ids_by_account.return_value = ['group_123']
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [
            {'problem_id': 'prob_123', 'title': 'Test Problem'}
        ]
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        result = self.problem_service.get_all_problems_by_account(account_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get_personal.assert_called_once_with(account_id, '', 0, None)
        self.mock_problem_repo.get_manageable_by_account.assert_called_once_with(['group_123'], '', 0, None)

    @patch('api.services.problem.problem_service.ProblemPopulatePartialTestcaseSerializer')
    def test_get_all_problems_by_account_empty_results(self, mock_serializer_class):
        """Test retrieval when no problems are found"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {}
        
        # Mock repositories to return empty lists
        self.mock_problem_repo.get_personal.return_value = []
        self.mock_problem_repo.get_manageable_by_account.return_value = []
        self.mock_group_repo.get_ids_by_account.return_value = ['group_123']
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = []
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        result = self.problem_service.get_all_problems_by_account(account_id, mock_request)
        
        # Assert
        self.assertEqual(result['max_personal'], 0)
        self.assertEqual(result['max_manageable'], 0)
        self.assertEqual(len(result['problems']), 0)
        self.assertEqual(len(result['manageable_problems']), 0)

    def test_get_all_problems_by_account_repository_exception(self):
        """Test handling of repository exceptions"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {}
        
        # Mock repository to raise exception
        self.mock_problem_repo.get_personal.side_effect = Exception("Database error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.problem_service.get_all_problems_by_account(account_id, mock_request)

    def test_service_initialization(self):
        """Test that service initializes correctly with repositories"""
        # Arrange & Act
        service = ProblemService(
            problem_repo=self.mock_problem_repo,
            account_repo=self.mock_account_repo,
            permission_repo=self.mock_permission_repo,
            group_repo=self.mock_group_repo,
            topic_repo=self.mock_topic_repo
        )
        
        # Assert
        self.assertEqual(service.problem_repo, self.mock_problem_repo)
        self.assertEqual(service.account_repo, self.mock_account_repo)
        self.assertEqual(service.permission_repo, self.mock_permission_repo)
        self.assertEqual(service.group_repo, self.mock_group_repo)
        self.assertEqual(service.topic_repo, self.mock_topic_repo)

    @patch('api.services.problem.problem_service.PythonGrader')
    def test_create_problem_grader_exception(self, mock_grader_class):
        """Test problem creation when grader raises exception"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_problem_data.copy()
        
        # Mock account repository
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Mock grader to raise exception
        mock_grader_class.side_effect = Exception("Grader error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.problem_service.create_problem(account_id, mock_request)

    @patch('api.services.problem.problem_service.PythonGrader')
    def test_create_problem_account_not_found(self, mock_grader_class):
        """Test problem creation when account is not found"""
        # Arrange
        account_id = 'nonexistent'
        mock_request = Mock()
        mock_request.data = self.sample_problem_data.copy()
        
        # Mock account repository to raise exception
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Account.DoesNotExist):
            self.problem_service.create_problem(account_id, mock_request)

    def test_validate_program_invalid_language(self):
        """Test program validation with invalid language"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'language': 'invalid_lang',
            'source_code': 'print("Hello")',
            'testcases': ['test1'],
            'time_limited': 1.0
        }
        
        # Act & Assert
        with self.assertRaises(KeyError):
            self.problem_service.validate_program(mock_request)

    def test_import_elabsheet_problem_no_file(self):
        """Test elabsheet import when no file is provided"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.data = {}  # No file
        
        # Act
        result = self.problem_service.import_elabsheet_problem(mock_request, problem_id)
        
        # Assert
        self.mock_problem_repo.update.assert_called_once_with(problem_id, {'pdf_url': None})
        self.assertIsNone(result)


class TestProblemServiceIntegration(unittest.TestCase):
    """Integration tests for ProblemService with real repositories"""

    def setUp(self):
        """Set up integration test fixtures"""
        from api.repositories.problem_repository import ProblemRepositoryImpl
        from api.repositories.account_repository import AccountRepositoryImpl
        from api.repositories.permission_repository import PermissionRepositoryImpl
        from api.repositories.group_repository import GroupRepositoryImpl
        from api.repositories.topic_repository import TopicRepositoryImpl
        
        self.real_problem_repo = ProblemRepositoryImpl()
        self.real_account_repo = AccountRepositoryImpl()
        self.real_permission_repo = PermissionRepositoryImpl()
        self.real_group_repo = GroupRepositoryImpl()
        self.real_topic_repo = TopicRepositoryImpl()
        
        self.problem_service = ProblemService(
            problem_repo=self.real_problem_repo,
            account_repo=self.real_account_repo,
            permission_repo=self.real_permission_repo,
            group_repo=self.real_group_repo,
            topic_repo=self.real_topic_repo
        )

    def test_integration_create_problem(self):
        """Integration test for problem creation"""
        # This test would require a real database connection
        # For now, we'll skip it in unit tests
        self.skipTest("Integration test requires database setup")

    def test_integration_get_problems(self):
        """Integration test for getting problems"""
        # This test would require a real database connection
        # For now, we'll skip it in unit tests
        self.skipTest("Integration test requires database setup")


if __name__ == '__main__':
    unittest.main()
