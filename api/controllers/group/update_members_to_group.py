from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_members_to_group(group:Group,request):
    GroupMember.objects.filter(group=group).delete()

    group_members = []
    for accountId in request.data['account_ids']:
        account = Account.objects.get(account_id=accountId)
        group_members.append(GroupMember(
            group=group,
            account=account
        ))

    GroupMember.objects.bulk_create(group_members)
    group.members = group_members

    serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(group)
    return Response(serialize.data,status=status.HTTP_200_OK)