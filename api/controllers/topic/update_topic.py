from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def update_topic(topic:Topic,request):    
    topic_ser = TopicSerializer(topic,data=request.data,partial=True)
    if topic_ser.is_valid():
        topic_ser.save()
        return Response(topic_ser.data,status=status.HTTP_200_OK)
    print(topic_ser.errors)
    return Response(topic_ser.errors,status=status.HTTP_400_BAD_REQUEST)
    