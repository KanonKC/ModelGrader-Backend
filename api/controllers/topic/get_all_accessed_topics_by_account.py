from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *
from django.db.models import Q

def get_all_accessed_topics_by_account(account:Account):
    groups = [gm.group for gm in GroupMember.objects.filter(account=account)]
    accessedTopics = TopicGroupPermission.objects.filter(Q(group__in=groups) & (Q(permission_view_topics=True) | Q(permission_manage_topics=True)))
    
    topics = []
    for at in accessedTopics:
        if at.topic not in topics:
            topics.append(at.topic)

    serialize = TopicSerializer(topics,many=True)

    return Response({'topics':serialize.data},status=status.HTTP_200_OK)
