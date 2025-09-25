from api.models import ProblemGroupPermission, CollectionGroupPermission, TopicGroupPermission
from typing import List


class PermissionRepository:
    def __init__(self):
        pass

    def get_problem_group_permissions(self, problem_id: str):
        return ProblemGroupPermission.objects.filter(problem_id=problem_id)

    def get_collection_group_permissions(self, collection_id: str):
        return CollectionGroupPermission.objects.filter(collection_id=collection_id)

    def get_topic_group_permissions(self, topic_id: str):
        return TopicGroupPermission.objects.filter(topic_id=topic_id)
    
    def delete_collection_group_permissions(self, collection_id: str):
        CollectionGroupPermission.objects.filter(collection_id=collection_id).delete()
    
    def bulk_create_collection_group_permissions(self, permissions: List[CollectionGroupPermission]):
        return CollectionGroupPermission.objects.bulk_create(permissions)