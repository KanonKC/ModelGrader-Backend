from django.db.models import Q
from api.models import Account
from abc import ABC, abstractmethod

class AccountRepository(ABC):
    @abstractmethod
    def create(self, r) -> Account:
        pass
    
    @abstractmethod
    def get(self, id: str) -> Account:
        pass
    
    @abstractmethod
    def list(self, q: str) -> list[Account]:
        pass

    @abstractmethod
    def get_by_token(self, token: str) -> Account:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> Account:
        pass

class AccountRepositoryImpl:
    def __init__(self):
        pass
    
    def create(self, r) -> Account:
        return Account.objects.create(**r)

    def get(self, id: str) -> Account:
        return Account.objects.get(account_id=id)

    def list(self, q) -> list[Account]:
        accounts = Account.objects.all()
        if q:
            accounts = accounts.filter(
                Q(username__icontains=q) | Q(account_id__icontains=q) | Q(email__icontains=q)
            ).distinct()
        return accounts

    def get_by_token(self, token: str) -> Account:
        return Account.objects.get(token=token)

    def get_by_username(self, username: str) -> Account:
        return Account.objects.get(username=username)
