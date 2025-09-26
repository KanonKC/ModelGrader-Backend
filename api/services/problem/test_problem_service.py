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
from api.models import Account, Problem, Testcase, ProblemGroupPermission
from api.errors.common import BadRequestError, InternalServerError, ItemNotFoundError


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
        
        # Sample data
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        
        self.sample_problem = Mock(spec=Problem)
        self.sample_problem.problem_id = 'prob_123'
        self.sample_problem.title = 'Test Problem'
        self.sample_problem.description = 'Test Description'
        self.sample_problem.solution = 'print("Hello")'
        self.sample_problem.language = 'python'
        self.sample_problem.time_limit = 1.5
        self.sample_problem.allowed_languages = ['python']
        self.sample_problem.is_private = False
        self.sample_problem.is_active = True
        self.sample_problem.creator = self.sample_account
        
        self.sample_testcase = Mock(spec=Testcase)
        self.sample_testcase.testcase_id = 'tc_123'
        self.sample_testcase.input = 'input'
        self.sample_testcase.output = 'output'
        self.sample_testcase.runtime_status = 'AC'
        
        self.sample_request_data = {
            'title': 'Test Problem',
            'description': 'Test Description',
            'solution': 'print("Hello")',
            'language': 'python',
            'time_limit': 1.5,
            'allowed_languages': ['python'],
            'testcases': [{'input': 'input', 'output': 'output'}]
        }

    @patch('api.services.problem.problem_service.PythonGrader')
    @patch('api.services.problem.problem_service.ProblemSerializer')
    @patch('api.services.problem.problem_service.TestcaseSerializer')
    def test_create_problem_success(self, mock_testcase_serializer, mock_problem_serializer, mock_python_grader):
        """Test successful problem creation"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        self.mock_account_repo.get.return_value = self.sample_account
        self.mock_problem_repo.create.return_value = self.sample_problem
        
        # Mock grader result
        mock_grader_instance = Mock()
        mock_grader_result = Mock()
        mock_grader_result.data = [Mock(input='input', output='output', runtime_status='AC')]
        mock_grader_instance.generate_output.return_value = mock_grader_result
        mock_python_grader.return_value = mock_grader_instance
        
        # Mock serializers
        mock_problem_serializer_instance = Mock()
        mock_problem_serializer_instance.data = {'problem_id': 'prob_123', 'title': 'Test Problem'}
        mock_problem_serializer.return_value = mock_problem_serializer_instance
        
        mock_testcase_serializer_instance = Mock()
        mock_testcase_serializer_instance.data = [{'testcase_id': 'tc_123', 'input': 'input'}]
        mock_testcase_serializer.return_value = mock_testcase_serializer_instance
        
        # Act
        result = self.problem_service.create_problem(account_id, mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        self.mock_problem_repo.create.assert_called_once()
        self.mock_problem_repo.bulk_create_testcases.assert_called_once()
        
        # Verify grader was called with correct parameters
        mock_python_grader.assert_called_once_with(
            self.sample_request_data['solution'],
            self.sample_request_data['testcases'],
            1,
            1.5
        )
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('problem_id', result)
        self.assertIn('testcases', result)

    def test_create_problem_account_not_found(self):
        """Test problem creation when account doesn't exist"""
        # Arrange
        account_id = 'nonexistent'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Account.DoesNotExist):
            self.problem_service.create_problem(account_id, mock_request)
        
        self.mock_account_repo.get.assert_called_once_with(account_id)

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
    def test_validate_program_success(self, mock_grader):
        """Test successful program validation"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'language': 'python',
            'source_code': 'print("Hello")',
            'testcases': [{'input': 'input', 'output': 'output'}],
            'time_limited': 1.5
        }
        
        # Mock grader
        mock_grader_instance = Mock()
        mock_grader_result = Mock()
        mock_grader_result.runnable = True
        mock_grader_result.has_error = False
        mock_grader_result.has_timeout = False
        mock_grader_result.getResult.return_value = [{'input': 'input', 'output': 'output', 'is_passed': True}]
        mock_grader_instance.generate_output.return_value = mock_grader_result
        mock_grader.__getitem__.return_value = mock_grader_instance
        
        # Act
        result = self.problem_service.validate_program(mock_request)
        
        # Assert
        mock_grader.__getitem__.assert_called_once_with('python')
        mock_grader_instance.assert_called_once_with(
            'print("Hello")',
            [{'input': 'input', 'output': 'output'}],
            1,
            1.5
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

    def test_get_all_problems_by_account_success(self):
        """Test getting all problems by account"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {
            'start': '0',
            'end': '10',
            'query': 'test'
        }
        
        # Mock repository responses
        personal_problems = [self.sample_problem]
        manageable_problems = []
        group_ids = ['group_123']
        
        self.mock_problem_repo.get_personal.return_value = personal_problems
        self.mock_problem_repo.get_manageable_by_account.return_value = manageable_problems
        self.mock_group_repo.get_by_creator.return_value = group_ids
        self.mock_problem_repo.get_testcases.return_value = [self.sample_testcase]
        
        # Mock serializers
        with patch('api.services.problem.problem_service.ProblemPopulatePartialTestcaseSerializer') as mock_serializer:
        mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'problem_id': 'prob_123', 'title': 'Test Problem'}]
            mock_serializer.return_value = mock_serializer_instance
        
        # Act
        result = self.problem_service.get_all_problems_by_account(account_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get_personal.assert_called_once_with(account_id, 'test', 0, 10)
        self.mock_group_repo.get_by_creator.assert_called_once_with(account_id)
        self.mock_problem_repo.get_manageable_by_account.assert_called_once_with(group_ids, 'test', 0, 10)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('start', result)
        self.assertIn('end', result)
        self.assertIn('total_personal_problems', result)
        self.assertIn('total_manageable_problems', result)
        self.assertIn('problems', result)
        self.assertIn('manageable_problems', result)

    def test_get_all_problems_by_account_with_default_params(self):
        """Test getting all problems by account with default parameters"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {}  # No query parameters
        
        # Mock repository responses
        personal_problems = []
        manageable_problems = []
        group_ids = []
        
        self.mock_problem_repo.get_personal.return_value = personal_problems
        self.mock_problem_repo.get_manageable_by_account.return_value = manageable_problems
        self.mock_group_repo.get_by_creator.return_value = group_ids
        
        # Mock serializers
        with patch('api.services.problem.problem_service.ProblemPopulatePartialTestcaseSerializer') as mock_serializer:
        mock_serializer_instance = Mock()
            mock_serializer_instance.data = []
            mock_serializer.return_value = mock_serializer_instance
        
        # Act
        result = self.problem_service.get_all_problems_by_account(account_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get_personal.assert_called_once_with(account_id, '', 0, None)
        self.mock_problem_repo.get_manageable_by_account.assert_called_once_with([], '', 0, None)

    def test_get_all_problem_with_best_submission_success(self):
        """Test getting all problems with best submission"""
        # Arrange
        account_id = 'acc_123'
        
        # Mock repository responses
        problems = [self.sample_problem]
        best_submission = Mock()
        best_submission.submission_id = 'sub_123'
        testcases = [self.sample_testcase]
        
        self.mock_problem_repo.get_with_best_submission.return_value = problems
        self.mock_problem_repo.get_best_submission.return_value = best_submission
        self.mock_problem_repo.get_submission_testcases.return_value = testcases
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'problem_id': 'prob_123', 'best_submission': {'submission_id': 'sub_123'}}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.get_all_problem_with_best_submission(account_id)
        
        # Assert
        self.mock_problem_repo.get_with_best_submission.assert_called_once_with(account_id)
        self.mock_problem_repo.get_best_submission.assert_called_once_with('prob_123', account_id)
        self.mock_problem_repo.get_submission_testcases.assert_called_once_with('sub_123')
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('problems', result)

    def test_get_all_problem_with_best_submission_no_best_submission(self):
        """Test getting all problems when no best submission exists"""
        # Arrange
        account_id = 'acc_123'
        
        # Mock repository responses
        problems = [self.sample_problem]
        
        self.mock_problem_repo.get_with_best_submission.return_value = problems
        self.mock_problem_repo.get_best_submission.return_value = None
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'problem_id': 'prob_123', 'best_submission': None}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.get_all_problem_with_best_submission(account_id)
        
        # Assert
        self.mock_problem_repo.get_best_submission.assert_called_once_with('prob_123', account_id)
        self.mock_problem_repo.get_submission_testcases.assert_not_called()

    def test_get_all_problems_success(self):
        """Test getting all problems with filters"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {
            'private': '0',
            'deactive': '0',
            'account_id': 'acc_123'
        }
        
        # Mock repository response
        problems = [self.sample_problem]
        self.mock_problem_repo.list.return_value = problems
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemPopulateAccountSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'problem_id': 'prob_123', 'title': 'Test Problem'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.get_all_problems(mock_request)
        
        # Assert
        expected_filters = {
            'is_private': False,
            'is_active': True,
            'creator_id': 'acc_123'
        }
        self.mock_problem_repo.list.assert_called_once_with(filters=expected_filters, order_by=['-problem_id'])
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('problems', result)

    def test_get_all_problems_with_default_filters(self):
        """Test getting all problems with default filters"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {}  # No query parameters
        
        # Mock repository response
        problems = [self.sample_problem]
        self.mock_problem_repo.list.return_value = problems
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemPopulateAccountSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'problem_id': 'prob_123', 'title': 'Test Problem'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.get_all_problems(mock_request)
        
        # Assert
        expected_filters = {
            'is_private': False,
            'is_active': True
        }
        self.mock_problem_repo.list.assert_called_once_with(filters=expected_filters, order_by=['-problem_id'])

    def test_get_problem_success(self):
        """Test getting a specific problem"""
        # Arrange
        problem_id = 'prob_123'
        
        # Mock repository responses
        testcases = [self.sample_testcase]
        permissions = [Mock(spec=ProblemGroupPermission)]
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_problem_repo.get_testcases.return_value = testcases
        self.mock_permission_repo.get_problem_permissions.return_value = permissions
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'problem_id': 'prob_123', 'title': 'Test Problem'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.get_problem(problem_id)
        
        # Assert
        self.mock_problem_repo.get.assert_called_once_with(problem_id)
        self.mock_problem_repo.get_testcases.assert_called_once_with(problem_id, deprecated=False)
        self.mock_permission_repo.get_problem_permissions.assert_called_once_with(problem_id)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('problem_id', result)

    def test_get_problem_public_success(self):
        """Test getting a public problem"""
        # Arrange
        problem_id = 'prob_123'
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemPopulateAccountSecureSerializer') as mock_serializer:
        mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'problem_id': 'prob_123', 'title': 'Test Problem'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.get_problem_public(problem_id)
        
        # Assert
        self.mock_problem_repo.get.assert_called_once_with(problem_id)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('problem_id', result)

    def test_remove_bulk_problems_success(self):
        """Test removing multiple problems"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'problem': ['prob_123', 'prob_456']
        }
        
        # Act
        result = self.problem_service.remove_bulk_problems(mock_request)
        
        # Assert
        self.mock_problem_repo.delete_many.assert_called_once_with(['prob_123', 'prob_456'])
        self.assertIsNone(result)

    def test_update_problem_success(self):
        """Test updating a problem"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'is_private': True
        }
        
        updated_problem = Mock(spec=Problem)
        updated_problem.problem_id = problem_id
        updated_problem.title = 'Updated Title'
        
        self.mock_problem_repo.update.return_value = updated_problem
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'problem_id': 'prob_123', 'title': 'Updated Title'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.update_problem(problem_id, mock_request)
        
        # Assert
        expected_update_data = {
            'title': 'Updated Title',
            'description': 'Updated Description',
            'is_private': True
        }
        self.mock_problem_repo.update.assert_called_once_with(problem_id, expected_update_data)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('problem_id', result)

    def test_update_problem_with_none_values(self):
        """Test updating a problem with None values (should be filtered out)"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.data = {
            'title': 'Updated Title',
            'description': None,
            'is_private': None,
            'language': 'python'
        }
        
        updated_problem = Mock(spec=Problem)
        self.mock_problem_repo.update.return_value = updated_problem
        
        # Mock serializer
        with patch('api.services.problem.problem_service.ProblemSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'problem_id': 'prob_123', 'title': 'Updated Title'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.problem_service.update_problem(problem_id, mock_request)
        
        # Assert
        expected_update_data = {
            'title': 'Updated Title',
            'language': 'python'
        }
        self.mock_problem_repo.update.assert_called_once_with(problem_id, expected_update_data)

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


if __name__ == '__main__':
    unittest.main()