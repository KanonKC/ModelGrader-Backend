from django.utils import timezone
from django.db.models import Q
from ...models import *
from .serializers import *
from ...errors.common import *
from api.repositories.topic_repository import TopicRepository
from api.repositories.account_repository import AccountRepository
from api.repositories.permission_repository import PermissionRepository
from api.repositories.group_repository import GroupRepository
from api.repositories.collection_repository import CollectionRepository

class TopicService:

    def __init__(self, topic_repo: TopicRepository, account_repo: AccountRepository, 
                 permission_repo: PermissionRepository, group_repo: GroupRepository, 
                 collection_repo: CollectionRepository):
        self.topic_repo = topic_repo
        self.account_repo = account_repo
        self.permission_repo = permission_repo
        self.group_repo = group_repo
        self.collection_repo = collection_repo

    def create_topic(self, account_id: str, request):
        topic_data = {
            'creator_id': account_id,
            **request.data
        }
        
        topic = self.topic_repo.create(topic_data)
        serializer = TopicSerializer(topic)
        return serializer.data

    def delete_topic(self, topic_id: str):
        self.topic_repo.delete(topic_id)
        return None

    def get_topic(self, topic_id: str):
        topic = self.topic_repo.get(topic_id)
        topic.group_permissions = self.permission_repo.get_topic_permissions(topic_id)
        topic.collections = list(self.topic_repo.get_collections(topic_id))

        collection_ids = [tp.collection_id for tp in topic.collections]
        problems_by_collection = {}
        for cp in self.collection_repo.get_problems_by_collections(collection_ids):
            problems_by_collection.setdefault(cp.collection_id, []).append(cp)
        permissions_by_collection = self.permission_repo.get_collection_permissions_for_collections(collection_ids)

        for tp in topic.collections:
            tp.collection.problems = problems_by_collection.get(tp.collection_id, [])
            tp.collection.group_permissions = permissions_by_collection.get(tp.collection_id, [])

        serialize = TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupAndTopicGroupPermissionPopulateGroupSerializer(topic)
        
        return serialize.data

    def get_all_topics(self, request):
        account_id = request.query_params.get('account_id', 0)
        
        filters = {}
        if account_id:
            filters['creator_id'] = account_id

        topics = self.topic_repo.list(filters=filters)
        serializer = TopicSerializer(topics, many=True)

        return {
            'topics': serializer.data
        }

    def update_topic(self, topic_id: str, request):    
        topic = self.topic_repo.update(topic_id, request.data)
        serializer = TopicSerializer(topic)
        return serializer.data

    def populated_collections(self, topics: Topic):
        topic_ids = [topic.topic_id for topic in topics]
        topicCollections = self.topic_repo.get_many_collections(topic_ids)
        collections_by_topic = {}
        for tc in topicCollections:
            collections_by_topic.setdefault(tc.topic_id, []).append(tc)

        populated_topics = []
        for topic in topics:
            topic.collections = collections_by_topic.get(topic.topic_id, [])
            populated_topics.append(topic)
        return populated_topics

    def get_all_topics_by_account(self, account_id: str, request):
        account = self.account_repo.get(account_id)
        personalTopics = self.topic_repo.get_by_creator(account_id)
        populatedPersonalTopics = self.populated_collections(personalTopics)
        personalSerialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populatedPersonalTopics, many=True)

        group_ids = self.group_repo.get_ids_by_account(account_id)
        manageableTopics = self.topic_repo.get_manageable_by_ids(group_ids)
        populatedmanageableTopics = self.populated_collections(manageableTopics)
        manageableSerialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populatedmanageableTopics, many=True)

        return {
            'topics': personalSerialize.data,
            'manageable_topics': manageableSerialize.data
        }

    def get_all_accessed_topics_by_account(self, account_id: str):
        accessedTopics = self.group_repo.get_accessible_by_account(account_id)
        
        topics = []
        for at in accessedTopics:
            if at.topic not in topics:
                topics.append(at.topic)

        serialize = TopicSerializer(topics, many=True)

        return {'topics': serialize.data}

    def get_topic_public(self, topic_id: str, request):
        account_id = request.query_params.get('account_id', None)

        topic = self.topic_repo.get(topic_id)
        account = self.account_repo.get(account_id)

        topicCollections = self.group_repo.get_accessible_collections_with_access(topic_id, account_id)
        group_ids = self.group_repo.get_ids_by_account(account_id)
        topicCollections = list(self.permission_repo.get_accessible_problems_for_collections(topicCollections, group_ids))

        problem_ids = [
            cp.problem.problem_id
            for tp in topicCollections
            for cp in tp.collection.problems
        ]
        best_by_problem = self.topic_repo.get_best_submissions_for_problems(problem_ids, account_id, topic_id)

        for tp in topicCollections:
            for cp in tp.collection.problems:
                cp.problem.best_submission = best_by_problem.get(cp.problem.problem_id)

        topic.collections = topicCollections

        serialize = TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(topic)

        return serialize.data

    def update_groups_permission_to_topic(self, topic_id: str, request):
        topic = self.topic_repo.get(topic_id)
        self.permission_repo.delete_topic_permissions(topic_id)
        
        topic_group_permissions = []
        for group_request in request.data['groups']:
            group = self.group_repo.get(group_request['group_id'])
            # Remove group_id from group_request to avoid duplication
            group_request_copy = group_request.copy()
            group_request_copy.pop('group_id', None)
            topic_group_permissions.append(
                TopicGroupPermission(
                    topic_id=topic_id,
                    group_id=group.group_id,
                    **group_request_copy
            ))

        self.permission_repo.bulk_create_topic_permissions(topic_group_permissions)

        topic.group_permissions = topic_group_permissions
        serialize = TopicPopulateTopicGroupPermissionsSerializer(topic)

        return serialize.data

    def update_collections_to_topic(self, topic_id: str, request):
        topic = self.topic_repo.get(topic_id)
        self.topic_repo.delete_collections(topic_id)

        topic_collections = []
        order = 0
        for collection_id in request.data['collection_ids']:
            collection = self.collection_repo.get(collection_id)
            topic_collection = TopicCollection(
                collection_id=collection_id,
                topic_id=topic_id,
                order=order
            )
            topic_collections.append(topic_collection)
            order += 1

        self.topic_repo.bulk_create_collections(topic_collections)
        topic = self.topic_repo.update_with_timestamp(topic_id)

        collection_serialize = TopicCollectionPopulateCollectionSerializer(topic_collections, many=True)
        topic_serialize = TopicSerializer(topic)

        return {
            **topic_serialize.data,
            'collections': collection_serialize.data
        }

    def add_collections_to_topic(self, topic_id: str, request):
        topic = self.topic_repo.get(topic_id)
        populated_collections = []
            
        index = 0
        for collection_id in request.data['collection_ids']:
            collection = self.collection_repo.get(collection_id)

            alreadyExist = self.topic_repo.find_existing_collection(topic_id, collection_id)
            if alreadyExist:
                alreadyExist.delete()
                
            topicCollection = self.topic_repo.create_collection(topic_id, collection_id, index)
            index += 1
            tc_serialize = TopicCollectionSerializer(topicCollection)
            populated_collections.append(tc_serialize.data)
        
        return {
            **TopicSerializer(topic).data,
            "collections": populated_collections
        }

    def remove_collections_from_topic(self, topic_id: str, request):
        self.topic_repo.delete_many_collections(topic_id, request.data['collection_ids'])
        return None
