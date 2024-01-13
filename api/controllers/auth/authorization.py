from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from time import time

def authorization(request):
    try:
        account = Account.objects.get(account_id=request.data['account_id'])
        account_dict = model_to_dict(account)
        if account_dict['token_expire'] >= time() and account_dict['token'] == request.data['token']:
            return Response({'result':True},status=status.HTTP_200_OK)
        return Response({'result':False},status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'result':False},status=status.HTTP_200_OK)
        # return Response({'message':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)
