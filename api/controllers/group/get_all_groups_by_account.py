from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_groups_by_account(account:Account,request):

    groups = Group.objects.filter(creator=account).order_by('-updated_date')

    populate_members = request.GET.get('populate_members',False)

    if populate_members:
        for group in groups:
            group.members = GroupMember.objects.filter(group=group)
        serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(groups,many=True)
    else:
        serialize = GroupSerializer(groups,many=True)
    return Response({"groups":serialize.data},status=status.HTTP_200_OK)
