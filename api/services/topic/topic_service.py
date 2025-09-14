from django.utils import timezone
from django.db.models import Q
from ...models import *
from .serializers import *
from ...errors.common import *

def create_topic(account_id: str, request):
    request.data._mutable = True
    request.data['creator'] = account_id
    serializer = TopicSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        return serializer.data
    else:
        raise BadRequestError(str(serializer.errors))

def delete_topic(topic: Topic):
    topic.delete()
    return None

def get_topic(topic: Topic):
    topic.group_permissions = TopicGroupPermission.objects.filter(topic=topic)
    topic.collections = TopicCollection.objects.filter(topic=topic).order_by('order')

    for tp in topic.collections:
        tp.collection.problems = CollectionProblem.objects.filter(collection=tp.collection)
        tp.collection.group_permissions = CollectionGroupPermission.objects.filter(collection=tp.collection)

    serialize = TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemsPopulateProblemAndCollectionGroupPermissionsPopulateGroupAndTopicGroupPermissionPopulateGroupSerializer(topic)
    
    return serialize.data

def get_all_topics(request):
    topics = Topic.objects.all()

    account_id = request.query_params.get('account_id', 0)

    if account_id:
        topics = topics.filter(creator_id=account_id)

    serializer = TopicSerializer(topics, many=True)

    return {
        'topics': serializer.data
    }

def update_topic(topic: Topic, request):    
    topic_ser = TopicSerializer(topic, data=request.data, partial=True)
    if topic_ser.is_valid():
        topic_ser.save()
        return topic_ser.data
    else:
        raise BadRequestError(str(topic_ser.errors))

def populated_collections(topics: Topic):
    topicCollections = TopicCollection.objects.filter(topic__in=topics)
    populated_topics = []
    for topic in topics:
        topic.collections = topicCollections.filter(topic=topic)
        populated_topics.append(topic)
    return populated_topics

def get_all_topics_by_account(account: Account, request):
    personalTopics = Topic.objects.filter(creator=account).order_by('-updated_date')
    populatedPersonalTopics = populated_collections(personalTopics)
    personalSerialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populatedPersonalTopics, many=True)

    manageableTopics = Topic.objects.filter(
        topicgrouppermission__permission_manage_topics=True,
        topicgrouppermission__group__in=GroupMember.objects.filter(account=account).values_list("group", flat=True)
    ).order_by('-updated_date')
    populatedmanageableTopics = populated_collections(manageableTopics)
    manageableSerialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populatedmanageableTopics, many=True)

    return {
        'topics': personalSerialize.data,
        'manageable_topics': manageableSerialize.data
    }

def get_all_accessed_topics_by_account(account: Account):
    groups = [gm.group for gm in GroupMember.objects.filter(account=account)]
    accessedTopics = TopicGroupPermission.objects.filter(
        Q(group__in=groups) & (Q(permission_view_topics=True) | Q(permission_manage_topics=True))
    )
    
    topics = []
    for at in accessedTopics:
        if at.topic not in topics:
            topics.append(at.topic)

    serialize = TopicSerializer(topics, many=True)

    return {'topics': serialize.data}

def get_topic_public(topic_id: str, request):
    account_id = request.query_params.get('account_id', None)

    topic = Topic.objects.get(topic_id=topic_id)
    account = Account.objects.get(account_id=account_id)

    topicCollections = TopicCollection.objects.filter(
        topic=topic,
        collection__in=
            CollectionGroupPermission.objects.filter(
                Q(group__in=GroupMember.objects.filter(account=account).values_list("group", flat=True)) &
                (
                    Q(permission_view_collections=True) | Q(permission_manage_collections=True)
                )
            ).values_list("collection", flat=True))

    for tp in topicCollections:
        collectionProblems = CollectionProblem.objects.filter(
            collection=tp.collection,
            problem__in=ProblemGroupPermission.objects.filter(
                Q(group__in=GroupMember.objects.filter(account=account).values_list("group", flat=True)) &
                (Q(permission_view_problems=True) |
                Q(permission_manage_problems=True))
            ).values_list("problem", flat=True))

        for cp in collectionProblems:
            try:
                best_submission = BestSubmission.objects.get(problem=cp.problem, account=account, topic=topic)
                best_submission = best_submission.submission
                best_submission.runtime_output = SubmissionTestcase.objects.filter(submission=best_submission)
            except:
                best_submission = None
            cp.problem.best_submission = best_submission

        tp.collection.problems = collectionProblems

    topic.collections = topicCollections

    serialize = TopicPopulateTopicCollectionPopulateCollectionPopulateCollectionProblemPopulateProblemPopulateAccountAndSubmissionPopulateSubmissionTestcasesSecureSerializer(topic)

    return serialize.data

def update_groups_permission_to_topic(topic: Topic, request):
    TopicGroupPermission.objects.filter(topic=topic).delete()
    
    topic_group_permissions = []
    for group_request in request.data['groups']:
        print(group_request)
        group = Group.objects.get(group_id=group_request['group_id'])
        topic_group_permissions.append(
            TopicGroupPermission(
                topic=topic,
                group=group,
                **group_request
        ))

    TopicGroupPermission.objects.bulk_create(topic_group_permissions)

    topic.group_permissions = topic_group_permissions
    serialize = TopicPopulateTopicGroupPermissionsSerializer(topic)

    return serialize.data

def update_collections_to_topic(topic: Topic, request):
    TopicCollection.objects.filter(topic=topic).delete()

    topic_collections = []
    order = 0
    for collection_id in request.data['collection_ids']:
        collection = Collection.objects.get(collection_id=collection_id)
        topic_collection = TopicCollection(
            collection=collection,
            topic=topic,
            order=order
        )
        topic_collections.append(topic_collection)
        order += 1

    TopicCollection.objects.bulk_create(topic_collections)
    topic.updated_date = timezone.now()
    topic.save()

    collection_serialize = TopicCollectionPopulateCollectionSerializer(topic_collections, many=True)
    topic_serialize = TopicSerializer(topic)

    return {
        **topic_serialize.data,
        'collections': collection_serialize.data
    }

def add_collections_to_topic(topic_id: str, request):
    topic = Topic.objects.get(topic_id=topic_id)
    populated_collections = []
        
    index = 0
    for collection_id in request.data['collection_ids']:
        collection = Collection.objects.get(collection_id=collection_id)

        alreadyExist = TopicCollection.objects.filter(topic_id=topic.topic_id, collection_id=collection.collection_id)
        if alreadyExist:
            alreadyExist.delete()
            
        topicCollection = TopicCollection(
            topic=topic,
            collection=collection,
            order=index
        )
        topicCollection.save()
        index += 1
        tc_serialize = TopicCollectionSerializer(topicCollection)
        populated_collections.append(tc_serialize.data)
    
    return {
        **TopicSerializer(topic).data,
        "collections": populated_collections
    }

def remove_collections_from_topic(topic_id: str, request):
    TopicCollection.objects.filter(topic_id=topic_id, collection_id__in=request.data['collection_ids']).delete()
    return None
