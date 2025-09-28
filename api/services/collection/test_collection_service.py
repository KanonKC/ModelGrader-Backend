import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.services.collection.collection_service import CollectionService
from api.repositories.collection_repository import CollectionRepository
from api.repositories.account_repository import AccountRepository
from api.repositories.problem_repository import ProblemRepository
from api.repositories.permission_repository import PermissionRepository
from api.repositories.group_repository import GroupRepository
from api.models import Collection, Problem, CollectionProblem, CollectionGroupPermission, Group
from api.errors.common import BadRequestError, InternalServerError, ItemNotFoundError


class TestCollectionService(TestCase):
    """Unit tests for CollectionService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_collection_repo = Mock(spec=CollectionRepository)
        self.mock_account_repo = Mock(spec=AccountRepository)
        self.mock_problem_repo = Mock(spec=ProblemRepository)
        self.mock_permission_repo = Mock(spec=PermissionRepository)
        self.mock_group_repo = Mock(spec=GroupRepository)
        
        self.collection_service = CollectionService(
            collection_repo=self.mock_collection_repo,
            account_repo=self.mock_account_repo,
            problem_repo=self.mock_problem_repo,
            permission_repo=self.mock_permission_repo,
            group_repo=self.mock_group_repo
        )
        
        # Sample data
        self.sample_collection = Mock(spec=Collection)
        self.sample_collection.collection_id = 'coll_123'
        self.sample_collection.name = 'Test Collection'
        self.sample_collection.description = 'Test Description'
        self.sample_collection.is_private = False
        self.sample_collection.is_active = True
        self.sample_collection.creator_id = 'acc_123'
        self.sample_collection._state = Mock()
        self.sample_collection._state.db = 'default'
        
        self.sample_problem = Mock(spec=Problem)
        self.sample_problem.problem_id = 'prob_123'
        self.sample_problem.title = 'Test Problem'
        self.sample_problem._state = Mock()
        self.sample_problem._state.db = 'default'
        
        self.sample_collection_problem = Mock(spec=CollectionProblem)
        self.sample_collection_problem.problem = self.sample_problem
        self.sample_collection_problem.order = 0
        self.sample_collection_problem._state = Mock()
        self.sample_collection_problem._state.db = 'default'
        
        self.sample_group = Mock(spec=Group)
        self.sample_group.group_id = 'group_123'
        self.sample_group.name = 'Test Group'
        self.sample_group._state = Mock()
        self.sample_group._state.db = 'default'
        
        self.sample_request_data = {
            'name': 'Test Collection',
            'description': 'Test Description',
            'is_private': False,
            'is_active': True
        }

    @patch('api.services.collection.collection_service.CollectionSerializer')
    def test_create_collection_success(self, mock_serializer_class):
        """Test successful collection creation"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.is_valid.return_value = True
        mock_serializer_instance.data = {
            'collection_id': 'coll_123',
            'name': 'Test Collection',
            'description': 'Test Description'
        }
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        result = self.collection_service.create_collection(account_id, mock_request)
        
        # Assert
        mock_serializer_class.assert_called_once()
        call_args = mock_serializer_class.call_args[1]['data']  # Get keyword arguments
        self.assertEqual(call_args['creator'], account_id)
        self.assertEqual(call_args['name'], 'Test Collection')
        
        mock_serializer_instance.is_valid.assert_called_once()
        mock_serializer_instance.save.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)
        self.assertIn('name', result)

    @patch('api.services.collection.collection_service.CollectionSerializer')
    def test_create_collection_validation_error(self, mock_serializer_class):
        """Test collection creation with validation error"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        # Mock serializer with validation error
        mock_serializer_instance = Mock()
        mock_serializer_instance.is_valid.return_value = False
        mock_serializer_instance.errors = {'name': ['This field is required.']}
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act & Assert
        with self.assertRaises(BadRequestError) as context:
            self.collection_service.create_collection(account_id, mock_request)
        
        self.assertIn('This field is required.', str(context.exception))

    def test_delete_collection_success(self):
        """Test successful collection deletion"""
        # Arrange
        collection_id = 'coll_123'
        self.mock_collection_repo.get.return_value = self.sample_collection
        
        # Act
        result = self.collection_service.delete_collection(collection_id)
        
        # Assert
        self.mock_collection_repo.get.assert_called_once_with(collection_id)
        self.sample_collection.delete.assert_called_once()
        self.assertIsNone(result)

    def test_get_collection_success(self):
        """Test successful collection retrieval"""
        # Arrange
        collection_id = 'coll_123'
        problems = [self.sample_collection_problem]
        permissions = [Mock(spec=CollectionGroupPermission)]
        
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_collection_repo.get_problems.return_value = problems
        self.mock_permission_repo.get_collection_permissions.return_value = permissions
        self.mock_problem_repo.get_testcases.return_value = []
        self.mock_permission_repo.get_problem_permissions.return_value = []
        
        # Mock serializer
        with patch('api.services.collection.collection_service.CollectionPopulateCollectionProblemsPopulateProblemPopulateAccountAndTestcasesAndProblemGroupPermissionsPopulateGroupAndCollectionGroupPermissionsPopulateGroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'collection_id': 'coll_123',
                'name': 'Test Collection',
                'problems': []
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.get_collection(collection_id)
        
        # Assert
        self.mock_collection_repo.get.assert_called_once_with(collection_id)
        self.mock_collection_repo.get_problems.assert_called_once_with(collection_id)
        self.mock_permission_repo.get_collection_permissions.assert_called_once_with(collection_id)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)

    def test_get_all_collections_success(self):
        """Test getting all collections"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {'account_id': 'acc_123'}
        
        # Create a mock QuerySet-like object
        mock_queryset = Mock()
        mock_queryset.filter.return_value = [self.sample_collection]
        collections = [self.sample_collection]
        self.mock_collection_repo.list.return_value = mock_queryset
        self.mock_collection_repo.get_problems.return_value = []
        
        # Mock serializer
        with patch('api.services.collection.collection_service.CollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'collection_id': 'coll_123',
                'name': 'Test Collection'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.get_all_collections(mock_request)
        
        # Assert
        self.mock_collection_repo.list.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('collections', result)
        self.assertIsInstance(result['collections'], list)

    def test_get_all_collections_without_account_filter(self):
        """Test getting all collections without account filter"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {}  # No account_id
        
        collections = [self.sample_collection]
        self.mock_collection_repo.list.return_value = collections
        self.mock_collection_repo.get_problems.return_value = []
        
        # Mock serializer
        with patch('api.services.collection.collection_service.CollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'collection_id': 'coll_123',
                'name': 'Test Collection'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.get_all_collections(mock_request)
        
        # Assert
        self.mock_collection_repo.list.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('collections', result)

    def test_get_all_collections_by_account_success(self):
        """Test getting all collections by account"""
        # Arrange
        account_id = 'acc_123'
        collections = [self.sample_collection]
        group_ids = ['group_123']
        manageable_collections = []
        
        self.mock_collection_repo.get_by_creator.return_value = collections
        self.mock_collection_repo.get_manageable_by_account.return_value = manageable_collections
        self.mock_group_repo.get_by_creator.return_value = group_ids
        # Create a mock QuerySet-like object for problemCollections
        mock_problem_queryset = Mock()
        mock_problem_queryset.filter.return_value = []
        self.mock_collection_repo.get_problems_by_collections.return_value = mock_problem_queryset
        
        # Mock serializers
        with patch('api.services.collection.collection_service.CollectionPopulateCollectionProblemsPopulateProblemSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'collection_id': 'coll_123', 'name': 'Test Collection'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.get_all_collections_by_account(account_id)
        
        # Assert
        self.mock_collection_repo.get_by_creator.assert_called_once_with(account_id)
        self.mock_group_repo.get_by_creator.assert_called_once_with(account_id)
        self.mock_collection_repo.get_manageable_by_account.assert_called_once_with(group_ids)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('collections', result)
        self.assertIn('manageable_collections', result)

    def test_update_collection_success(self):
        """Test successful collection update"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'name': 'Updated Collection',
            'description': 'Updated Description',
            'is_private': True,
            'is_active': False
        }
        
        updated_collection = Mock(spec=Collection)
        updated_collection.collection_id = collection_id
        updated_collection.name = 'Updated Collection'
        
        self.mock_collection_repo.update_with_timestamp.return_value = updated_collection
        
        # Mock serializer
        with patch('api.services.collection.collection_service.CollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'collection_id': 'coll_123',
                'name': 'Updated Collection'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.update_collection(collection_id, mock_request)
        
        # Assert
        expected_update_data = {
            'name': 'Updated Collection',
            'description': 'Updated Description',
            'is_private': True,
            'is_active': False
        }
        self.mock_collection_repo.update_with_timestamp.assert_called_once_with(collection_id, expected_update_data)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)

    def test_update_collection_with_none_values(self):
        """Test updating collection with None values (should be filtered out)"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'name': 'Updated Collection',
            'description': None,
            'is_private': None,
            'is_active': True
        }
        
        updated_collection = Mock(spec=Collection)
        self.mock_collection_repo.update_with_timestamp.return_value = updated_collection
        
        # Mock serializer
        with patch('api.services.collection.collection_service.CollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'collection_id': 'coll_123', 'name': 'Updated Collection'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.update_collection(collection_id, mock_request)
        
        # Assert
        expected_update_data = {
            'name': 'Updated Collection',
            'is_active': True
        }
        self.mock_collection_repo.update_with_timestamp.assert_called_once_with(collection_id, expected_update_data)

    def test_update_group_permissions_collection_success(self):
        """Test updating group permissions for collection"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'groups': [
                {'group_id': 'group_123', 'permission_view_collections': True, 'permission_manage_collections': False}
            ]
        }
        
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_group_repo.get.return_value = self.sample_group
        
        # Mock serializer
        with patch('api.services.collection.collection_service.CollectionPopulateCollectionGroupPermissionsPopulateGroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'collection_id': 'coll_123',
                'group_permissions': []
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.collection_service.update_group_permissions_collection(collection_id, mock_request)
        
        # Assert
        self.mock_collection_repo.get.assert_called_once_with(collection_id)
        self.mock_permission_repo.delete_collection_permissions.assert_called_once_with(collection_id)
        self.mock_group_repo.get.assert_called_once_with('group_123')
        self.mock_permission_repo.bulk_create_collection_permissions.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)

    def test_update_problems_to_collection_success(self):
        """Test updating problems in collection"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'problem_ids': ['prob_123', 'prob_456']
        }
        
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_problem_repo.get.side_effect = [self.sample_problem, self.sample_problem]
        
        # Mock serializers
        with patch('api.services.collection.collection_service.CollectionProblemPopulateProblemSecureSerializer') as mock_problem_serializer, \
             patch('api.services.collection.collection_service.CollectionSerializer') as mock_collection_serializer:
            
            mock_problem_serializer_instance = Mock()
            mock_problem_serializer_instance.data = [{'problem_id': 'prob_123'}]
            mock_problem_serializer.return_value = mock_problem_serializer_instance
            
            mock_collection_serializer_instance = Mock()
            mock_collection_serializer_instance.data = {'collection_id': 'coll_123'}
            mock_collection_serializer.return_value = mock_collection_serializer_instance
            
            # Act
            result = self.collection_service.update_problems_to_collection(collection_id, mock_request)
        
        # Assert
        self.mock_collection_repo.get.assert_called_once_with(collection_id)
        self.mock_collection_repo.delete_problems.assert_called_once_with(collection_id)
        self.mock_problem_repo.get.assert_any_call('prob_123')
        self.mock_problem_repo.get.assert_any_call('prob_456')
        self.mock_collection_repo.bulk_create_problems.assert_called_once()
        self.mock_collection_repo.update_with_timestamp.assert_called_once_with(collection_id, {})
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)
        self.assertIn('problems', result)

    def test_add_problems_to_collection_success(self):
        """Test adding problems to collection"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'problem_ids': ['prob_123']
        }
        
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_collection_repo.find_existing_problem.return_value = None
        self.mock_collection_repo.update_with_timestamp.return_value = self.sample_collection
        
        # Mock CollectionProblem creation and save
        with patch('api.services.collection.collection_service.CollectionProblem') as mock_collection_problem_class, \
             patch('api.services.collection.collection_service.CollectionProblemPopulateProblemSecureSerializer') as mock_problem_serializer, \
             patch('api.services.collection.collection_service.CollectionSerializer') as mock_collection_serializer:
            
            mock_collection_problem_instance = Mock()
            mock_collection_problem_instance.save = Mock()
            mock_collection_problem_class.return_value = mock_collection_problem_instance
            
            mock_problem_serializer_instance = Mock()
            mock_problem_serializer_instance.data = [{'problem_id': 'prob_123'}]
            mock_problem_serializer.return_value = mock_problem_serializer_instance
            
            mock_collection_serializer_instance = Mock()
            mock_collection_serializer_instance.data = {'collection_id': 'coll_123'}
            mock_collection_serializer.return_value = mock_collection_serializer_instance
            
            # Act
            result = self.collection_service.add_problems_to_collection(collection_id, mock_request)
        
        # Assert
        self.mock_collection_repo.get.assert_called_once_with(collection_id)
        self.mock_problem_repo.get.assert_called_once_with('prob_123')
        self.mock_collection_repo.find_existing_problem.assert_called_once_with('prob_123', collection_id)
        self.mock_collection_repo.update_with_timestamp.assert_called_once_with(collection_id, {})
        
        # Verify CollectionProblem was created and saved
        mock_collection_problem_class.assert_called_once()
        mock_collection_problem_instance.save.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)
        self.assertIn('problems', result)

    def test_add_problems_to_collection_with_existing_problem(self):
        """Test adding problems to collection when problem already exists"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'problem_ids': ['prob_123']
        }
        
        existing_problem = Mock(spec=CollectionProblem)
        existing_problem.delete = Mock()
        
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_problem_repo.get.return_value = self.sample_problem
        self.mock_collection_repo.find_existing_problem.return_value = existing_problem
        self.mock_collection_repo.update_with_timestamp.return_value = self.sample_collection
        
        # Mock CollectionProblem creation and save
        with patch('api.services.collection.collection_service.CollectionProblem') as mock_collection_problem_class, \
             patch('api.services.collection.collection_service.CollectionProblemPopulateProblemSecureSerializer') as mock_problem_serializer, \
             patch('api.services.collection.collection_service.CollectionSerializer') as mock_collection_serializer:
            
            mock_collection_problem_instance = Mock()
            mock_collection_problem_instance.save = Mock()
            mock_collection_problem_class.return_value = mock_collection_problem_instance
            
            mock_problem_serializer_instance = Mock()
            mock_problem_serializer_instance.data = [{'problem_id': 'prob_123'}]
            mock_problem_serializer.return_value = mock_problem_serializer_instance
            
            mock_collection_serializer_instance = Mock()
            mock_collection_serializer_instance.data = {'collection_id': 'coll_123'}
            mock_collection_serializer.return_value = mock_collection_serializer_instance
            
            # Act
            result = self.collection_service.add_problems_to_collection(collection_id, mock_request)
        
        # Assert
        existing_problem.delete.assert_called_once()
        mock_collection_problem_class.assert_called_once()
        mock_collection_problem_instance.save.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('collection_id', result)
        self.assertIn('problems', result)

    def test_remove_problems_from_collection_success(self):
        """Test removing problems from collection"""
        # Arrange
        collection_id = 'coll_123'
        mock_request = Mock()
        mock_request.data = {
            'problem_ids': ['prob_123', 'prob_456']
        }
        
        # Act
        result = self.collection_service.remove_problems_from_collection(collection_id, mock_request)
        
        # Assert
        self.mock_collection_repo.delete_many_problems.assert_called_once_with(collection_id, ['prob_123', 'prob_456'])
        self.mock_collection_repo.update_with_timestamp.assert_called_once_with(collection_id, {})
        self.assertIsNone(result)

    def test_service_initialization(self):
        """Test that service initializes correctly with repositories"""
        # Arrange & Act
        service = CollectionService(
            collection_repo=self.mock_collection_repo,
            account_repo=self.mock_account_repo,
            problem_repo=self.mock_problem_repo,
            permission_repo=self.mock_permission_repo,
            group_repo=self.mock_group_repo
        )
        
        # Assert
        self.assertEqual(service.collection_repo, self.mock_collection_repo)
        self.assertEqual(service.account_repo, self.mock_account_repo)
        self.assertEqual(service.problem_repo, self.mock_problem_repo)
        self.assertEqual(service.permission_repo, self.mock_permission_repo)
        self.assertEqual(service.group_repo, self.mock_group_repo)


if __name__ == '__main__':
    unittest.main()
