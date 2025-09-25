import unittest
from unittest.mock import Mock, patch, MagicMock
from django.test import TestCase
from django.http import HttpRequest
from api.services.auth.auth_service import AuthServiceImpl
from api.repositories.account_repository import AccountRepository
from api.models import Account
from api.errors.common import *
from api.errors.auth import IncorrectPasswordError
from time import time
from uuid import uuid4


class TestAuthService(TestCase):
    """Unit tests for AuthService"""

    def setUp(self):
        """Set up test fixtures"""
        self.mock_account_repo = Mock(spec=AccountRepository)
        self.mock_config = Mock()
        self.mock_config.token_lifetime = 3600  # 1 hour
        
        self.auth_service = AuthServiceImpl(
            config=self.mock_config,
            account_repo=self.mock_account_repo
        )
        
        # Sample account data
        self.sample_account = Mock(spec=Account)
        self.sample_account.account_id = 'acc_123'
        self.sample_account.username = 'testuser'
        self.sample_account.email = 'test@example.com'
        self.sample_account.password = 'encrypted_password'
        self.sample_account.token = 'valid_token'
        self.sample_account.token_expire = int(time()) + 3600  # 1 hour from now
        
        # Sample account dict (as returned by model_to_dict)
        self.sample_account_dict = {
            'account_id': 'acc_123',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'encrypted_password',
            'token': 'valid_token',
            'token_expire': int(time()) + 3600
        }

    @patch('api.services.auth.auth_service.model_to_dict')
    def test_verify_token_success(self, mock_model_to_dict):
        """Test successful token verification"""
        # Arrange
        token = 'valid_token'
        self.mock_account_repo.get_by_token.return_value = self.sample_account
        mock_model_to_dict.return_value = self.sample_account_dict
        
        # Act
        result = self.auth_service.verify_token(token)
        
        # Assert
        self.mock_account_repo.get_by_token.assert_called_once_with(token)
        mock_model_to_dict.assert_called_once_with(self.sample_account)
        self.assertTrue(result)

    @patch('api.services.auth.auth_service.model_to_dict')
    def test_verify_token_expired(self, mock_model_to_dict):
        """Test token verification with expired token"""
        # Arrange
        token = 'expired_token'
        expired_account_dict = self.sample_account_dict.copy()
        expired_account_dict['token_expire'] = int(time()) - 3600  # 1 hour ago
        
        self.mock_account_repo.get_by_token.return_value = self.sample_account
        mock_model_to_dict.return_value = expired_account_dict
        
        # Act
        result = self.auth_service.verify_token(token)
        
        # Assert
        self.mock_account_repo.get_by_token.assert_called_once_with(token)
        self.assertFalse(result)

    def test_verify_token_account_not_found(self):
        """Test token verification when account doesn't exist"""
        # Arrange
        token = 'invalid_token'
        self.mock_account_repo.get_by_token.side_effect = Account.DoesNotExist()
        
        # Act
        result = self.auth_service.verify_token(token)
        
        # Assert
        self.mock_account_repo.get_by_token.assert_called_once_with(token)
        self.assertFalse(result)

    def test_get_account_by_token_success(self):
        """Test successful account retrieval by token"""
        # Arrange
        token = 'valid_token'
        self.mock_account_repo.get_by_token.return_value = self.sample_account
        
        # Act
        result = self.auth_service.getAccountByToken(token)
        
        # Assert
        self.mock_account_repo.get_by_token.assert_called_once_with(token)
        self.assertEqual(result, self.sample_account)

    def test_get_account_by_token_expired(self):
        """Test account retrieval with expired token"""
        # Arrange
        token = 'expired_token'
        expired_account = Mock(spec=Account)
        expired_account.token_expire = int(time()) - 3600  # 1 hour ago
        self.mock_account_repo.get_by_token.return_value = expired_account
        
        # Act & Assert
        with self.assertRaises(InvalidTokenError):
            self.auth_service.getAccountByToken(token)
        
        self.mock_account_repo.get_by_token.assert_called_once_with(token)

    def test_get_account_by_token_not_found(self):
        """Test account retrieval when account doesn't exist"""
        # Arrange
        token = 'invalid_token'
        self.mock_account_repo.get_by_token.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(InvalidTokenError):
            self.auth_service.getAccountByToken(token)
        
        self.mock_account_repo.get_by_token.assert_called_once_with(token)

    @patch('api.services.auth.auth_service.passwordEncryption')
    @patch('api.services.auth.auth_service.model_to_dict')
    @patch('api.services.auth.auth_service.uuid4')
    @patch('api.services.auth.auth_service.time')
    def test_login_success(self, mock_time, mock_uuid4, mock_model_to_dict, mock_password_encryption):
        """Test successful login"""
        # Arrange
        mock_time.return_value = 1000
        mock_uuid4.return_value.hex = 'new_token_hex'
        mock_password_encryption.return_value = 'encrypted_password'
        
        mock_request = Mock()
        mock_request.data = {
            'username': 'testuser',
            'password': 'plaintext_password'
        }
        
        self.mock_account_repo.get_by_username.return_value = self.sample_account
        mock_model_to_dict.return_value = self.sample_account_dict
        
        # Act
        result = self.auth_service.login(mock_request)
        
        # Assert
        self.mock_account_repo.get_by_username.assert_called_once_with('testuser')
        mock_password_encryption.assert_called_once_with('plaintext_password')
        mock_model_to_dict.assert_called_once_with(self.sample_account)
        
        # Verify token was set
        self.assertEqual(self.sample_account.token, 'new_token_hex')
        self.assertEqual(self.sample_account.token_expire, 1000 + self.mock_config.token_lifetime)
        self.sample_account.save.assert_called_once()
        
        # Verify result
        self.assertEqual(result, self.sample_account_dict)

    @patch('api.services.auth.auth_service.passwordEncryption')
    def test_login_incorrect_password(self, mock_password_encryption):
        """Test login with incorrect password"""
        # Arrange
        mock_password_encryption.return_value = 'wrong_password'
        
        mock_request = Mock()
        mock_request.data = {
            'username': 'testuser',
            'password': 'wrong_password'
        }
        
        self.mock_account_repo.get_by_username.return_value = self.sample_account
        
        # Act & Assert
        with self.assertRaises(IncorrectPasswordError):
            self.auth_service.login(mock_request)
        
        self.mock_account_repo.get_by_username.assert_called_once_with('testuser')
        mock_password_encryption.assert_called_once_with('wrong_password')

    def test_login_user_not_found(self):
        """Test login when user doesn't exist"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'username': 'nonexistent',
            'password': 'password'
        }
        
        self.mock_account_repo.get_by_username.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(ItemNotFoundError) as context:
            self.auth_service.login(mock_request)
        
        self.assertEqual(str(context.exception), "User not found.")
        self.mock_account_repo.get_by_username.assert_called_once_with('nonexistent')

    @patch('api.services.auth.auth_service.model_to_dict')
    @patch('api.services.auth.auth_service.time')
    def test_authorization_success(self, mock_time, mock_model_to_dict):
        """Test successful authorization"""
        # Arrange
        mock_time.return_value = 1000
        mock_model_to_dict.return_value = self.sample_account_dict
        
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Act
        result = self.auth_service.authorization(mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with('acc_123')
        mock_model_to_dict.assert_called_once_with(self.sample_account)
        self.assertEqual(result, {'result': True})

    @patch('api.services.auth.auth_service.model_to_dict')
    @patch('api.services.auth.auth_service.time')
    def test_authorization_expired_token(self, mock_time, mock_model_to_dict):
        """Test authorization with expired token"""
        # Arrange
        mock_time.return_value = 1000
        expired_account_dict = self.sample_account_dict.copy()
        expired_account_dict['token_expire'] = 500  # Expired
        
        mock_model_to_dict.return_value = expired_account_dict
        
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Act
        result = self.auth_service.authorization(mock_request)
        
        # Assert
        self.assertEqual(result, {'result': False})

    @patch('api.services.auth.auth_service.model_to_dict')
    @patch('api.services.auth.auth_service.time')
    def test_authorization_wrong_token(self, mock_time, mock_model_to_dict):
        """Test authorization with wrong token"""
        # Arrange
        mock_time.return_value = 1000
        mock_model_to_dict.return_value = self.sample_account_dict
        
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'wrong_token'
        }
        
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Act
        result = self.auth_service.authorization(mock_request)
        
        # Assert
        self.assertEqual(result, {'result': False})

    def test_authorization_account_not_found(self):
        """Test authorization when account doesn't exist"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'nonexistent',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act
        result = self.auth_service.authorization(mock_request)
        
        # Assert
        self.assertEqual(result, {'result': False})

    @patch('api.services.auth.auth_service.model_to_dict')
    def test_logout_success(self, mock_model_to_dict):
        """Test successful logout"""
        # Arrange
        mock_model_to_dict.return_value = self.sample_account_dict
        
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Act
        result = self.auth_service.logout(mock_request)
        
        # Assert
        self.mock_account_repo.get.assert_called_once_with('acc_123')
        self.assertIsNone(self.sample_account.token)
        self.sample_account.save.assert_called_once()
        mock_model_to_dict.assert_called_once_with(self.sample_account)
        
        # Verify result is a Response object
        from rest_framework.response import Response
        self.assertIsInstance(result, Response)
        self.assertEqual(result.status_code, 200)

    def test_logout_wrong_token(self):
        """Test logout with wrong token"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'wrong_token'
        }
        
        self.mock_account_repo.get.return_value = self.sample_account
        
        # Act & Assert
        with self.assertRaises(InvalidTokenError):
            self.auth_service.logout(mock_request)
        
        self.mock_account_repo.get.assert_called_once_with('acc_123')

    def test_logout_account_not_found(self):
        """Test logout when account doesn't exist"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'nonexistent',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.side_effect = Account.DoesNotExist()
        
        # Act & Assert
        with self.assertRaises(ItemNotFoundError) as context:
            self.auth_service.logout(mock_request)
        
        self.assertEqual(str(context.exception), "User not found.")
        self.mock_account_repo.get.assert_called_once_with('nonexistent')

    def test_service_initialization(self):
        """Test that service initializes correctly with dependencies"""
        # Arrange & Act
        service = AuthServiceImpl(self.mock_config, self.mock_account_repo)
        
        # Assert
        self.assertEqual(service.config, self.mock_config)
        self.assertEqual(service.account_repo, self.mock_account_repo)

    @patch('api.services.auth.auth_service.model_to_dict')
    def test_verify_token_repository_exception(self, mock_model_to_dict):
        """Test token verification when repository raises unexpected exception"""
        # Arrange
        token = 'valid_token'
        self.mock_account_repo.get_by_token.side_effect = Exception("Database error")
        
        # Act
        result = self.auth_service.verify_token(token)
        
        # Assert
        self.assertFalse(result)

    def test_get_account_by_token_repository_exception(self):
        """Test account retrieval when repository raises unexpected exception"""
        # Arrange
        token = 'valid_token'
        self.mock_account_repo.get_by_token.side_effect = Exception("Database error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.auth_service.getAccountByToken(token)

    @patch('api.services.auth.auth_service.passwordEncryption')
    def test_login_repository_exception(self, mock_password_encryption):
        """Test login when repository raises unexpected exception"""
        # Arrange
        mock_password_encryption.return_value = 'encrypted_password'
        
        mock_request = Mock()
        mock_request.data = {
            'username': 'testuser',
            'password': 'password'
        }
        
        self.mock_account_repo.get_by_username.side_effect = Exception("Database error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.auth_service.login(mock_request)

    def test_authorization_repository_exception(self):
        """Test authorization when repository raises unexpected exception"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.side_effect = Exception("Database error")
        
        # Act
        result = self.auth_service.authorization(mock_request)
        
        # Assert
        self.assertEqual(result, {'result': False})

    def test_logout_repository_exception(self):
        """Test logout when repository raises unexpected exception"""
        # Arrange
        mock_request = Mock()
        mock_request.data = {
            'account_id': 'acc_123',
            'token': 'valid_token'
        }
        
        self.mock_account_repo.get.side_effect = Exception("Database error")
        
        # Act & Assert
        with self.assertRaises(Exception):
            self.auth_service.logout(mock_request)


class TestAuthServiceIntegration(unittest.TestCase):
    """Integration tests for AuthService with real repositories"""

    def setUp(self):
        """Set up integration test fixtures"""
        from api.repositories.account_repository import AccountRepositoryImpl
        from api.config import Configuration
        from decouple import AutoConfig
        
        try:
            config = Configuration(AutoConfig())
        except Exception:
            # Fallback configuration
            class FallbackConfig:
                def __init__(self):
                    self.token_lifetime = 3600
            config = FallbackConfig()
        
        self.real_account_repo = AccountRepositoryImpl()
        self.auth_service = AuthServiceImpl(config, self.real_account_repo)

    def test_integration_login_flow(self):
        """Integration test for complete login flow"""
        # This test would require a real database connection
        # For now, we'll skip it in unit tests
        self.skipTest("Integration test requires database setup")

    def test_integration_token_verification(self):
        """Integration test for token verification"""
        # This test would require a real database connection
        # For now, we'll skip it in unit tests
        self.skipTest("Integration test requires database setup")


class TestAuthServiceModuleFunctions(unittest.TestCase):
    """Tests for module-level functions in auth_service.py"""

    @patch('api.services.auth.auth_service._get_auth_service')
    def test_verify_token_function(self, mock_get_auth_service):
        """Test the module-level verify_token function"""
        # Arrange
        mock_auth_service = Mock()
        mock_auth_service.verify_token.return_value = True
        mock_get_auth_service.return_value = mock_auth_service
        
        from api.services.auth.auth_service import verify_token
        
        # Act
        result = verify_token('test_token')
        
        # Assert
        mock_get_auth_service.assert_called_once()
        mock_auth_service.verify_token.assert_called_once_with('test_token')
        self.assertTrue(result)

    @patch('api.services.auth.auth_service._get_auth_service')
    def test_get_account_by_token_function(self, mock_get_auth_service):
        """Test the module-level getAccountByToken function"""
        # Arrange
        mock_auth_service = Mock()
        mock_account = Mock()
        mock_auth_service.getAccountByToken.return_value = mock_account
        mock_get_auth_service.return_value = mock_auth_service
        
        from api.services.auth.auth_service import getAccountByToken
        
        # Act
        result = getAccountByToken('test_token')
        
        # Assert
        mock_get_auth_service.assert_called_once()
        mock_auth_service.getAccountByToken.assert_called_once_with('test_token')
        self.assertEqual(result, mock_account)


if __name__ == '__main__':
    unittest.main()
