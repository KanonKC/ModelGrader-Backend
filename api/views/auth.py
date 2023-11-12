import re
from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict
from uuid import uuid4
from time import time
from decouple import config

TOKEN_LIFETIME = int(config('TOKEN_LIFETIME_SECOND')) # (Second)

@api_view([POST])
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
            return Response({'detail':"Incorrect password!"},status=status.HTTP_406_NOT_ACCEPTABLE)
    except Account.DoesNotExist:
        return Response({'detail':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)

@api_view([POST])
def logout(request):
    try:
        account = Account.objects.get(account_id=request.data['account_id'])
        if account.token == request.data['token']:
            account.token = None
            account.save()
            return Response(model_to_dict(account),status=status.HTTP_200_OK)
        else:
            return Response({'detail':"Invalid token!"},status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'detail':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)

@api_view([PUT])
def get_authorization(request):
    try:
        account = Account.objects.get(account_id=request.data['account_id'])
        account_dict = model_to_dict(account)
        if account_dict['token_expire'] >= time() and account_dict['token'] == request.data['token']:
            return Response({'result':True,'is_admin':account.is_admin},status=status.HTTP_200_OK)
        return Response({'result':False,'is_admin':False},status=status.HTTP_200_OK)
    except Account.DoesNotExist:
        return Response({'result':False,'is_admin':False},status=status.HTTP_200_OK)
        # return Response({'detail':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)

# @api_view([GET])
# def get_token(request):
#     try:
#         account = Account.objects.get(username=request.data['username'])
#         account_dict = model_to_dict(account)

#         if account_dict['token_expire'] < time():
#             return Response({'detail':"Login timeout!"},status=status.HTTP_200_OK)
#         elif account_dict['token'] == request.data['token']

#         if passwordEncryption(request.data['password']) == account_dict['password']:
#             account.token = uuid4().hex
#             account.token_expire = int(time()+60)
#             account.save()
#             return Response(model_to_dict(account),status=status.HTTP_202_ACCEPTED)
#         else:
#             return Response({'detail':"Incorrect password!"},status=status.HTTP_200_OK)
#     except Account.DoesNotExist:
#         return Response({'detail':"User doesn't exists!"},status=status.HTTP_404_NOT_FOUND)