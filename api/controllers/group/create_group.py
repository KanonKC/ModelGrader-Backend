from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def create_group(account:Account,request):

    group = Group(
        creator=account,
        name=request.data['name'],
        description=request.data['description'] if 'description' in request.data else None,
        color=request.data['color'] if 'color' in request.data else None,
    )

    group.save()
    serialize = GroupSerializer(group)

    return Response(serialize.data,status=status.HTTP_201_CREATED)