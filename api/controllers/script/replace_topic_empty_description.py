from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict

def replace_topic_empty_description(request):
    topics = Topic.objects.all()
    for topic in topics:
        if len(topic.description) == 0:
            topic.description = f'[{{"id": "1","type": ELEMENT_PARAGRAPH,"children": [{{ "text": "" }}]}}]'
            topic.save()
        elif topic.description[0] != '[':
            topic.description = f'[{{"id": "1","type": ELEMENT_PARAGRAPH,"children": [{{ "text": "{topic.description}" }}]}}]'
            topic.save()
    return Response({'message': 'Success!'},status=status.HTTP_201_CREATED)