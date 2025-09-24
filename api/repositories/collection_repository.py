from abc import ABC, abstractmethod
from django.db.models import Q
from api.models import Collection, CollectionProblem

class CollectionRepository:
    def __init__(self):
        pass

    def create(self, r):
        collection = Collection.objects.create(**r)
        collection.save()
        return collection

    def get(self, collection_id: str):
        return Collection.objects.get(collection_id=collection_id)

    def list(self):
        return Collection.objects.all()

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
        return CollectionProblem.objects.filter(collection_id=collection_id).order_by('order')