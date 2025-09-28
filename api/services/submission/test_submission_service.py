import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.sandbox.grader import ProgramGrader
from api.services.submission.submission_service import SubmissionService
from api.repositories.submission_repository import SubmissionRepository
from api.repositories.problem_repository import ProblemRepository
from api.repositories.account_repository import AccountRepository
from api.repositories.topic_repository import TopicRepository
from api.services.problem.problem_service import ProblemService
from api.models import Submission, Problem, Account, Testcase, SubmissionTestcase
from api.errors.common import BadRequestError, InternalServerError, ItemNotFoundError


class TestSubmissionService(TestCase):
    """Unit tests for SubmissionService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_submission_repo = Mock(spec=SubmissionRepository)
        self.mock_problem_repo = Mock(spec=ProblemRepository)
        self.mock_account_repo = Mock(spec=AccountRepository)
        self.mock_topic_repo = Mock(spec=TopicRepository)
        self.mock_problem_service = Mock(spec=ProblemService)
        self.mock_grader = Mock()
        self.submission_service = SubmissionService(
            submission_repo=self.mock_submission_repo,
            problem_repo=self.mock_problem_repo,
            account_repo=self.mock_account_repo,
            topic_repo=self.mock_topic_repo,
            problem_service=self.mock_problem_service,
            grader=self.mock_grader
        )
        
        # Sample data
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        
        self.sample_problem = Mock(spec=Problem)
        self.sample_problem.problem_id = 'prob_123'
        self.sample_problem.title = 'Test Problem'
        self.sample_problem.submission_regex = r'.*'
        
        self.sample_testcase = Mock(spec=Testcase)
        self.sample_testcase.testcase_id = 'tc_123'
        self.sample_testcase.input = 'input'
        self.sample_testcase.output = 'output'
        
        self.sample_submission = Mock(spec=Submission)
        self.sample_submission.submission_id = 'sub_123'
        self.sample_submission.problem_id = 'prob_123'
        self.sample_submission.account_id = 'acc_123'
        self.sample_submission.language = 'python'
        self.sample_submission.submission_code = 'print("Hello")'
        self.sample_submission.is_passed = True
        self.sample_submission.score = 1
        self.sample_submission.max_score = 1
        self.sample_submission.passed_ratio = 1.0
        
        self.sample_submission_testcase = Mock(spec=SubmissionTestcase)
        self.sample_submission_testcase.submission_id = 'sub_123'
        self.sample_submission_testcase.testcase_id = 'tc_123'
        self.sample_submission_testcase.output = 'output'
        self.sample_submission_testcase.is_passed = True
        self.sample_submission_testcase.runtime_status = 'AC'
        
        self.sample_request_data = {
            'submission_code': 'print("Hello")',
            'language': 'python'
        }

    def test_get_all_submissions_by_creator_problem_success(self):
        """Test getting all submissions by creator problem"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.query_params = {
            'start': '0',
            'end': '10'
        }
        
        submissions = [self.sample_submission]
        testcases = [self.sample_testcase]
        submission_testcases = [self.sample_submission_testcase]
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_submission_repo.get_by_problem.return_value = submissions
        self.mock_submission_repo.get_testcases.return_value = submission_testcases
        self.mock_problem_repo.get_testcases.return_value = testcases
        
        # Mock serializers
        with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseAndAccountSerializer') as mock_submission_serializer, \
             patch('api.services.submission.submission_service.ProblemPopulateTestcaseSerializer') as mock_problem_serializer:
            
            mock_submission_serializer_instance = Mock()
            mock_submission_serializer_instance.data = [{'submission_id': 'sub_123'}]
            mock_submission_serializer.return_value = mock_submission_serializer_instance
            
            mock_problem_serializer_instance = Mock()
            mock_problem_serializer_instance.data = {'problem_id': 'prob_123'}
            mock_problem_serializer.return_value = mock_problem_serializer_instance
            
            # Act
            result = self.submission_service.get_all_submissions_by_creator_problem(problem_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get.assert_called_once_with(problem_id)
        self.mock_submission_repo.get_by_problem.assert_called_once_with(problem_id, 0, 10)
        self.mock_submission_repo.get_testcases.assert_called_once_with('sub_123')
        self.mock_problem_repo.get_testcases.assert_called_once_with(problem_id, deprecated=False)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('problem', result)
        self.assertIn('submissions', result)
        self.assertIn('start', result)
        self.assertIn('end', result)
        self.assertIn('total', result)

    def test_get_all_submissions_by_creator_problem_no_submissions(self):
        """Test getting all submissions when no submissions exist"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.query_params = {
            'start': '0',
            'end': '10'
        }
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_submission_repo.get_by_problem.return_value = []
        
        # Act
        result = self.submission_service.get_all_submissions_by_creator_problem(problem_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get.assert_called_once_with(problem_id)
        self.mock_submission_repo.get_by_problem.assert_called_once_with(problem_id, 0, 10)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('submissions', result)
        self.assertEqual(result['submissions'], [])

    def test_get_all_submissions_by_creator_problem_with_default_params(self):
        """Test getting all submissions with default parameters"""
        # Arrange
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.query_params = {}  # No query parameters
        
        submissions = [self.sample_submission]
        testcases = [self.sample_testcase]
        submission_testcases = [self.sample_submission_testcase]
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_submission_repo.get_by_problem.return_value = submissions
        self.mock_submission_repo.get_testcases.return_value = submission_testcases
        self.mock_problem_repo.get_testcases.return_value = testcases
        
        # Mock serializers
        with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseAndAccountSerializer') as mock_submission_serializer, \
             patch('api.services.submission.submission_service.ProblemPopulateTestcaseSerializer') as mock_problem_serializer:
            
            mock_submission_serializer_instance = Mock()
            mock_submission_serializer_instance.data = [{'submission_id': 'sub_123'}]
            mock_submission_serializer.return_value = mock_submission_serializer_instance
            
            mock_problem_serializer_instance = Mock()
            mock_problem_serializer_instance.data = {'problem_id': 'prob_123'}
            mock_problem_serializer.return_value = mock_problem_serializer_instance
            
            # Act
            result = self.submission_service.get_all_submissions_by_creator_problem(problem_id, mock_request)
        
        # Assert
        self.mock_submission_repo.get_by_problem.assert_called_once_with(problem_id, 0, None)

    def test_get_submission_by_queries_success(self):
        """Test getting submissions by queries"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {
            'problem_id': 'prob_123',
            'account_id': 'acc_123',
            'topic_id': 'topic_123',
            'passed': '1',
            'sort_score': '1',
            'sort_date': '0',
            'start': '0',
            'end': '10'
        }
        
        submissions = [self.sample_submission]
        submission_testcases = [self.sample_submission_testcase]
        
        self.mock_submission_repo.list.return_value = submissions
        self.mock_submission_repo.get_testcases.return_value = submission_testcases
        
        # Mock serializer
        with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'submission_id': 'sub_123'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.submission_service.get_submission_by_quries(mock_request)
        
        # Assert
        self.mock_submission_repo.list.assert_called_once_with(
            problem_id='prob_123',
            account_id='acc_123',
            topic_id='topic_123',
            passed=1,
            sort_score=1,
            sort_date=0,
            start=0,
            end=10
        )
        self.mock_submission_repo.get_testcases.assert_called_once_with('sub_123')
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('submissions', result)

    def test_get_submission_by_queries_with_empty_params(self):
        """Test getting submissions with empty query parameters"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {
            'problem_id': '',
            'account_id': '',
            'topic_id': '',
            'passed': '-1',
            'sort_score': '0',
            'sort_date': '0',
            'start': '-1',
            'end': '-1'
        }
        
        submissions = [self.sample_submission]
        submission_testcases = [self.sample_submission_testcase]
        
        self.mock_submission_repo.list.return_value = submissions
        self.mock_submission_repo.get_testcases.return_value = submission_testcases
        
        # Mock serializer
        with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseAndProblemSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'submission_id': 'sub_123'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.submission_service.get_submission_by_quries(mock_request)
        
        # Assert
        self.mock_submission_repo.list.assert_called_once_with(
            problem_id=None,
            account_id=None,
            topic_id=None,
            passed=None,
            sort_score=0,
            sort_date=0,
            start=None,
            end=None
        )

    def test_get_submissions_by_account_problem_in_topic_success(self):
        """Test getting submissions by account problem in topic"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        topic_id = 'topic_123'
        
        submissions = [self.sample_submission]
        submission_testcases = [self.sample_submission_testcase]
        best_submission = Mock()
        best_submission.submission_id = 'sub_123'
        best_submission.submission = self.sample_submission
        
        self.mock_submission_repo.get_by_account_problem_topic.return_value = submissions
        self.mock_submission_repo.get_testcases.return_value = submission_testcases
        self.mock_submission_repo.get_best_record.return_value = best_submission
        
        # Mock serializer
        with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'submission_id': 'sub_123'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.submission_service.get_submissions_by_account_problem_in_topic(account_id, problem_id, topic_id)
        
        # Assert
        self.mock_submission_repo.get_by_account_problem_topic.assert_called_once_with(account_id, problem_id, topic_id)
        self.mock_submission_repo.get_testcases.assert_any_call('sub_123')
        self.mock_submission_repo.get_best_record.assert_called_once_with(problem_id, account_id, topic_id)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('best_submission', result)
        self.assertIn('submissions', result)

    def test_get_submissions_by_account_problem_in_topic_no_submissions(self):
        """Test getting submissions when no submissions exist"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        topic_id = 'topic_123'
        
        self.mock_submission_repo.get_by_account_problem_topic.return_value = []
        
        # Act
        result = self.submission_service.get_submissions_by_account_problem_in_topic(account_id, problem_id, topic_id)
        
        # Assert
        self.mock_submission_repo.get_by_account_problem_topic.assert_called_once_with(account_id, problem_id, topic_id)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('best_submission', result)
        self.assertIn('submissions', result)
        self.assertIsNone(result['best_submission'])
        self.assertEqual(result['submissions'], [])

    def test_get_submissions_by_account_problem_success(self):
        """Test getting submissions by account problem"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        
        submissions = [self.sample_submission]
        submission_testcases = [self.sample_submission_testcase]
        
        self.mock_submission_repo.get_by_account_problem.return_value = submissions
        self.mock_submission_repo.get_testcases.return_value = submission_testcases
        
        # Mock serializer
        with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'submission_id': 'sub_123'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.submission_service.get_submissions_by_account_problem(account_id, problem_id)
        
        # Assert
        self.mock_submission_repo.get_by_account_problem.assert_called_once_with(account_id, problem_id)
        self.mock_submission_repo.get_testcases.assert_called_once_with('sub_123')
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('best_submission', result)
        self.assertIn('submissions', result)

    def test_get_submissions_by_account_problem_no_submissions(self):
        """Test getting submissions when no submissions exist"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        
        self.mock_submission_repo.get_by_account_problem.return_value = []
        
        # Act
        result = self.submission_service.get_submissions_by_account_problem(account_id, problem_id)
        
        # Assert
        self.mock_submission_repo.get_by_account_problem.assert_called_once_with(account_id, problem_id)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('best_submission', result)
        self.assertIn('submissions', result)
        self.assertIsNone(result['best_submission'])
        self.assertEqual(result['submissions'], [])

    def test_submit_problem_on_topic_success(self):
        """Test submitting problem on topic"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        testcases = [self.sample_testcase]
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_problem_repo.get_testcases.return_value = testcases
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Mock grading result
        mock_grading_result = Mock()
        mock_grading_result.is_passed = True
        mock_testcase_result = Mock()
        mock_testcase_result.is_passed = True
        mock_grading_result.data = [mock_testcase_result]
        
        # Mock grader
        with patch('api.services.submission.submission_service.regexMatching') as mock_regex, \
             patch('api.services.submission.submission_service.model_to_dict') as mock_model_to_dict:
            
            # Mock grader dictionary access
            mock_grader_class = Mock()
            mock_grader_instance = Mock()
            mock_grader_instance.grading.return_value = mock_grading_result
            mock_grader_class.return_value = mock_grader_instance
            self.mock_grader.__getitem__ = Mock(return_value=mock_grader_class)
            
            mock_regex.return_value = True
            mock_model_to_dict.return_value = {'input': 'input', 'output': 'output'}
            
            # Mock submission creation
            self.mock_submission_repo.create.return_value = self.sample_submission
            
            # Mock serializer
            with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseSecureSerializer') as mock_serializer:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {'submission_id': 'sub_123'}
                mock_serializer.return_value = mock_serializer_instance
                
                # Act
                result = self.submission_service.submit_problem_on_topic(account_id, problem_id, topic_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get.assert_called_once_with(problem_id)
        self.mock_problem_repo.get_testcases.assert_called_once_with(problem_id, deprecated=False)
        self.mock_submission_repo.create.assert_called_once()
        self.mock_submission_repo.create_or_update_best.assert_called_once()
        self.mock_submission_repo.bulk_create_testcases.assert_called_once()
        self.mock_problem_service.update_problem_difficulty.assert_called_once_with(self.sample_problem)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('submission_id', result)

    def test_submit_problem_success(self):
        """Test submitting problem"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        testcases = [self.sample_testcase]
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_problem_repo.get_testcases.return_value = testcases
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Mock grading result
        mock_grading_result = Mock()
        mock_grading_result.is_passed = True
        mock_testcase_result = Mock()
        mock_testcase_result.is_passed = True
        mock_grading_result.data = [mock_testcase_result]
        
        # Mock grader
        with patch('api.services.submission.submission_service.regexMatching') as mock_regex, \
             patch('api.services.submission.submission_service.model_to_dict') as mock_model_to_dict:
            
            # Mock grader dictionary access
            mock_grader_class = Mock()
            mock_grader_instance = Mock()
            mock_grader_instance.grading.return_value = mock_grading_result
            mock_grader_class.return_value = mock_grader_instance
            self.mock_grader.__getitem__ = Mock(return_value=mock_grader_class)
            
            mock_regex.return_value = True
            mock_model_to_dict.return_value = {'input': 'input', 'output': 'output'}
            
            # Mock submission creation
            self.mock_submission_repo.create.return_value = self.sample_submission
            
            # Mock serializer
            with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseSecureSerializer') as mock_serializer:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {'submission_id': 'sub_123'}
                mock_serializer.return_value = mock_serializer_instance
                
                # Act
                result = self.submission_service.submit_problem(account_id, problem_id, mock_request)
        
        # Assert
        self.mock_problem_repo.get.assert_called_once_with(problem_id)
        self.mock_problem_repo.get_testcases.assert_called_once_with(problem_id, deprecated=False)
        self.mock_submission_repo.create.assert_called_once()
        self.mock_submission_repo.create_or_update_best.assert_called_once()
        self.mock_submission_repo.bulk_create_testcases.assert_called_once()
        self.mock_problem_service.update_problem_difficulty.assert_called_once_with(self.sample_problem)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('submission_id', result)

    def test_submit_problem_with_exception(self):
        """Test submitting problem with exception"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        # Mock exception in submit_problem_function
        with patch.object(self.submission_service, 'submit_problem_function', side_effect=Exception("Test error")):
            # Act & Assert
            with self.assertRaises(InternalServerError):
                self.submission_service.submit_problem(account_id, problem_id, mock_request)

    def test_submit_problem_regex_mismatch(self):
        """Test submitting problem with regex mismatch"""
        # Arrange
        account_id = 'acc_123'
        problem_id = 'prob_123'
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        testcases = [self.sample_testcase]
        
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_problem_repo.get_testcases.return_value = testcases
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Mock grading result for failed submission
        mock_grading_result = Mock()
        mock_grading_result.is_passed = False
        mock_testcase_result = Mock()
        mock_testcase_result.is_passed = False
        mock_grading_result.data = [mock_testcase_result]
        
        # Mock grader and regex mismatch
        with patch('api.services.submission.submission_service.regexMatching') as mock_regex, \
             patch('api.services.submission.submission_service.model_to_dict') as mock_model_to_dict:
            
            # Mock grader dictionary access
            mock_grader_class = Mock()
            mock_grader_instance = Mock()
            mock_grader_instance.grading.return_value = mock_grading_result
            mock_grader_class.return_value = mock_grader_instance
            self.mock_grader.__getitem__ = Mock(return_value=mock_grader_class)
            
            mock_regex.return_value = False
            mock_model_to_dict.return_value = {'input': 'input', 'output': 'output'}
            
            # Mock submission creation
            self.mock_submission_repo.create.return_value = self.sample_submission
            
            # Mock serializer
            with patch('api.services.submission.submission_service.SubmissionPopulateSubmissionTestcaseSecureSerializer') as mock_serializer:
                mock_serializer_instance = Mock()
                mock_serializer_instance.data = {'submission_id': 'sub_123'}
                mock_serializer.return_value = mock_serializer_instance
                
                # Act
                result = self.submission_service.submit_problem_on_topic(account_id, problem_id, topic_id, mock_request)
        
        # Assert
        # Should still create submission but with failed grading
        self.mock_submission_repo.create.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('submission_id', result)

    def test_service_initialization(self):
        """Test that service initializes correctly with repositories"""
        # Arrange & Act
        service = SubmissionService(
            submission_repo=self.mock_submission_repo,
            problem_repo=self.mock_problem_repo,
            account_repo=self.mock_account_repo,
            topic_repo=self.mock_topic_repo,
            problem_service=self.mock_problem_service,
            grader=self.mock_grader
        )
        
        # Assert
        self.assertEqual(service.submission_repo, self.mock_submission_repo)
        self.assertEqual(service.problem_repo, self.mock_problem_repo)
        self.assertEqual(service.account_repo, self.mock_account_repo)
        self.assertEqual(service.topic_repo, self.mock_topic_repo)
        self.assertEqual(service.problem_service, self.mock_problem_service)


if __name__ == '__main__':
    unittest.main()
