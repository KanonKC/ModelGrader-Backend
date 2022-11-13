from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import grading, checker
from ..constant import GET,POST,PUT,DELETE
from ..models import Account, Problem,Testcase
from rest_framework import status
from django.forms.models import model_to_dict

@api_view([POST])
def create_account(request):
    request.data['password'] = passwordEncryption(request.data['password'])
    try:
        account = Account.objects.create(**request.data)
    except Exception as e:
        return Response({'message':str(e)},status=status.HTTP_400_BAD_REQUEST)
    return Response({'message':'Registration Completed','account':model_to_dict(account)},status=status.HTTP_201_CREATED)

@api_view([GET])
def get_account(request,account_id):
    try:
        account = Account.objects.get(account_id=account_id)
        return Response(model_to_dict(account),status=status.HTTP_200_OK)
    except:
        return Response({'message':'Account not found!'},status=status.HTTP_404_NOT_FOUND)
