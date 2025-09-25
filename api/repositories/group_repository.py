from django.db.models import Q
from api.models import GroupMember, Group
from typing import List


class GroupRepository:
    def __init__(self):
        pass

    def get_group_ids_by_account(self, account_id: str) -> List[str]:
        """Common method to get group IDs for an account - used by other repositories"""
        return GroupMember.objects.filter(account_id=account_id).values_list("group", flat=True)
    
    def list_by_account_id(self, account_id: str) -> List[str]:
        """Alias for backward compatibility"""
        return self.get_group_ids_by_account(account_id)
    
    def get(self, group_id: str):
        return Group.objects.get(group_id=group_id)
    
    def get_members(self, account_id: str):
        return [gm.group for gm in GroupMember.objects.filter(account_id=account_id)]
    
    def get_accessible_topics(self, account_id: str):
        from api.models import TopicGroupPermission
        groups = self.get_members(account_id)
        return TopicGroupPermission.objects.filter(
            Q(group__in=groups) & (Q(permission_view_topics=True) | Q(permission_manage_topics=True))
        )