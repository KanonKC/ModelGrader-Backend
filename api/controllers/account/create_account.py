from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def create_account(request):
    request.data['password'] = passwordEncryption(request.data['password'])
    try:
        account = Account.objects.create(**request.data)
    except Exception as e:
        return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)
    serialize = AccountSerializer(account)
    return Response(serialize.data,status=status.HTTP_201_CREATED)
