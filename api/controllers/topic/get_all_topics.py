from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def get_all_topics(request):
    topics = Topic.objects.all()

    account_id = request.query_params.get('account_id',0)

    if account_id:
        topics = topics.filter(creator_id=account_id)

    serializer = TopicSerializer(topics,many=True)

    return Response({
        'topics': serializer.data
    },status=status.HTTP_200_OK)