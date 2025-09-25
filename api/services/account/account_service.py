from api.repositories.account_repository import AccountRepository
from api.utility import passwordEncryption
from api.models import *
from api.services.account.serializers import *
from django.db.models import Q
from api.errors.common import *
from abc import ABC, abstractmethod

class AccountService(ABC):

    @abstractmethod
    def create_account(self, request):
        pass
    
    @abstractmethod
    def get_account(self, account_id: str):
        pass
    
    @abstractmethod
    def get_all_accounts(self, request):
        pass

class AccountServiceImpl(AccountService):

    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    def create_account(self, request):
        body = {
            **request.data,
            'password': passwordEncryption(request.data['password'])
        }
        try:
            account = self.account_repo.create(body)
        except Exception as e:
            raise InternalServerError(e)
        serialize = AccountSerializer(account)
        return serialize.data

    def get_account(self, account_id: str):
        try:
            account = self.account_repo.get(account_id)
            serialize = AccountSerializer(account)
            return serialize.data
        except Account.DoesNotExist:
            raise ItemNotFoundError("Account")

    def get_all_accounts(self, request):
        # get search query
        search = request.GET.get('search', '')
        
        accounts = self.account_repo.list(search)
        
        serialize = AccountSecureSerializer(accounts, many=True)
        return {
            "accounts": serialize.data
        }
    

    # TODO: Move this to submission service
    # def get_daily_submission(account_id:str):
    #     submissions = Submission.objects.filter(account_id=account_id)
    #     serializes = SubmissionSerializer(submissions,many=True)

    #     submission_by_date = {}

    #     for submission in serializes.data:
    #         [date,] = submission['date'].split("T")
    #         if date in submission_by_date:
    #             submission_by_date[date]["submissions"].append(submission)
    #             submission_by_date[date]["count"] += 1
    #         else:
    #             submission_by_date[date] = {"count":1, "submissions": [ submission ]}
        
    #     return Response({"submissions_by_date": submission_by_date})