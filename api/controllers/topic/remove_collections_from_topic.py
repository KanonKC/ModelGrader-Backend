from api.utility import passwordEncryption
from rest_framework.response import Response
from rest_framework.decorators import api_view
from api.sandbox.grader import PythonGrader
from ...constant import GET,POST,PUT,DELETE
from ...models import *
from rest_framework import status
from django.forms.models import model_to_dict
from ...serializers import *

def remove_collections_from_topic(topic_id:int,request):
    TopicCollection.objects.filter(topic_id=topic_id,collection_id__in=request.data['collection_ids']).delete()
    # collections = Collection.objects.filter(collection_id__in=request.data['collection_ids'])
    # problems = Problem.objects.filter(problem_id__in=request.data['problems_id'])
    # TopicProblem.objects.filter(topic_id=topic,problem_id__in=problems).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
