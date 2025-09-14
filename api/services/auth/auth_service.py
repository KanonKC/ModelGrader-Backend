from django.forms.models import model_to_dict
from time import time

from api.errors.auth import IncorrectPasswordError
from ..models import Account
from ..errors.common import *
from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ..constant import GET, POST, PUT, DELETE
from rest_framework import status
from ..serializers import *
from decouple import config
from uuid import uuid4

TOKEN_LIFETIME = int(config('TOKEN_LIFETIME_SECOND'))  # (Second)

def verify_token(token):
    """
    Check if user has valid token and not expired
    Return: True/False
    """
    try:
        account = Account.objects.get(token=token)
        account_dict = model_to_dict(account)
        if account_dict['token_expire'] >= time():
            return True
        else:
            return False
    except Account.DoesNotExist:
        return False
    
def getAccountByToken(token):
    """
    Get account from token
    Return: account object
    """
    try:
        account = Account.objects.get(token=token)
        if account.token_expire < time():
            raise InvalidTokenError()
        return account
    except Account.DoesNotExist:
        raise InvalidTokenError()
    except Exception as e:
        raise e

def login(request):
    try:
        account = Account.objects.get(username=request.data['username'])
        account_dict = model_to_dict(account)
        if passwordEncryption(request.data['password']) == account_dict['password']:
            account.token = uuid4().hex
            account.token_expire = int(time() + TOKEN_LIFETIME)
            account.save()
            return model_to_dict(account)
        else:
            raise IncorrectPasswordError()
    except Account.DoesNotExist:
        raise ItemNotFoundError("User")

def authorization(request):
    try:
        account = Account.objects.get(account_id=request.data['account_id'])
        account_dict = model_to_dict(account)
        if account_dict['token_expire'] >= time() and account_dict['token'] == request.data['token']:
            return {'result': True}
        return {'result': False}
    except Account.DoesNotExist:
        return {'result': False}

def logout(request):
    try:
        account = Account.objects.get(account_id=request.data['account_id'])
        if account.token == request.data['token']:
            account.token = None
            account.save()
            return Response(model_to_dict(account), status=status.HTTP_200_OK)
        else:
            raise InvalidTokenError()
    except Account.DoesNotExist:
        raise ItemNotFoundError("User")