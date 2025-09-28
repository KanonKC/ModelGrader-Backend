from ...models import *
from .serializers import *
from ...errors.common import *
from api.repositories.group_repository import GroupRepository
from api.repositories.account_repository import AccountRepository

class GroupService:

    def __init__(self, group_repo: GroupRepository, account_repo: AccountRepository):
        self.group_repo = group_repo
        self.account_repo = account_repo

    def create_group(self, account_id: str, request):
        account = self.account_repo.get(account_id)
        group_data = {
            'creator_id': account.account_id,
            **request.data
        }
        
        group = self.group_repo.create(group_data)
        serialize = GroupSerializer(group)
        return serialize.data

    def delete_group(self, group_id: str):
        self.group_repo.delete(group_id)
        return None

    def get_group(self, group_id: str, request):
        group = self.group_repo.get(group_id)
        populate_members = request.GET.get('populate_members', False)

        if populate_members:
            group.members = self.group_repo.get_members(group_id)
            serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(group)
        else:
            serialize = GroupSerializer(group)
        
        return serialize.data

    def get_all_groups_by_account(self, account_id: str, request):
        account = self.account_repo.get(account_id)

        # Get request headers
        headers = request.headers

        groups = self.group_repo.get_by_creator(account_id)

        populate_members = request.GET.get('populate_members', False)

        if populate_members:
            for group in groups:
                group.members = self.group_repo.get_members(group.group_id)
            serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(groups, many=True)
        else:
            serialize = GroupSerializer(groups, many=True)
        
        return {"groups": serialize.data}

    def update_group(self, group_id: str, request):
        group = self.group_repo.update(group_id, request.data)
        serializer = GroupSerializer(group)
        return serializer.data

    def add_members_to_group(self, group_id: str, request):
        group = self.group_repo.get(group_id)
        group_members = []
        for accountId in request.data['account_ids']:
            account = self.account_repo.get(accountId)
            group_members.append(GroupMember(
                group_id=group_id,
                account_id=accountId
            ))

        self.group_repo.bulk_create_members(group_members)
        group.members = group_members

        serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(group)
        return serialize.data

    def update_members_to_group(self, group_id: str, request):
        group = self.group_repo.get(group_id)
        self.group_repo.delete_members(group_id)

        group_members = []
        for accountId in request.data['account_ids']:
            account = self.account_repo.get(accountId)
            group_members.append(GroupMember(
                group_id=group_id,
                account_id=accountId
            ))

        self.group_repo.bulk_create_members(group_members)
        group.members = group_members

        serialize = GroupPopulateGroupMemberPopulateAccountSecureSerializer(group)
        return serialize.data
