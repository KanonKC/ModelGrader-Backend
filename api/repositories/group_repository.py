from django.db.models import Q
from django.utils import timezone
from api.models import GroupMember, Group, TopicCollection, CollectionGroupPermission
from api.utility import group_by
from typing import List


class GroupRepository:
    def __init__(self):
        pass

    def get_ids_by_account(self, account_id: str) -> List[str]:
        """Common method to get group IDs for an account - used by other repositories"""
        return GroupMember.objects.filter(account_id=account_id).values_list("group", flat=True)
    
    def list_by_account_id(self, account_id: str) -> List[str]:
        """Alias for backward compatibility"""
        return self.get_ids_by_account(account_id)
    
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
    
    def create(self, group_data: dict):
        group = Group(**group_data)
        group.save()
        return group
    
    def delete(self, group_id: str):
        group = self.get(group_id)
        group.delete()
        return None
    
    def get_by_creator(self, account_id: str, order_by: str = '-updated_date'):
        return Group.objects.filter(creator_id=account_id).order_by(order_by)
    
    def get_members(self, group_id: str):
        return GroupMember.objects.filter(group_id=group_id).select_related('account')

    def get_members_for_groups(self, group_ids: List[str]):
        members = GroupMember.objects.filter(group_id__in=group_ids).select_related('account')
        return group_by(members, lambda member: member.group_id)

    def update(self, group_id: str, group_data: dict):
        group = self.get(group_id)
        for key, value in group_data.items():
            setattr(group, key, value)
        group.updated_date = timezone.now()
        group.save()
        return group
    
    def bulk_create_members(self, members: List[GroupMember]):
        return GroupMember.objects.bulk_create(members)
    
    def delete_members(self, group_id: str):
        GroupMember.objects.filter(group_id=group_id).delete()
    
    def get_accessible_by_account(self, account_id: str):
        """Get accessible topics by account through group permissions"""
        groups = [gm.group for gm in GroupMember.objects.filter(account_id=account_id)]
        from api.models import TopicGroupPermission
        accessed_topics = TopicGroupPermission.objects.filter(
            Q(group__in=groups) & (Q(permission_view_topics=True) | Q(permission_manage_topics=True))
        )
        return accessed_topics
    
    def get_accessible_collections_with_access(self, topic_id: str, account_id: str):
        """Get accessible collections for a topic based on account's group permissions"""
        group_ids = GroupMember.objects.filter(account_id=account_id).values_list("group", flat=True)
        
        topic_collections = TopicCollection.objects.filter(
            topic_id=topic_id,
            collection__in=CollectionGroupPermission.objects.filter(
                Q(group__in=group_ids) & (Q(permission_view_collections=True) | Q(permission_manage_collections=True))
            ).values_list("collection", flat=True)
        )
        return topic_collections