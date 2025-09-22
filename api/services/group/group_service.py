from django.utils import timezone
from ...models import *
from .serializers import *
from ...errors.common import *

class GroupService:

    def __init__(self):
        pass

    def create_group(self, account: Account, request):
        serialize = GroupSerializer(data={
            'creator': account.account_id,
            **request.data
        })

        if serialize.is_valid():
            serialize.save()
            return serialize.data
        else:
            raise BadRequestError(str(serialize.errors))

    def delete_group(self, group: Group, request):
        group.delete()
        return None

    def get_group(self, group: Group, request):
        populate_members = request.GET.get('populate_members', False)

        if populate_members:
            group.members = GroupMember.objects.filter(group=group)
            serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(group)
        else:
            serialize = GroupSerializer(group)
        
        return serialize.data

    def get_all_groups_by_account(self, account: Account, request):
        print("GET ALL")

        # Get request headers
        headers = request.headers

        groups = Group.objects.filter(creator=account).order_by('-updated_date')

        populate_members = request.GET.get('populate_members', False)

        if populate_members:
            for group in groups:
                group.members = GroupMember.objects.filter(group=group)
            serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(groups, many=True)
        else:
            serialize = GroupSerializer(groups, many=True)
        
        return {"groups": serialize.data}

    def update_group(self, group: Group, request):
        serializer = GroupSerializer(group, data={
            **request.data,
            'updated_date': timezone.now()
        }, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return serializer.data
        else:
            raise BadRequestError(str(serializer.errors))

    def add_members_to_group(self, group: Group, request):
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
        return serialize.data

    def update_members_to_group(self, group: Group, request):
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
        return serialize.data
