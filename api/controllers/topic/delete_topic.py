from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def delete_topic(topic_id:int):
    topic = Topic.objects.get(topic_id=topic_id)
    topic.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
