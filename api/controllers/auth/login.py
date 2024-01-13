from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from decouple import config
from uuid import uuid4
from time import time

TOKEN_LIFETIME = int(config('TOKEN_LIFETIME_SECOND')) # (Second)

def login(request):
    try:
        account = Account.objects.get(username=request.data['username'])
        account_dict = model_to_dict(account)

        if passwordEncryption(request.data['password']) == account_dict['password']:
            account.token = uuid4().hex
            account.token_expire = int(time()+TOKEN_LIFETIME)
            account.save()
            return Response(model_to_dict(account),status=status.HTTP_202_ACCEPTED)
        else:
            return Response({'message':"Incorrect password!"},status=status.HTTP_406_NOT_ACCEPTABLE)
    except Account.DoesNotExist:
        return Response({'message':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)
