from api.setup import account_service
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET,POST,PUT,DELETE
from ..serializers import *
from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException
import api.services.account.account_service as account_service
from abc import ABC, abstractmethod
from api.services.account.account_service import AccountService

class AccountController(ABC):
    @abstractmethod
    def all_accounts(self, request):
        pass
    
    @abstractmethod
    def one_creator(self, request, account_id):
        pass
    
    @abstractmethod
    def change_password(self, request, account_id):
        pass

class AccountControllerImpl(AccountController):
    def __init__(self, account_svc: AccountService):
        self.account_svc = account_svc

    @api_view([GET,POST])
    def all_accounts(self,request):
        try:
            if request.method == GET:
                result = self.account_svc.get_all_accounts(request)
            elif request.method == POST:
                result = self.account_svc.create_account(request)
            return Response(result, status=200)
        except GraderException as ge:
            return ge.django_response()
        except Exception as e:
            return InternalServerError(e).django_response()

    @api_view([GET])
    @authentication_required
    def one_creator(self,request,account_id):
        try:
            result = self.account_svc.get_account(account_id)
            return Response(result, status=200)
        except GraderException as ge:
            return ge.django_response()
        except Exception as e:
            return InternalServerError(e).django_response()

    @api_view([PUT])
    @authentication_required
    def change_password(self,request,account_id):
        try:
            result = self.account_svc.change_password(account_id, request.data['password'])
            return Response(result, status=200)
        except GraderException as ge:
            return ge.django_response()
        except Exception as e:
            return InternalServerError(e).django_response()

# @api_view([GET])
# @authentication_required
# def get_daily_submission(request,account_id:str):
#     try:
#         result = account_service.get_daily_submission(account_id)
#         return Response(result, status=200)
#     except GraderException as ge:
#         return ge.django_response()
#     except Exception as e:
#         return InternalServerError(e).django_response()

