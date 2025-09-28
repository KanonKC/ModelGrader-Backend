from django.utils import timezone
from django.db.models import Q
from api.models import Topic, TopicCollection, Collection, BestSubmission, SubmissionTestcase
from typing import List

class TopicRepository:
    def __init__(self):
        pass

    def get(self, topic_id: str):
        return Topic.objects.get(topic_id=topic_id)
    
    def list(self, filters: dict = {}):
        topics = Topic.objects.all()
        if 'creator_id' in filters and filters['creator_id']:
            topics = topics.filter(creator_id=filters['creator_id'])
        return topics
    
    def get_by_creator(self, account_id: str):
        return Topic.objects.filter(creator_id=account_id).order_by('-updated_date')
    
    def get_collections(self, topic_id: str):
        return TopicCollection.objects.filter(topic_id=topic_id).order_by('order')
    
    def get_many_collections(self, topic_ids: List[str]):
        return TopicCollection.objects.filter(topic__in=topic_ids)
    
    def delete_collections(self, topic_id: str):
        TopicCollection.objects.filter(topic_id=topic_id).delete()
    
    def bulk_create_collections(self, topic_collections: List[TopicCollection]):
        TopicCollection.objects.bulk_create(topic_collections)
    
    def find_existing_collection(self, topic_id: str, collection_id: str):
        return TopicCollection.objects.filter(topic_id=topic_id, collection_id=collection_id)
    
    def delete_many_collections(self, topic_id: str, collection_ids: List[str]):
        TopicCollection.objects.filter(topic_id=topic_id, collection_id__in=collection_ids).delete()
    
    def update_with_timestamp(self, topic_id: str, data: dict = {}):
        topic = self.get(topic_id)
        for key, value in data.items():
            if hasattr(topic, key):
                setattr(topic, key, value)
        topic.updated_date = timezone.now()
        topic.save()
        return topic
    
    def delete(self, topic_id: str):
        topic = self.get(topic_id)
        topic.delete()
    
    def get_manageable_by_ids(self, ids: List[str], order_by: str = '-updated_date'):
        """Get topics manageable by account through group permissions"""
        return Topic.objects.filter(
            topicgrouppermission__permission_manage_topics=True,
            topicgrouppermission__group__in=ids
        ).order_by(order_by)
    
    def create(self, topic_data: dict):
        topic = Topic(**topic_data)
        topic.save()
        return topic
    
    def update(self, topic_id: str, topic_data: dict):
        topic = self.get(topic_id)
        for key, value in topic_data.items():
            if hasattr(topic, key):
                setattr(topic, key, value)
        topic.save()
        return topic
    
    
    def get_best_submission_for_problem(self, problem_id: str, account_id: str, topic_id: str):
        try:
            best_submission = BestSubmission.objects.get(problem_id=problem_id, account_id=account_id, topic_id=topic_id)
            best_submission = best_submission.submission
            best_submission.runtime_output = SubmissionTestcase.objects.filter(submission_id=best_submission.submission_id)
            return best_submission
        except:
            return None
    
    
    def create_collection(self, topic_id: str, collection_id: str, order: int):
        topic_collection = TopicCollection(
            topic_id=topic_id,
            collection_id=collection_id,
            order=order
        )
        topic_collection.save()
        return topic_collection