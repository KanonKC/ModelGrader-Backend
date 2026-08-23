from abc import ABC, abstractmethod
from django.db.models import Q
from django.utils import timezone
from api.models import Collection, CollectionProblem, TopicCollection
from typing import List

class CollectionRepository:
    def __init__(self):
        pass

    def create(self, r):
        collection = Collection.objects.create(**r)
        collection.save()
        return collection

    def get(self, collection_id: str):
        return Collection.objects.get(collection_id=collection_id)

    def list(self, q: str = '', f: dict = {}):
        if q:
            collections = Collection.objects.filter(Q(name__icontains=q) | Q(description__icontains=q))
        else:
            collections = Collection.objects.all()

        if 'creator_id' in f and f['creator_id']:
            collections = collections.filter(creator__account_id=f['creator_id'])

        return collections

    def update(self, collection_id: str, r):
        collection = self.get(collection_id)
        collection.name = r.get('name', collection.name)
        collection.description = r.get('description', collection.description)
        collection.is_active = r.get('is_active', collection.is_active)
        collection.is_private = r.get('is_private', collection.is_private)
        collection.save()
        return collection

    def delete(self, collection_id: str):
        self.get(collection_id).delete()

    def get_problems(self, collection_id: str):
        return CollectionProblem.objects.filter(collection_id=collection_id).select_related('problem', 'problem__creator').order_by('order')
    
    def get_problems_by_collections(self, collection_ids):
        return CollectionProblem.objects.filter(collection__in=collection_ids).select_related('problem').order_by('order')
    
    def get_by_creator(self, account_id: str, order_by: str = '-updated_date'):
        return Collection.objects.filter(creator_id=account_id).order_by(order_by)
    
    def update_with_timestamp(self, collection_id: str, data: dict):
        collection = self.get(collection_id)
        for key, value in data.items():
            if hasattr(collection, key):
                setattr(collection, key, value)
        collection.updated_date = timezone.now()
        collection.save()
        return collection
    
    def delete_problems(self, collection_id: str):
        CollectionProblem.objects.filter(collection_id=collection_id).delete()
    
    def bulk_create_problems(self, collection_problems: List[CollectionProblem]):
        CollectionProblem.objects.bulk_create(collection_problems)
    
    def find_existing_problem(self, problem_id: str, collection_id: str):
        return CollectionProblem.objects.filter(problem_id=problem_id, collection_id=collection_id)
    
    def delete_many_problems(self, collection_id: str, problem_ids: List[str]):
        CollectionProblem.objects.filter(collection_id=collection_id, problem_id__in=problem_ids).delete()
    
    def get_accessible_problems_for_collection(self, collection_id: str, group_ids: List[str]):
        from django.db.models import Q
        from api.models import ProblemGroupPermission
        
        accessible_problems = ProblemGroupPermission.objects.filter(
            Q(group__in=group_ids) & (Q(permission_view_problems=True) | Q(permission_manage_problems=True))
        ).values_list("problem", flat=True)
        
        return CollectionProblem.objects.filter(
            collection_id=collection_id,
            problem__in=accessible_problems
        )
    
    def get_manageable_by_account(self, group_ids: List[str], order_by: str = '-updated_date'):
        """Get collections manageable by account through group permissions"""
        return Collection.objects.filter(
            collectiongrouppermission__permission_manage_collections=True,
            collectiongrouppermission__group__in=group_ids
        ).order_by(order_by)
    
    def get_accessible_collections(self, topic_id: str, group_ids: List[str]):
        """Get accessible collections for a topic based on group permissions"""
        from api.models import CollectionGroupPermission
        
        accessible_collections = CollectionGroupPermission.objects.filter(
            Q(group__in=group_ids) & (Q(permission_view_collections=True) | Q(permission_manage_collections=True))
        ).values_list("collection", flat=True)
        
        return TopicCollection.objects.filter(
            topic_id=topic_id,
            collection__in=accessible_collections
        )
    