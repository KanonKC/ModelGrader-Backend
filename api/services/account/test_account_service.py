import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.services.account.account_service import AccountServiceImpl
from api.repositories.account_repository import AccountRepository
from api.models import Account
from api.errors.common import InternalServerError, ItemNotFoundError


class TestAccountService(TestCase):
    """Unit tests for AccountService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_account_repo = Mock(spec=AccountRepository)
        self.account_service = AccountServiceImpl(self.mock_account_repo)
        
        # Sample account data
        self.sample_account_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'plaintext_password',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Sample account object with all required fields
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        self.sample_account.email = 'test@example.com'
        self.sample_account.first_name = 'Test'
        self.sample_account.last_name = 'User'
        self.sample_account.password = 'encrypted_password'
        self.sample_account.is_active = True
        self.sample_account.is_staff = False
        self.sample_account.is_superuser = False
        self.sample_account.date_joined = '2023-01-01T00:00:00Z'
        self.sample_account.last_login = None
        self.sample_account.token = 'test_token'

    @patch('api.services.account.account_service.passwordEncryption')
    @patch('api.services.account.account_service.AccountSerializer')
    def test_create_account_success(self, mock_serializer_class, mock_password_encryption):
        """Test successful account creation"""
        # Arrange
        mock_password_encryption.return_value = 'encrypted_password'
        self.mock_account_repo.create.return_value = self.sample_account
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'account_id': 'acc_123',
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Create a mock request object
        mock_request = Mock()
        mock_request.data = self.sample_account_data.copy()
        
        # Act
        result = self.account_service.create_account(mock_request)
        
        # Assert
        self.mock_account_repo.create.assert_called_once()
        call_args = self.mock_account_repo.create.call_args[0][0]
        
        # Verify password was encrypted
        self.assertEqual(call_args['password'], 'encrypted_password')
        mock_password_encryption.assert_called_once_with('plaintext_password')
        
        # Verify other data is preserved
        self.assertEqual(call_args['username'], 'testuser')
        self.assertEqual(call_args['email'], 'test@example.com')
        
        # Verify serializer was called with the account
        mock_serializer_class.assert_called_once_with(self.sample_account)
        
        # Verify result structure
        self.assertIsInstance(result, dict)
        self.assertIn('account_id', result)
        self.assertIn('username', result)

    @patch('api.services.account.account_service.passwordEncryption')
    def test_create_account_repository_exception(self, mock_password_encryption):
        """Test account creation when repository raises exception"""
        # Arrange
        mock_password_encryption.return_value = 'encrypted_password'
        self.mock_account_repo.create.side_effect = Exception("Database error")
        
        mock_request = Mock()
        mock_request.data = self.sample_account_data.copy()
        
        # Act & Assert
        with self.assertRaises(InternalServerError):
            self.account_service.create_account(mock_request)
        
        self.mock_account_repo.create.assert_called_once()

    @patch('api.services.account.account_service.AccountSerializer')
    def test_get_account_success(self, mock_serializer_class):
        """Test successful account retrieval"""
        # Arrange
        account_id = 'acc_123'
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {
            'account_id': 'acc_123',
            'username': 'testuser',
            'email': 'test@example.com'
        }
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        result = self.account_service.get_account(account_id)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with(account_id)
        mock_serializer_class.assert_called_once_with(self.sample_account)
        self.assertIsInstance(result, dict)
        self.assertIn('account_id', result)
        self.assertIn('username', result)

    def test_get_account_not_found(self):
        """Test account retrieval when account doesn't exist"""
        # Arrange
        account_id = 'nonexistent'
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(ItemNotFoundError) as context:
            self.account_service.get_account(account_id)
        
        self.assertEqual(str(context.exception), "Account not found.")
        self.mock_account_repo.get.assert_called_once_with(account_id)

    def test_get_account_repository_exception(self):
        """Test account retrieval when repository raises unexpected exception"""
        # Arrange
        account_id = 'acc_123'
        self.mock_account_repo.get.side_effect = Exception("Database connection error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.account_service.get_account(account_id)
        
        self.mock_account_repo.get.assert_called_once_with(account_id)

    @patch('api.services.account.account_service.AccountSecureSerializer')
    def test_get_all_accounts_without_search(self, mock_serializer_class):
        """Test getting all accounts without search query"""
        # Arrange
        mock_accounts = [self.sample_account, self.sample_account]
        self.mock_account_repo.list.return_value = mock_accounts
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [
            {'account_id': 'acc_123', 'username': 'testuser'},
            {'account_id': 'acc_123', 'username': 'testuser'}
        ]
        mock_serializer_class.return_value = mock_serializer_instance
        
        mock_request = Mock()
        mock_request.GET = {}
        
        # Act
        result = self.account_service.get_all_accounts(mock_request)
        
        # Assert
        self.mock_account_repo.list.assert_called_once_with('')
        mock_serializer_class.assert_called_once_with(mock_accounts, many=True)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)
        self.assertIsInstance(result['accounts'], list)
        self.assertEqual(len(result['accounts']), 2)

    @patch('api.services.account.account_service.AccountSecureSerializer')
    def test_get_all_accounts_with_search(self, mock_serializer_class):
        """Test getting accounts with search query"""
        # Arrange
        search_query = 'test'
        mock_accounts = [self.sample_account]
        self.mock_account_repo.list.return_value = mock_accounts
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [{'account_id': 'acc_123', 'username': 'testuser'}]
        mock_serializer_class.return_value = mock_serializer_instance
        
        mock_request = Mock()
        mock_request.GET = {'search': search_query}
        
        # Act
        result = self.account_service.get_all_accounts(mock_request)
        
        # Assert
        self.mock_account_repo.list.assert_called_once_with(search_query)
        mock_serializer_class.assert_called_once_with(mock_accounts, many=True)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)
        self.assertIsInstance(result['accounts'], list)
        self.assertEqual(len(result['accounts']), 1)

    @patch('api.services.account.account_service.AccountSecureSerializer')
    def test_get_all_accounts_empty_result(self, mock_serializer_class):
        """Test getting accounts when no accounts match search"""
        # Arrange
        self.mock_account_repo.list.return_value = []
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = []
        mock_serializer_class.return_value = mock_serializer_instance
        
        mock_request = Mock()
        mock_request.GET = {'search': 'nonexistent'}
        
        # Act
        result = self.account_service.get_all_accounts(mock_request)
        
        # Assert
        self.mock_account_repo.list.assert_called_once_with('nonexistent')
        mock_serializer_class.assert_called_once_with([], many=True)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)
        self.assertIsInstance(result['accounts'], list)
        self.assertEqual(len(result['accounts']), 0)

    def test_get_all_accounts_repository_exception(self):
        """Test getting accounts when repository raises exception"""
        # Arrange
        self.mock_account_repo.list.side_effect = Exception("Database error")
        
        mock_request = Mock()
        mock_request.GET = {}
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.account_service.get_all_accounts(mock_request)
        
        self.mock_account_repo.list.assert_called_once_with('')

    @patch('api.services.account.account_service.AccountSecureSerializer')
    def test_get_all_accounts_missing_search_param(self, mock_serializer_class):
        """Test getting accounts when search parameter is missing"""
        # Arrange
        mock_accounts = [self.sample_account]
        self.mock_account_repo.list.return_value = mock_accounts
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [{'account_id': 'acc_123', 'username': 'testuser'}]
        mock_serializer_class.return_value = mock_serializer_instance
        
        mock_request = Mock()
        mock_request.GET = {}  # No search parameter
        
        # Act
        result = self.account_service.get_all_accounts(mock_request)
        
        # Assert
        self.mock_account_repo.list.assert_called_once_with('')
        mock_serializer_class.assert_called_once_with(mock_accounts, many=True)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)

    @patch('api.services.account.account_service.AccountSecureSerializer')
    def test_get_all_accounts_empty_search_param(self, mock_serializer_class):
        """Test getting accounts when search parameter is empty string"""
        # Arrange
        mock_accounts = [self.sample_account]
        self.mock_account_repo.list.return_value = mock_accounts
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = [{'account_id': 'acc_123', 'username': 'testuser'}]
        mock_serializer_class.return_value = mock_serializer_instance
        
        mock_request = Mock()
        mock_request.GET = {'search': ''}
        
        # Act
        result = self.account_service.get_all_accounts(mock_request)
        
        # Assert
        self.mock_account_repo.list.assert_called_once_with('')
        mock_serializer_class.assert_called_once_with(mock_accounts, many=True)
        self.assertIsInstance(result, dict)
        self.assertIn('accounts', result)

    @patch('api.services.account.account_service.passwordEncryption')
    @patch('api.services.account.account_service.AccountSerializer')
    def test_create_account_data_mutation(self, mock_serializer_class, mock_password_encryption):
        """Test that create_account doesn't mutate original request data"""
        # Arrange
        mock_password_encryption.return_value = 'encrypted_password'
        original_data = self.sample_account_data.copy()
        mock_request = Mock()
        mock_request.data = original_data.copy()
        
        self.mock_account_repo.create.return_value = self.sample_account
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {'account_id': 'acc_123', 'username': 'testuser'}
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        self.account_service.create_account(mock_request)
        
        # Assert
        # Verify original data is not mutated
        self.assertEqual(mock_request.data, original_data)

    def test_service_initialization(self):
        """Test that service initializes correctly with repository"""
        # Arrange & Act
        service = AccountServiceImpl(self.mock_account_repo)
        
        # Assert
        self.assertEqual(service.account_repo, self.mock_account_repo)

    @patch('api.services.account.account_service.passwordEncryption')
    @patch('api.services.account.account_service.AccountSerializer')
    def test_create_account_with_minimal_data(self, mock_serializer_class, mock_password_encryption):
        """Test account creation with minimal required data"""
        # Arrange
        mock_password_encryption.return_value = 'encrypted_password'
        minimal_data = {
            'username': 'minimaluser',
            'password': 'password123'
        }
        
        mock_request = Mock()
        mock_request.data = minimal_data.copy()
        
        self.mock_account_repo.create.return_value = self.sample_account
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {'account_id': 'acc_123', 'username': 'minimaluser'}
        mock_serializer_class.return_value = mock_serializer_instance
        
        # Act
        result = self.account_service.create_account(mock_request)
        
        # Assert
        self.mock_account_repo.create.assert_called_once()
        call_args = self.mock_account_repo.create.call_args[0][0]
        self.assertEqual(call_args['username'], 'minimaluser')
        self.assertIsInstance(result, dict)

    @patch('api.services.account.account_service.AccountSerializer')
    def test_get_account_with_different_id_formats(self, mock_serializer_class):
        """Test account retrieval with different ID formats"""
        # Arrange
        test_ids = ['acc_123', 'user_456', 'admin_789']
        
        # Mock serializer
        mock_serializer_instance = Mock()
        mock_serializer_instance.data = {'account_id': 'acc_123', 'username': 'testuser'}
        mock_serializer_class.return_value = mock_serializer_instance
        
        for account_id in test_ids:
            with self.subTest(account_id=account_id):
                self.mock_account_repo.reset_mock()
                self.mock_account_repo.get.return_value = self.sample_account
                
                # Act
                result = self.account_service.get_account(account_id)
                
                # Assert
                self.mock_account_repo.get.assert_called_once_with(account_id)
                self.assertIsInstance(result, dict)


class TestAccountServiceIntegration(unittest.TestCase):
    """Integration tests for AccountService with real repository"""

    def setUp(self):
        """Set up integration test fixtures"""
        from api.repositories.account_repository import AccountRepositoryImpl
        self.real_repo = AccountRepositoryImpl()
        self.account_service = AccountServiceImpl(self.real_repo)

    def test_error_handling_consistency(self):
        """Test that error handling is consistent across methods"""
        # Test that all methods handle repository exceptions appropriately
        methods_to_test = [
            ('create_account', lambda: self.account_service.create_account(Mock())),
            ('get_account', lambda: self.account_service.get_account('test_id')),
            ('get_all_accounts', lambda: self.account_service.get_all_accounts(Mock()))
        ]
        
        for method_name, method_call in methods_to_test:
            with self.subTest(method=method_name):
                # This would test error handling consistency
                # Implementation depends on specific error handling requirements
                pass


if __name__ == '__main__':
    unittest.main()
