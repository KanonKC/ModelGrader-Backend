from django.forms.models import model_to_dict
from time import time
from api.config import Configuration
from api.errors.auth import IncorrectPasswordError
from api.models import Account
from api.repositories.account_repository import AccountRepository, AccountRepositoryImpl
from api.errors.common import *
from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework import status
from uuid import uuid4
from abc import ABC, abstractmethod
from decouple import AutoConfig

class AuthService(ABC):
    @abstractmethod
    def verify_token(self,token):
        pass
    @abstractmethod
    def getAccountByToken(self,token):
        pass
    @abstractmethod
    def login(self,request):
        pass
    @abstractmethod
    def authorization(self,request):
        pass
    @abstractmethod
    def logout(self,request):
        pass

class AuthServiceImpl:

    def __init__(self, config: Configuration, account_repo: AccountRepository):
        self.config = config
        self.account_repo = account_repo

    def verify_token(self,token):
        """
        Check if user has valid token and not expired
        Return: True/False
        """
        try:
            account = self.account_repo.get_by_token(token)
            account_dict = model_to_dict(account)
            if account_dict['token_expire'] >= time():
                return True
            else:
                return False
        except:
            return False
        
    def getAccountByToken(self,token):
        """
        Get account from token
        Return: account object
        """
        try:
            account = self.account_repo.get_by_token(token)
            if account.token_expire < time():
                raise InvalidTokenError()
            return account
        except Account.DoesNotExist:
            raise InvalidTokenError()
        except Exception as e:
            raise e

    def login(self,request):
        try:
            account = self.account_repo.get_by_username(request.data['username'])
            if passwordEncryption(request.data['password']) == account.password:
                account.token = uuid4().hex
                account.token_expire = int(time() + self.config.token_lifetime)
                account.save()
                return model_to_dict(account)
            else:
                raise IncorrectPasswordError()
        except Account.DoesNotExist:
            raise ItemNotFoundError("User")

    def authorization(self,request):
        try:
            account = self.account_repo.get(request.data['account_id'])
            account_dict = model_to_dict(account)
            if account_dict['token_expire'] >= time() and account_dict['token'] == request.data['token']:
                return {'result': True}
            return {'result': False}
        except Account.DoesNotExist:
            return {'result': False}

    def logout(self,request):
        try:
            account = self.account_repo.get(request.data['account_id'])
            if account.token == request.data['token']:
                account.token = None
                account.save()
                return Response(model_to_dict(account), status=status.HTTP_200_OK)
            else:
                raise InvalidTokenError()
        except Account.DoesNotExist:
            raise ItemNotFoundError("User")

# Module-level functions for backward compatibility
# These provide the function-based interface expected by existing code

def _get_auth_service():
    """Get a configured auth service instance"""
    try:
        config = Configuration(AutoConfig())
        account_repo = AccountRepositoryImpl()
        return AuthServiceImpl(config, account_repo)
    except Exception:
        # Fallback configuration if decouple is not available
        class FallbackConfig:
            def __init__(self):
                self.token_lifetime = 3600  # 1 hour default
        
        account_repo = AccountRepositoryImpl()
        return AuthServiceImpl(FallbackConfig(), account_repo)

def verify_token(token):
    """
    Check if user has valid token and not expired
    Return: True/False
    """
    auth_service = _get_auth_service()
    return auth_service.verify_token(token)

def getAccountByToken(token):
    """
    Get account from token
    Return: account object
    """
    auth_service = _get_auth_service()
    return auth_service.getAccountByToken(token)
