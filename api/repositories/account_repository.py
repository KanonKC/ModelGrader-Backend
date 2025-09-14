from django.db.models import Q
from api.models import Account
from abc import ABC, abstractmethod

class AccountRepository(ABC):
    @abstractmethod
    def create(self, r):
        pass
    
    @abstractmethod
    def get(self, id: str):
        pass
    
    @abstractmethod
    def list(self, q):
        pass

class AccountRepositoryImpl:
    def __init__(self):
        pass
    
    def create(self, r):
        return Account.objects.create(**r)

    def get(self, id: str):
        return Account.objects.get(account_id=id)

    def list(self, q):
        accounts = Account.objects.all()
        if q:
            accounts = accounts.filter(
                Q(username__icontains=q) | Q(account_id__icontains=q) | Q(email__icontains=q)
            ).distinct()
        return accounts

class AccountRepositoryMock(AccountRepository):
    def __init__(self):
        pass
    
    def create(self, r):
        return {"message": "Account created"}
    
    def get(self, id: str):
        return {"message": "Account"}
    
    def list(self, q):
        return {"message": "Accounts"}