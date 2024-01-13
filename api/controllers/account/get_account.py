from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_account(account_id:str):
    try:
        account = Account.objects.get(account_id=account_id)
        serialize = AccountSerializer(account)
        return Response(serialize.data,status=status.HTTP_200_OK)
    except:
        return Response({'message':'Account not found!'},status=status.HTTP_404_NOT_FOUND)
