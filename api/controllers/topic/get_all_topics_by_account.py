from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_topics_by_account(account_id:int,request):
    topics = Topic.objects.filter(creator_id=account_id)
    topicCollections = TopicCollection.objects.filter(topic__in=topics)

    populated_topics = []
    for topic in topics:
        topic.collections = topicCollections.filter(topic=topic)
        populated_topics.append(topic)

    serialize = TopicPopulateTopicCollectionPopulateCollectionSerializer(populated_topics,many=True)

    return Response({
        'topics': serialize.data
    },status=status.HTTP_200_OK)