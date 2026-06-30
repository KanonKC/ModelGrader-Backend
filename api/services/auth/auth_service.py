from django.forms.models import model_to_dict
from api.config import Configuration
from api.errors.auth import IncorrectPasswordError
from api.models import Account
from api.repositories.account_repository import AccountRepository, AccountRepositoryImpl
from api.errors.common import *
from api.utility import passwordEncryption
from api.services.auth.jwt_service import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
    verify_refresh_token,
)

from abc import ABC, abstractmethod
from decouple import AutoConfig


def _build_token_response(account: Account) -> dict:
    account_data = model_to_dict(account)
    account_data.pop("password", None)
    account_data.pop("token", None)
    account_data.pop("token_expire", None)
    return {
        "access_token": create_access_token(account.account_id),
        "refresh_token": create_refresh_token(account.account_id),
        "account_id": account.account_id,
        "username": account.username,
        "email": account.email,
    }


class AuthService(ABC):
    @abstractmethod
    def verify_token(self, token): pass

    @abstractmethod
    def getAccountByToken(self, token): pass

    @abstractmethod
    def login(self, request): pass

    @abstractmethod
    def refresh(self, request): pass

    @abstractmethod
    def logout(self, request): pass


class AuthServiceImpl:

    def __init__(self, config: Configuration, account_repo: AccountRepository):
        self.config = config
        self.account_repo = account_repo

    def verify_token(self, token) -> bool:
        try:
            verify_access_token(token)
            return True
        except Exception:
            return False

    def getAccountByToken(self, token) -> Account:
        try:
            account_id = verify_access_token(token)
            return self.account_repo.get(account_id)
        except Account.DoesNotExist:
            raise InvalidTokenError()
        except Exception:
            raise InvalidTokenError()

    def login(self, request) -> dict:
        try:
            account = self.account_repo.get_by_username(request.data["username"])
            if passwordEncryption(request.data["password"]) == account.password:
                return _build_token_response(account)
            else:
                raise IncorrectPasswordError()
        except Account.DoesNotExist:
            raise ItemNotFoundError("User")

    def refresh(self, request) -> dict:
        try:
            refresh_token = request.data.get("refresh_token")
            if not refresh_token:
                raise InvalidTokenError()
            account_id = verify_refresh_token(refresh_token)
            account = self.account_repo.get(account_id)
            return {"access_token": create_access_token(account.account_id)}
        except Account.DoesNotExist:
            raise InvalidTokenError()
        except Exception:
            raise InvalidTokenError()

    def authorization(self, request) -> dict:
        try:
            token = request.data.get("token") or request.data.get("access_token")
            if not token:
                return {"result": False}
            account_id = verify_access_token(token)
            self.account_repo.get(account_id)
            return {"result": True}
        except Exception:
            return {"result": False}

    def logout(self, request) -> dict:
        return {"result": True}


# Module-level helpers used by wrappers and other services

def _get_auth_service():
    try:
        config = Configuration(AutoConfig())
        account_repo = AccountRepositoryImpl()
        return AuthServiceImpl(config, account_repo)
    except Exception:
        class FallbackConfig:
            token_lifetime = 3600
        account_repo = AccountRepositoryImpl()
        return AuthServiceImpl(FallbackConfig(), account_repo)


def verify_token(token) -> bool:
    return _get_auth_service().verify_token(token)


def getAccountByToken(token) -> Account:
    return _get_auth_service().getAccountByToken(token)
