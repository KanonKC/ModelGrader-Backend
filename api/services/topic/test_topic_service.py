import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.services.topic.topic_service import TopicService
from api.repositories.topic_repository import TopicRepository
from api.repositories.account_repository import AccountRepository
from api.repositories.permission_repository import PermissionRepository
from api.repositories.group_repository import GroupRepository
from api.repositories.collection_repository import CollectionRepository
from api.models import Topic, Account, TopicCollection, TopicGroupPermission, Collection, Group
from api.errors.common import BadRequestError, InternalServerError, ItemNotFoundError


class TestTopicService(TestCase):
    """Unit tests for TopicService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_topic_repo = Mock(spec=TopicRepository)
        self.mock_account_repo = Mock(spec=AccountRepository)
        self.mock_permission_repo = Mock(spec=PermissionRepository)
        self.mock_group_repo = Mock(spec=GroupRepository)
        self.mock_collection_repo = Mock(spec=CollectionRepository)
        
        self.topic_service = TopicService(
            topic_repo=self.mock_topic_repo,
            account_repo=self.mock_account_repo,
            permission_repo=self.mock_permission_repo,
            group_repo=self.mock_group_repo,
            collection_repo=self.mock_collection_repo
        )
        
        # Sample data
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        
        self.sample_topic = Mock(spec=Topic)
        self.sample_topic.topic_id = 'topic_123'
        self.sample_topic.name = 'Test Topic'
        self.sample_topic.description = 'Test Description'
        self.sample_topic.creator_id = 'acc_123'
        self.sample_topic.created_date = '2023-01-01T00:00:00Z'
        self.sample_topic.updated_date = '2023-01-01T00:00:00Z'
        
        self.sample_collection = Mock(spec=Collection)
        self.sample_collection.collection_id = 'coll_123'
        self.sample_collection.name = 'Test Collection'
        self.sample_collection.problems = []
        
        self.sample_topic_collection = Mock(spec=TopicCollection)
        self.sample_topic_collection.topic_id = 'topic_123'
        self.sample_topic_collection.collection_id = 'coll_123'
        self.sample_topic_collection.collection = self.sample_collection
        self.sample_topic_collection.order = 0
        
        self.sample_group = Mock(spec=Group)
        self.sample_group.group_id = 'group_123'
        self.sample_group.name = 'Test Group'
        
        self.sample_request_data = {
            'name': 'Test Topic',
            'description': 'Test Description'
        }

    def test_create_topic_success(self):
        """Test successful topic creation"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        self.mock_topic_repo.create.return_value = self.sample_topic
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'topic_id': 'topic_123',
                'name': 'Test Topic',
                'description': 'Test Description'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.create_topic(account_id, mock_request)
        
        # Assert
        expected_topic_data = {
            'creator_id': account_id,
            'name': 'Test Topic',
            'description': 'Test Description'
        }
        self.mock_topic_repo.create.assert_called_once_with(expected_topic_data)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)
        self.assertIn('name', result)

    def test_delete_topic_success(self):
        """Test successful topic deletion"""
        # Arrange
        topic_id = 'topic_123'
        
        # Act
        result = self.topic_service.delete_topic(topic_id)
        
        # Assert
        self.mock_topic_repo.delete.assert_called_once_with(topic_id)
        self.assertIsNone(result)

    def test_get_topic_success(self):
        """Test successful topic retrieval"""
        # Arrange
        topic_id = 'topic_123'
        permissions = [Mock(spec=TopicGroupPermission)]
        collections = [self.sample_topic_collection]
        
        self.mock_topic_repo.get.return_value = self.sample_topic
        self.mock_permission_repo.get_topic_permissions.return_value = permissions
        self.mock_topic_repo.get_collections.return_value = collections
        self.mock_collection_repo.get_problems_by_collections.return_value = []
        self.mock_permission_repo.get_collection_permissions_for_collections.return_value = {}
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupAndTopicGroupPermissionPopulateGroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'topic_id': 'topic_123',
                'name': 'Test Topic',
                'collections': []
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.get_topic(topic_id)
        
        # Assert
        self.mock_topic_repo.get.assert_called_once_with(topic_id)
        self.mock_permission_repo.get_topic_permissions.assert_called_once_with(topic_id)
        self.mock_topic_repo.get_collections.assert_called_once_with(topic_id)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)

    def test_get_all_topics_success(self):
        """Test getting all topics"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {'account_id': 'acc_123'}
        
        topics = [self.sample_topic]
        self.mock_topic_repo.list.return_value = topics
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'topic_id': 'topic_123', 'name': 'Test Topic'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.get_all_topics(mock_request)
        
        # Assert
        expected_filters = {'creator_id': 'acc_123'}
        self.mock_topic_repo.list.assert_called_once_with(filters=expected_filters)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topics', result)
        self.assertIsInstance(result['topics'], list)

    def test_get_all_topics_without_account_filter(self):
        """Test getting all topics without account filter"""
        # Arrange
        mock_request = Mock()
        mock_request.query_params = {}  # No account_id
        
        topics = [self.sample_topic]
        self.mock_topic_repo.list.return_value = topics
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'topic_id': 'topic_123', 'name': 'Test Topic'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.get_all_topics(mock_request)
        
        # Assert
        self.mock_topic_repo.list.assert_called_once_with(filters={})
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topics', result)

    def test_update_topic_success(self):
        """Test successful topic update"""
        # Arrange
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = {
            'name': 'Updated Topic',
            'description': 'Updated Description'
        }
        
        updated_topic = Mock(spec=Topic)
        updated_topic.topic_id = topic_id
        updated_topic.name = 'Updated Topic'
        
        self.mock_topic_repo.update.return_value = updated_topic
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'topic_id': 'topic_123',
                'name': 'Updated Topic'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.update_topic(topic_id, mock_request)
        
        # Assert
        self.mock_topic_repo.update.assert_called_once_with(topic_id, {
            'name': 'Updated Topic',
            'description': 'Updated Description'
        })
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)

    def test_get_all_topics_by_account_success(self):
        """Test getting all topics by account"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        
        personal_topics = [self.sample_topic]
        group_ids = ['group_123']
        manageable_topics = []
        
        self.mock_account_repo.get.return_value = self.sample_account
        self.mock_topic_repo.get_by_creator.return_value = personal_topics
        self.mock_group_repo.get_ids_by_account.return_value = group_ids
        self.mock_topic_repo.get_manageable_by_ids.return_value = manageable_topics
        # Mock QuerySet-like object for collections
        mock_collections = Mock()
        mock_collections.filter.return_value = []
        self.mock_topic_repo.get_many_collections.return_value = mock_collections
        
        # Mock serializers
        with patch('api.services.topic.topic_service.TopicPopulateTopicCollectionPopulateCollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'topic_id': 'topic_123', 'name': 'Test Topic'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.get_all_topics_by_account(account_id, mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        self.mock_topic_repo.get_by_creator.assert_called_once_with(account_id)
        self.mock_group_repo.get_ids_by_account.assert_called_once_with(account_id)
        self.mock_topic_repo.get_manageable_by_ids.assert_called_once_with(group_ids)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topics', result)
        self.assertIn('manageable_topics', result)

    def test_get_all_topics_by_account_account_not_found(self):
        """Test getting all topics when account doesn't exist"""
        # Arrange
        account_id = 'nonexistent'
        mock_request = Mock()
        
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Account.DoesNotExist):
            self.topic_service.get_all_topics_by_account(account_id, mock_request)
        
        self.mock_account_repo.get.assert_called_once_with(account_id)

    def test_get_all_accessed_topics_by_account_success(self):
        """Test getting all accessed topics by account"""
        # Arrange
        account_id = 'acc_123'
        
        # Mock accessible topics
        accessible_topic = Mock()
        accessible_topic.topic = self.sample_topic
        
        self.mock_group_repo.get_accessible_by_account.return_value = [accessible_topic]
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'topic_id': 'topic_123', 'name': 'Test Topic'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.get_all_accessed_topics_by_account(account_id)
        
        # Assert
        self.mock_group_repo.get_accessible_by_account.assert_called_once_with(account_id)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topics', result)

    def test_get_topic_public_success(self):
        """Test getting public topic"""
        # Arrange
        topic_id = 'topic_123'
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.query_params = {'account_id': account_id}
        
        group_ids = ['group_123']
        topic_collections = [self.sample_topic_collection]
        
        self.mock_topic_repo.get.return_value = self.sample_topic
        self.mock_account_repo.get.return_value = self.sample_account
        self.mock_group_repo.get_accessible_collections_with_access.return_value = topic_collections
        self.mock_group_repo.get_ids_by_account.return_value = group_ids
        self.mock_permission_repo.get_accessible_problems_for_collections.return_value = topic_collections
        self.mock_topic_repo.get_best_submission_for_problem.return_value = None
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'topic_id': 'topic_123',
                'name': 'Test Topic',
                'collections': []
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.get_topic_public(topic_id, mock_request)
        
        # Assert
        self.mock_topic_repo.get.assert_called_once_with(topic_id)
        self.mock_account_repo.get.assert_called_once_with(account_id)
        self.mock_group_repo.get_accessible_collections_with_access.assert_called_once_with(topic_id, account_id)
        self.mock_group_repo.get_ids_by_account.assert_called_once_with(account_id)
        self.mock_permission_repo.get_accessible_problems_for_collections.assert_called_once_with(topic_collections, group_ids)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)

    def test_update_groups_permission_to_topic_success(self):
        """Test updating group permissions for topic"""
        # Arrange
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = {
            'groups': [
                {'group_id': 'group_123', 'permission_view_topics': True, 'permission_manage_topics': False, 'permission_view_topics_log': False}
            ]
        }
        
        self.mock_topic_repo.get.return_value = self.sample_topic
        self.mock_group_repo.get.return_value = self.sample_group
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicPopulateTopicGroupPermissionsSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'topic_id': 'topic_123',
                'group_permissions': []
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.update_groups_permission_to_topic(topic_id, mock_request)
        
        # Assert
        self.mock_topic_repo.get.assert_called_once_with(topic_id)
        self.mock_permission_repo.delete_topic_permissions.assert_called_once_with(topic_id)
        self.mock_group_repo.get.assert_called_once_with('group_123')
        self.mock_permission_repo.bulk_create_topic_permissions.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)

    def test_update_collections_to_topic_success(self):
        """Test updating collections in topic"""
        # Arrange
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = {
            'collection_ids': ['coll_123', 'coll_456']
        }
        
        self.mock_topic_repo.get.return_value = self.sample_topic
        self.mock_collection_repo.get.side_effect = [self.sample_collection, self.sample_collection]
        
        # Mock serializers
        with patch('api.services.topic.topic_service.TopicCollectionPopulateCollectionSerializer') as mock_collection_serializer, \
             patch('api.services.topic.topic_service.TopicSerializer') as mock_topic_serializer:
            
            mock_collection_serializer_instance = Mock()
            mock_collection_serializer_instance.data = [{'collection_id': 'coll_123'}]
            mock_collection_serializer.return_value = mock_collection_serializer_instance
            
            mock_topic_serializer_instance = Mock()
            mock_topic_serializer_instance.data = {'topic_id': 'topic_123'}
            mock_topic_serializer.return_value = mock_topic_serializer_instance
            
            # Act
            result = self.topic_service.update_collections_to_topic(topic_id, mock_request)
        
        # Assert
        self.mock_topic_repo.get.assert_called_once_with(topic_id)
        self.mock_topic_repo.delete_collections.assert_called_once_with(topic_id)
        self.mock_collection_repo.get.assert_any_call('coll_123')
        self.mock_collection_repo.get.assert_any_call('coll_456')
        self.mock_topic_repo.bulk_create_collections.assert_called_once()
        self.mock_topic_repo.update_with_timestamp.assert_called_once_with(topic_id)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)
        self.assertIn('collections', result)

    def test_add_collections_to_topic_success(self):
        """Test adding collections to topic"""
        # Arrange
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = {
            'collection_ids': ['coll_123']
        }
        
        self.mock_topic_repo.get.return_value = self.sample_topic
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_topic_repo.find_existing_collection.return_value = None
        
        # Mock topic collection creation
        created_topic_collection = Mock(spec=TopicCollection)
        self.mock_topic_repo.create_collection.return_value = created_topic_collection
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicCollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'collection_id': 'coll_123'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.add_collections_to_topic(topic_id, mock_request)
        
        # Assert
        self.mock_topic_repo.get.assert_called_once_with(topic_id)
        self.mock_collection_repo.get.assert_called_once_with('coll_123')
        self.mock_topic_repo.find_existing_collection.assert_called_once_with(topic_id, 'coll_123')
        self.mock_topic_repo.create_collection.assert_called_once_with(topic_id, 'coll_123', 0)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)
        self.assertIn('collections', result)

    def test_add_collections_to_topic_with_existing_collection(self):
        """Test adding collections to topic when collection already exists"""
        # Arrange
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = {
            'collection_ids': ['coll_123']
        }
        
        existing_collection = Mock(spec=TopicCollection)
        
        self.mock_topic_repo.get.return_value = self.sample_topic
        self.mock_collection_repo.get.return_value = self.sample_collection
        self.mock_topic_repo.find_existing_collection.return_value = existing_collection
        
        # Mock topic collection creation
        created_topic_collection = Mock(spec=TopicCollection)
        self.mock_topic_repo.create_collection.return_value = created_topic_collection
        
        # Mock serializer
        with patch('api.services.topic.topic_service.TopicCollectionSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {'collection_id': 'coll_123'}
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.topic_service.add_collections_to_topic(topic_id, mock_request)
        
        # Assert
        existing_collection.delete.assert_called_once()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('topic_id', result)
        self.assertIn('collections', result)

    def test_remove_collections_from_topic_success(self):
        """Test removing collections from topic"""
        # Arrange
        topic_id = 'topic_123'
        mock_request = Mock()
        mock_request.data = {
            'collection_ids': ['coll_123', 'coll_456']
        }
        
        # Act
        result = self.topic_service.remove_collections_from_topic(topic_id, mock_request)
        
        # Assert
        self.mock_topic_repo.delete_many_collections.assert_called_once_with(topic_id, ['coll_123', 'coll_456'])
        self.assertIsNone(result)

    def test_service_initialization(self):
        """Test that service initializes correctly with repositories"""
        # Arrange & Act
        service = TopicService(
            topic_repo=self.mock_topic_repo,
            account_repo=self.mock_account_repo,
            permission_repo=self.mock_permission_repo,
            group_repo=self.mock_group_repo,
            collection_repo=self.mock_collection_repo
        )
        
        # Assert
        self.assertEqual(service.topic_repo, self.mock_topic_repo)
        self.assertEqual(service.account_repo, self.mock_account_repo)
        self.assertEqual(service.permission_repo, self.mock_permission_repo)
        self.assertEqual(service.group_repo, self.mock_group_repo)
        self.assertEqual(service.collection_repo, self.mock_collection_repo)


if __name__ == '__main__':
    unittest.main()
