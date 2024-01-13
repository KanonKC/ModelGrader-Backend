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

def logout(request):
    try:
        account = Account.objects.get(account_id=request.data['account_id'])
        if account.token == request.data['token']:
            account.token = None
            account.save()
            return Response(model_to_dict(account),status=status.HTTP_200_OK)
        else:
            return Response({'message':"Invalid token!"},status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'message':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)
