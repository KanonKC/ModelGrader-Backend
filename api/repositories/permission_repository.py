from django.db.models import Q
from api.models import ProblemGroupPermission, CollectionGroupPermission, TopicGroupPermission, CollectionProblem, ProblemGroupPermission
from typing import List


class PermissionRepository:
    def __init__(self):
        pass

    def get_problem_permissions(self, problem_id: str):
        return ProblemGroupPermission.objects.filter(problem_id=problem_id)

    def get_problem_permissions_for_problems(self, problem_ids: List[str]):
        from api.utility import group_by
        permissions = ProblemGroupPermission.objects.filter(problem_id__in=problem_ids).select_related('group')
        return group_by(permissions, lambda p: p.problem_id)

    def get_collection_permissions(self, collection_id: str):
        return CollectionGroupPermission.objects.filter(collection_id=collection_id)

    def get_collection_permissions_for_collections(self, collection_ids: List[str]):
        from api.utility import group_by
        permissions = CollectionGroupPermission.objects.filter(collection_id__in=collection_ids).select_related('group')
        return group_by(permissions, lambda p: p.collection_id)

    def get_topic_permissions(self, topic_id: str):
        return TopicGroupPermission.objects.filter(topic_id=topic_id)
    
    def delete_collection_permissions(self, collection_id: str):
        CollectionGroupPermission.objects.filter(collection_id=collection_id).delete()
    
    def bulk_create_collection_permissions(self, permissions: List[CollectionGroupPermission]):
        return CollectionGroupPermission.objects.bulk_create(permissions)
    
    def delete_topic_permissions(self, topic_id: str):
        TopicGroupPermission.objects.filter(topic_id=topic_id).delete()
    
    def bulk_create_topic_permissions(self, permissions: List[TopicGroupPermission]):
        TopicGroupPermission.objects.bulk_create(permissions)
    
    def delete_problem_permissions(self, problem_id: str):
        ProblemGroupPermission.objects.filter(problem_id=problem_id).delete()
    
    def bulk_create_problem_permissions(self, permissions: List[ProblemGroupPermission]):
        ProblemGroupPermission.objects.bulk_create(permissions)
    
    def get_accessible_collections(self, ids: List[str]):
        """Get collections accessible by group IDs"""
        return CollectionGroupPermission.objects.filter(
            Q(group__in=ids) & (Q(permission_view_collections=True) | Q(permission_manage_collections=True))
        ).values_list("collection", flat=True)
    
    def get_accessible_problems_for_collections(self, topic_collections, ids: List[str]):
        """Get accessible problems for collections based on group permissions"""
        from api.utility import group_by

        accessible_problem_ids = ProblemGroupPermission.objects.filter(
            Q(group__in=ids) & (Q(permission_view_problems=True) | Q(permission_manage_problems=True))
        ).values_list("problem", flat=True)

        collection_ids = [tp.collection_id for tp in topic_collections]
        collection_problems = CollectionProblem.objects.select_related('problem').filter(
            collection_id__in=collection_ids,
            problem_id__in=accessible_problem_ids
        )
        problems_by_collection = group_by(collection_problems, lambda cp: cp.collection_id)

        for tp in topic_collections:
            tp.collection.problems = problems_by_collection.get(tp.collection_id, [])
        return topic_collections