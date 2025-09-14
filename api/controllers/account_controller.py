from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from api.wrappers.auth_wrapper import authentication_required
from ..constant import GET,POST,PUT,DELETE
from ..models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ..serializers import *
from ..controllers.account.create_account import *
from ..controllers.account.get_account import *
from ..controllers.account.get_all_accounts import *
from api.errors.common import InternalServerError
from api.errors.core.grader_exception import GraderException

@api_view([GET,POST])
def all_accounts_view(request):
    try:
        if request.method == GET:
            result = get_all_accounts(request)
        elif request.method == POST:
            result = create_account(request)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def one_creator_view(request,account_id):
    try:
        result = get_account(account_id)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([PUT])
@authentication_required
def change_password(request,account_id):
    try:
        result = change_password(account_id, request.data['password'])
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

@api_view([GET])
@authentication_required
def get_daily_submission(request,account_id:str):
    try:
        result = get_daily_submission(account_id)
        return Response(result, status=200)
    except GraderException as ge:
        return ge.django_response()
    except Exception as e:
        return InternalServerError(e).django_response()

