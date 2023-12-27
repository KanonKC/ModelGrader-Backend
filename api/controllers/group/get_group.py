from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_group(group:Group,request):

    populate_members = request.GET.get('populate_members',False)

    if populate_members:
        group.members = GroupMember.objects.filter(group=group)
        serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(group)
    else:
        serialize = GroupSerializer(group)
    return Response(serialize.data,status=status.HTTP_200_OK)
