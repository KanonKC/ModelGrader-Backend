from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def populated_collections(topics:Topic):
    topicCollections = TopicCollection.objects.filter(topic__in=topics)
    populated_topics = []
    for topic in topics:
        topic.collections = topicCollections.filter(topic=topic)
        populated_topics.append(topic)
    return populated_topics

def get_all_topics_by_account(account:Account,request):
    personalTopics = Topic.objects.filter(creator=account).order_by('-updated_date')
    populatedPersonalTopics = populated_collections(personalTopics)
    personalSerialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populatedPersonalTopics,many=True)

    # print(GroupMember.objects.all().values_list("group",flat=True))
    manageableTopics = Topic.objects.filter(topicgrouppermission__permission_manage_topics=True,topicgrouppermission__group__in=GroupMember.objects.all().values_list("group",flat=True)).order_by('-updated_date')
    populatedmanageableTopics = populated_collections(manageableTopics)
    manageableSerialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populatedmanageableTopics,many=True)

    return Response({
        'topics': personalSerialize.data,
        'manageable_topics': manageableSerialize.data
    },status=status.HTTP_200_OK)