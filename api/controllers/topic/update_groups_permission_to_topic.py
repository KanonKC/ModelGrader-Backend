from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_groups_permission_to_topic(topic:Topic,request):

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

    return Response(serialize.data,status=status.HTTP_202_ACCEPTED)