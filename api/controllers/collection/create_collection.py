from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def create_collection(account_id:str,request):
    
    request.data['creator'] = account_id
    serialize = CollectionSerializer(data=request.data)

    if serialize.is_valid():
        serialize.save()
        return Response(serialize.data,status=status.HTTP_201_CREATED)
    else:
        return Response(serialize.errors,status=status.HTTP_400_BAD_REQUEST)
