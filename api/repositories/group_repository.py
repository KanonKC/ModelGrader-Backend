from api.models import GroupMember, Group, Collection
from typing import List


class GroupRepository:
    def __init__(self):
        pass

    def list_by_account_id(self, account_id: str) -> List[str]:
        return GroupMember.objects.filter(account_id=account_id).values_list("group", flat=True)
    
    def get(self, group_id: str):
        return Group.objects.get(group_id=group_id)
    
    def get_manageable_collections(self, account_id: str, order_by: str = '-updated_date'):
        return Collection.objects.filter(
            collectiongrouppermission__permission_manage_collections=True,
            collectiongrouppermission__group__in=GroupMember.objects.filter(account_id=account_id).values_list("group", flat=True)
        ).order_by(order_by)