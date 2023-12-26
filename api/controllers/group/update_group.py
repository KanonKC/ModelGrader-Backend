from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_group(group:Group,request):
    
    group.name = request.data.get('name',group.name)
    group.description = request.data.get('description',group.description)
    group.color = request.data.get('color',group.color)

    group.save()
    serialize = GroupSerializer(group)

    return Response(serialize.data,status=status.HTTP_200_OK)