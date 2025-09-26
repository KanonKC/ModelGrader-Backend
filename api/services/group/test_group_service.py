import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.services.group.group_service import GroupService
from api.repositories.group_repository import GroupRepository
from api.repositories.account_repository import AccountRepository
from api.models import Group, Account, GroupMember
from api.errors.common import BadRequestError, InternalServerError, ItemNotFoundError


class TestGroupService(TestCase):
    """Unit tests for GroupService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_group_repo = Mock(spec=GroupRepository)
        self.mock_account_repo = Mock(spec=AccountRepository)
        
        self.group_service = GroupService(
            group_repo=self.mock_group_repo,
            account_repo=self.mock_account_repo
        )
        
        # Sample data
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        self.sample_account.first_name = 'Test'
        self.sample_account.last_name = 'User'
        
        self.sample_group = Mock(spec=Group)
        self.sample_group.group_id = 'group_123'
        self.sample_group.name = 'Test Group'
        self.sample_group.description = 'Test Description'
        self.sample_group.creator_id = 'acc_123'
        
        self.sample_group_member = Mock(spec=GroupMember)
        self.sample_group_member.group_id = 'group_123'
        self.sample_group_member.account_id = 'acc_123'
        self.sample_group_member.account = self.sample_account
        
        self.sample_request_data = {
            'name': 'Test Group',
            'description': 'Test Description'
        }

    def test_create_group_success(self):
        """Test successful group creation"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        self.mock_account_repo.get.return_value = self.sample_account
        self.mock_group_repo.create.return_value = self.sample_group
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Test Group',
                'description': 'Test Description'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.create_group(account_id, mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        
        # Verify group creation data
        expected_group_data = {
            'creator_id': 'acc_123',
            'name': 'Test Group',
            'description': 'Test Description'
        }
        self.mock_group_repo.create.assert_called_once_with(expected_group_data)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)
        self.assertIn('name', result)

    def test_create_group_account_not_found(self):
        """Test group creation when account doesn't exist"""
        # Arrange
        account_id = 'nonexistent'
        mock_request = Mock()
        mock_request.data = self.sample_request_data.copy()
        
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Account.DoesNotExist):
            self.group_service.create_group(account_id, mock_request)
        
        self.mock_account_repo.get.assert_called_once_with(account_id)

    def test_delete_group_success(self):
        """Test successful group deletion"""
        # Arrange
        group_id = 'group_123'
        
        # Act
        result = self.group_service.delete_group(group_id)
        
        # Assert
        self.mock_group_repo.delete.assert_called_once_with(group_id)
        self.assertIsNone(result)

    def test_get_group_success_without_members(self):
        """Test getting a group without populating members"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.GET = {}  # No populate_members parameter
        
        self.mock_group_repo.get.return_value = self.sample_group
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Test Group'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.get_group(group_id, mock_request)
        
        # Assert
        self.mock_group_repo.get.assert_called_once_with(group_id)
        self.mock_group_repo.get_members.assert_not_called()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)

    def test_get_group_success_with_members(self):
        """Test getting a group with populating members"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.GET = {'populate_members': 'true'}
        
        members = [self.sample_group_member]
        self.mock_group_repo.get.return_value = self.sample_group
        self.mock_group_repo.get_members.return_value = members
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupPopulateGroupMemberPopulateAccountSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Test Group',
                'members': [{'account_id': 'acc_123', 'username': 'testuser'}]
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.get_group(group_id, mock_request)
        
        # Assert
        self.mock_group_repo.get.assert_called_once_with(group_id)
        self.mock_group_repo.get_members.assert_called_once_with(group_id)
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)
        self.assertIn('members', result)

    def test_get_all_groups_by_account_success_without_members(self):
        """Test getting all groups by account without populating members"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.GET = {}  # No populate_members parameter
        mock_request.headers = {}
        
        groups = [self.sample_group]
        self.mock_account_repo.get.return_value = self.sample_account
        self.mock_group_repo.get_by_creator.return_value = groups
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{'group_id': 'group_123', 'name': 'Test Group'}]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.get_all_groups_by_account(account_id, mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        self.mock_group_repo.get_by_creator.assert_called_once_with(account_id)
        self.mock_group_repo.get_members.assert_not_called()
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('groups', result)
        self.assertIsInstance(result['groups'], list)

    def test_get_all_groups_by_account_success_with_members(self):
        """Test getting all groups by account with populating members"""
        # Arrange
        account_id = 'acc_123'
        mock_request = Mock()
        mock_request.GET = {'populate_members': 'true'}
        mock_request.headers = {}
        
        groups = [self.sample_group]
        members = [self.sample_group_member]
        
        self.mock_account_repo.get.return_value = self.sample_account
        self.mock_group_repo.get_by_creator.return_value = groups
        self.mock_group_repo.get_members.return_value = members
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupPopulateGroupMemberPopulateAccountSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = [{
                'group_id': 'group_123',
                'name': 'Test Group',
                'members': [{'account_id': 'acc_123', 'username': 'testuser'}]
            }]
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.get_all_groups_by_account(account_id, mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        self.mock_group_repo.get_by_creator.assert_called_once_with(account_id)
        self.mock_group_repo.get_members.assert_called_once_with('group_123')
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('groups', result)
        self.assertIsInstance(result['groups'], list)

    def test_get_all_groups_by_account_account_not_found(self):
        """Test getting all groups when account doesn't exist"""
        # Arrange
        account_id = 'nonexistent'
        mock_request = Mock()
        mock_request.GET = {}
        mock_request.headers = {}
        
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Account.DoesNotExist):
            self.group_service.get_all_groups_by_account(account_id, mock_request)
        
        self.mock_account_repo.get.assert_called_once_with(account_id)

    def test_update_group_success(self):
        """Test successful group update"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.data = {
            'name': 'Updated Group',
            'description': 'Updated Description'
        }
        
        updated_group = Mock(spec=Group)
        updated_group.group_id = group_id
        updated_group.name = 'Updated Group'
        
        self.mock_group_repo.update.return_value = updated_group
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Updated Group'
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.update_group(group_id, mock_request)
        
        # Assert
        self.mock_group_repo.update.assert_called_once_with(group_id, {
            'name': 'Updated Group',
            'description': 'Updated Description'
        })
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)

    def test_add_members_to_group_success(self):
        """Test adding members to group"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.data = {
            'account_ids': ['acc_123', 'acc_456']
        }
        
        account1 = Mock(spec=Account)
        account1.account_id = 'acc_123'
        account2 = Mock(spec=Account)
        account2.account_id = 'acc_456'
        
        self.mock_group_repo.get.return_value = self.sample_group
        self.mock_account_repo.get.side_effect = [account1, account2]
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupPopulateGroupMemberPopulateAccountSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Test Group',
                'members': [
                    {'account_id': 'acc_123', 'username': 'user1'},
                    {'account_id': 'acc_456', 'username': 'user2'}
                ]
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.add_members_to_group(group_id, mock_request)
        
        # Assert
        self.mock_group_repo.get.assert_called_once_with(group_id)
        self.mock_account_repo.get.assert_any_call('acc_123')
        self.mock_account_repo.get.assert_any_call('acc_456')
        self.mock_group_repo.bulk_create_members.assert_called_once()
        
        # Verify that GroupMember objects were created correctly
        call_args = self.mock_group_repo.bulk_create_members.call_args[0][0]
        self.assertEqual(len(call_args), 2)
        self.assertEqual(call_args[0].group_id, group_id)
        self.assertEqual(call_args[0].account_id, 'acc_123')
        self.assertEqual(call_args[1].group_id, group_id)
        self.assertEqual(call_args[1].account_id, 'acc_456')
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)
        self.assertIn('members', result)

    def test_add_members_to_group_account_not_found(self):
        """Test adding members when account doesn't exist"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.data = {
            'account_ids': ['nonexistent']
        }
        
        self.mock_group_repo.get.return_value = self.sample_group
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(Account.DoesNotExist):
            self.group_service.add_members_to_group(group_id, mock_request)
        
        self.mock_group_repo.get.assert_called_once_with(group_id)
        self.mock_account_repo.get.assert_called_once_with('nonexistent')

    def test_update_members_to_group_success(self):
        """Test updating members in group"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.data = {
            'account_ids': ['acc_123', 'acc_456']
        }
        
        account1 = Mock(spec=Account)
        account1.account_id = 'acc_123'
        account2 = Mock(spec=Account)
        account2.account_id = 'acc_456'
        
        self.mock_group_repo.get.return_value = self.sample_group
        self.mock_account_repo.get.side_effect = [account1, account2]
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupPopulateGroupMemberPopulateAccountSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Test Group',
                'members': [
                    {'account_id': 'acc_123', 'username': 'user1'},
                    {'account_id': 'acc_456', 'username': 'user2'}
                ]
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.update_members_to_group(group_id, mock_request)
        
        # Assert
        self.mock_group_repo.get.assert_called_once_with(group_id)
        self.mock_group_repo.delete_members.assert_called_once_with(group_id)
        self.mock_account_repo.get.assert_any_call('acc_123')
        self.mock_account_repo.get.assert_any_call('acc_456')
        self.mock_group_repo.bulk_create_members.assert_called_once()
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)
        self.assertIn('members', result)

    def test_update_members_to_group_empty_list(self):
        """Test updating members with empty list (should remove all members)"""
        # Arrange
        group_id = 'group_123'
        mock_request = Mock()
        mock_request.data = {
            'account_ids': []
        }
        
        self.mock_group_repo.get.return_value = self.sample_group
        
        # Mock serializer
        with patch('api.services.group.group_service.GroupPopulateGroupMemberPopulateAccountSecureSerializer') as mock_serializer:
            mock_serializer_instance = Mock()
            mock_serializer_instance.data = {
                'group_id': 'group_123',
                'name': 'Test Group',
                'members': []
            }
            mock_serializer.return_value = mock_serializer_instance
            
            # Act
            result = self.group_service.update_members_to_group(group_id, mock_request)
        
        # Assert
        self.mock_group_repo.get.assert_called_once_with(group_id)
        self.mock_group_repo.delete_members.assert_called_once_with(group_id)
        self.mock_account_repo.get.assert_not_called()
        self.mock_group_repo.bulk_create_members.assert_called_once_with([])
        
        # Verify result
        self.assertIsInstance(result, dict)
        self.assertIn('group_id', result)

    def test_service_initialization(self):
        """Test that service initializes correctly with repositories"""
        # Arrange & Act
        service = GroupService(
            group_repo=self.mock_group_repo,
            account_repo=self.mock_account_repo
        )
        
        # Assert
        self.assertEqual(service.group_repo, self.mock_group_repo)
        self.assertEqual(service.account_repo, self.mock_account_repo)


if __name__ == '__main__':
    unittest.main()
